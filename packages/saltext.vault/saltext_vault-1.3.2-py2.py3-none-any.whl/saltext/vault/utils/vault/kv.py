"""
Class wrappers for the Key/Value backend
"""

import logging

from saltext.vault.utils.vault.exceptions import VaultException
from saltext.vault.utils.vault.exceptions import VaultInvocationError
from saltext.vault.utils.vault.exceptions import VaultNotFoundError
from saltext.vault.utils.vault.exceptions import VaultPermissionDeniedError
from saltext.vault.utils.vault.exceptions import VaultUnsupportedOperationError

log = logging.getLogger(__name__)


class VaultKV:
    """
    Interface to Vault secret paths
    """

    def __init__(self, client, metadata_cache):
        self.client = client
        self.metadata_cache = metadata_cache

    def read(self, path, include_metadata=False, version=None):
        """
        Read secret data at path.

        include_metadata
            For KV v2, include metadata in the return value:
            ``{"data": {} ,"metadata": {}}``.
        """
        v2_info = self.is_v2(path)
        if v2_info["v2"]:
            path = v2_info["data"]
        elif version is not None:
            if version != 0:
                raise VaultInvocationError("Cannot request secret versions on KV v1")
            version = None
        if version is not None:
            path += f"?version={version}"
        res = self.client.get(path)
        ret = res["data"]
        if v2_info["v2"] and not include_metadata:
            return ret["data"]
        return ret

    def read_meta(self, path):
        """
        Read secret metadata for all versions at path. This is different from
        the metadata returned by read, which pertains only to the most recent
        version. Requires KV v2.

        .. versionadded:: 1.2.0
        """
        v2_info = self.is_v2(path)
        if not v2_info["v2"]:
            raise VaultInvocationError("The backend is not KV v2")
        return self.client.get(v2_info["metadata"])["data"]

    def write(self, path, data):
        """
        Write secret data to path.
        """
        v2_info = self.is_v2(path)
        if v2_info["v2"]:
            path = v2_info["data"]
            data = {"data": data}
        return self.client.post(path, payload=data)

    def patch(self, path, data):
        """
        Patch existing data.
        Tries to use a PATCH request, otherwise falls back to updating in memory
        and writing back the whole secret, thus might consume more than one token use.

        Since this uses the `JSON Merge Patch format <https://datatracker.ietf.org/doc/html/draft-ietf-appsawg-json-merge-patch-07>`_,
        values set to ``null`` (``None``) will be dropped.
        """

        def apply_json_merge_patch(data, patch):
            if not patch:
                return data
            if not isinstance(data, dict) or not isinstance(patch, dict):
                raise ValueError("Data and patch must be dictionaries.")

            for key, value in patch.items():
                if value is None:
                    data.pop(key, None)
                elif isinstance(value, dict):
                    data[key] = apply_json_merge_patch(data.get(key, {}), value)
                else:
                    data[key] = value
            return data

        def patch_in_memory(path, data):
            current = self.read(path)
            updated = apply_json_merge_patch(current, data)
            return self.write(path, updated)

        v2_info = self.is_v2(path)
        if not v2_info["v2"]:
            return patch_in_memory(path, data)

        path = v2_info["data"]
        payload = {"data": data}
        try:
            return self.client.patch(path, payload=payload)
        except VaultPermissionDeniedError:
            log.warning("Failed patching secret, is the `patch` capability set?")
        except VaultUnsupportedOperationError:
            pass
        return patch_in_memory(path, data)

    def delete(self, path, versions=None, all_versions=False):
        """
        Delete secret path data. For KV v1, this is permanent.
        For KV v2, this only soft-deletes the data.

        versions
            For KV v2, specifies versions to soft-delete. Needs to be castable
            to a list of integers.

        all_versions
            For KV v2, delete all known versions. Defaults to false.

            .. versionadded:: 1.2.0

        """
        method = "DELETE"
        payload = None
        v2_info = self.is_v2(path)

        if all_versions and v2_info["v2"]:
            versions = []
            try:
                curr = self.read_meta(path)
            except VaultNotFoundError:
                # The delete API behaves the same
                return True
            for version, meta in curr["versions"].items():
                if not meta["destroyed"] and not meta["deletion_time"]:
                    versions.append(version)
            if not versions:
                # No version left to delete
                return True
        versions = self._parse_versions(versions)

        if v2_info["v2"]:
            if versions is not None:
                method = "POST"
                path = v2_info["delete_versions"]
                payload = {"versions": versions}
            else:
                # data and delete operations only differ by HTTP verb
                path = v2_info["data"]
        elif versions is not None:
            raise VaultInvocationError("Versioning support requires KV v2.")

        return self.client.request(method, path, payload=payload)

    def restore(self, path, versions=None, all_versions=False):
        """
        .. versionadded:: 1.2.0

        Restore secret versions. Requires KV v2.

        versions
            Specifies soft-deleted versions of a secret path
            to restore. Needs to be castable to a list of integers.
            If unspecified and the latest version of a secret
            is deleted, restores this version, otherwise fails.

        all_versions
            Restore all soft-deleted versions of the secret. Defaults to false.
        """
        v2_info = self.is_v2(path)
        if not v2_info["v2"]:
            raise VaultInvocationError("Destroy operation requires KV v2.")
        if all_versions or not versions:
            versions = []
            curr = self.read_meta(path)["versions"]
            if all_versions:
                for version, meta in curr.items():
                    if not meta["destroyed"] and meta["deletion_time"]:
                        versions.append(version)
            else:
                most_recent = str(max(int(x) for x in curr))
                if not curr[most_recent]["destroyed"] and curr[most_recent]["deletion_time"]:
                    versions = [most_recent]
            if not versions:
                # No version left to destroy
                raise VaultInvocationError("No secret version to restore.")

        versions = self._parse_versions(versions)
        path = v2_info["undelete"]
        payload = {"versions": versions}
        return self.client.post(path, payload=payload)

    def destroy(self, path, versions=None, all_versions=False):
        """
        Permanently remove version data. Requires KV v2.

        versions
            Specifies versions to destroy. Needs to be castable
            to a list of integers.

            .. versionchanged:: 1.2.0
                If unspecified, destroys the most recent version.

        all_versions
            Destroy all versions of the secret. Defaults to false.

            .. versionadded:: 1.2.0
        """
        v2_info = self.is_v2(path)
        if not v2_info["v2"]:
            raise VaultInvocationError("Destroy operation requires KV v2.")
        if all_versions or not versions:
            versions = []
            try:
                curr = self.read_meta(path)["versions"]
            except VaultNotFoundError:
                # The destroy API behaves the same
                return True
            if all_versions:
                for version, meta in curr.items():
                    if not meta["destroyed"]:
                        versions.append(version)
            else:
                most_recent = str(max(int(x) for x in curr))
                if not curr[most_recent]["destroyed"]:
                    versions = [most_recent]
            if not versions:
                # No version left to destroy
                return True

        versions = self._parse_versions(versions)
        path = v2_info["destroy"]
        payload = {"versions": versions}
        return self.client.post(path, payload=payload)

    def _parse_versions(self, versions):
        if versions is None:
            return versions
        if not isinstance(versions, list):
            versions = [versions]
        try:
            versions = [int(x) for x in versions]
        except ValueError as err:
            raise VaultInvocationError("Versions have to be specified as integers.") from err
        return versions

    def nuke(self, path):
        """
        Delete path metadata and version data, including all version history.
        Requires KV v2.
        """
        v2_info = self.is_v2(path)
        if not v2_info["v2"]:
            raise VaultInvocationError("Wipe operation requires KV v2.")
        path = v2_info["metadata"]
        return self.client.delete(path)

    def list(self, path):
        """
        List keys at path.
        """
        v2_info = self.is_v2(path)
        if v2_info["v2"]:
            path = v2_info["metadata"]

        return self.client.list(path)["data"]["keys"]

    def is_v2(self, path):
        """
        Determines if a given secret path is KV v1 or v2.
        """
        ret = {
            "v2": False,
            "data": path,
            "metadata": path,
            "delete": path,
            "type": None,
        }
        path_metadata = self._get_secret_path_metadata(path)
        if not path_metadata:
            # metadata lookup failed. Simply return not v2
            return ret
        ret["type"] = path_metadata.get("type", "kv")
        if (
            ret["type"] == "kv"
            and path_metadata["options"] is not None
            and path_metadata.get("options", {}).get("version", "1") == "2"
        ):
            ret["v2"] = True
            ret["data"] = self._v2_the_path(path, path_metadata.get("path", path))
            ret["metadata"] = self._v2_the_path(path, path_metadata.get("path", path), "metadata")
            ret["delete"] = ret["data"]
            ret["delete_versions"] = self._v2_the_path(
                path, path_metadata.get("path", path), "delete"
            )
            ret["destroy"] = self._v2_the_path(path, path_metadata.get("path", path), "destroy")
            ret["undelete"] = self._v2_the_path(path, path_metadata.get("path", path), "undelete")
        return ret

    def _v2_the_path(self, path, pfilter, ptype="data"):
        """
        Given a path, a filter, and a path type, properly inject
        'data' or 'metadata' into the path.
        """
        possible_types = ("data", "metadata", "delete", "destroy", "undelete")
        if ptype not in possible_types:
            raise AssertionError()
        msg = f"Path {path} already contains {ptype} in the right place - saltstack duct tape?"

        path = path.rstrip("/").lstrip("/")
        pfilter = pfilter.rstrip("/").lstrip("/")

        together = pfilter + "/" + ptype

        otype = possible_types[0] if possible_types[0] != ptype else possible_types[1]
        other = pfilter + "/" + otype
        if path.startswith(other):
            path = path.replace(other, together, 1)
            msg = f'Path is a "{otype}" type but "{ptype}" type requested - Flipping: {path}'
        elif not path.startswith(together):
            old_path = path
            path = path.replace(pfilter, together, 1)
            msg = f"Converting path to v2 {old_path} => {path}"
        log.debug(msg)
        return path

    def _get_secret_path_metadata(self, path):
        """
        Given a path, query vault to determine mount point, type, and version.
        """
        cache_content = self.metadata_cache.get() or {}

        ret = None
        if path.startswith(tuple(cache_content.keys())):
            log.debug("Found cached metadata for %s", path)
            ret = next(v for k, v in cache_content.items() if path.startswith(k))
        else:
            log.debug("Fetching metadata for %s", path)
            try:
                endpoint = f"sys/internal/ui/mounts/{path}"
                res = self.client.get(endpoint)
                if "data" in res:
                    log.debug("Got metadata for %s", path)
                    cache_content[path] = ret = res["data"]
                    self.metadata_cache.store(cache_content)
                else:
                    raise VaultException("Unexpected response to metadata query.")
            except Exception as err:  # pylint: disable=broad-except
                log.error("Failed to get secret metadata %s: %s", type(err).__name__, err)
        return ret
