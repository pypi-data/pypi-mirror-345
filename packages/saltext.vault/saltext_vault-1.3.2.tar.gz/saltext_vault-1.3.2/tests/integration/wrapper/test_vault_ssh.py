import pytest

from tests.support.vault import vault_delete
from tests.support.vault import vault_disable_secret_engine
from tests.support.vault import vault_enable_secret_engine
from tests.support.vault import vault_list
from tests.support.vault import vault_read
from tests.support.vault import vault_write

try:
    from cryptography.hazmat.primitives.serialization import SSHCertificateType
    from cryptography.hazmat.primitives.serialization import load_ssh_public_identity

    CERT_CHECK = True
except ImportError:
    CERT_CHECK = False

pytest.importorskip("docker")

pytestmark = [
    pytest.mark.skip_if_binaries_missing("vault"),
    pytest.mark.usefixtures("vault_container_version"),
    pytest.mark.parametrize("vault_container_version", ("latest",), indirect=True),
]


@pytest.fixture(scope="module")
def master_config_overrides():
    return {
        "vault": {
            "policies": {
                "assign": [
                    "salt_minion",
                    "ssh_admin",
                ]
            },
        },
    }


@pytest.fixture
def userrole():
    return {
        "key_type": "ca",
        "allowed_users": "*",
        "allowed_extensions": "*",
        "allow_user_certificates": True,
        "ttl": 3600,
        "max_ttl": 86400,
    }


@pytest.fixture
def hostrole():
    return {
        "key_type": "ca",
        "allowed_domains": "*",
        "allow_host_certificates": True,
        "ttl": 3600,
        "max_ttl": 86400,
    }


@pytest.fixture
def iprole():
    return {
        "key_type": "otp",
        "default_user": "foobar",
        "cidr_list": "0.0.0.0/1",
        "exclude_cidr_list": "128.0.0.0/1",
        "port": 9876,
    }


@pytest.fixture
def ec_priv():
    return """
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAaAAAABNlY2RzYS1zaGEy
LW5pc3RwMjU2AAAACG5pc3RwMjU2AAAAQQSO2hM3nJP6fxgzyXIEEKhHeqOqXccIvV8EZLfqCrcX
NGR7Be7yYdPNx+bcNFx5fyLrxKin+f/4pV4/q+mMoqVxAAAAoHwE+2V8BPtlAAAAE2VjZHNhLXNo
YTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBI7aEzeck/p/GDPJcgQQqEd6o6pdxwi9XwRkt+oK
txc0ZHsF7vJh083H5tw0XHl/IuvEqKf5//ilXj+r6YyipXEAAAAgc5sbtq4PEIHmkqJzEbNaO1sB
2PSfCjWqlGSC7ODBqy4AAAAAAQIDBAUGBwg=
-----END OPENSSH PRIVATE KEY-----
    """.strip()


@pytest.fixture
def ec_priv_file(ec_priv, tmp_path):
    path = tmp_path / "ec"
    path.write_text(ec_priv)
    return str(path)


@pytest.fixture
def ec_pub():
    return "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBI7aEzeck/p/GDPJcgQQqEd6o6pdxwi9XwRkt+oKtxc0ZHsF7vJh083H5tw0XHl/IuvEqKf5//ilXj+r6YyipXE="


@pytest.fixture
def ec_pub_file(ec_pub, tmp_path):
    path = tmp_path / "ec.pub"
    path.write_text(ec_pub)
    return str(path)


@pytest.fixture(scope="module", autouse=True)
def ssh_engine(vault_container_version):  # pylint: disable=unused-argument
    assert vault_enable_secret_engine("ssh")
    yield
    assert vault_disable_secret_engine("ssh")


@pytest.fixture(params=(("userrole", "hostrole", "iprole"),))
def roles_setup(request):  # pylint: disable=unused-argument
    try:
        for role_name in request.param:
            role_args = request.getfixturevalue(role_name)
            vault_write(f"ssh/roles/{role_name}", **role_args)
            assert role_name in vault_list("ssh/roles")
        yield
    finally:
        for role_name in request.param:
            if role_name in vault_list("ssh/roles"):
                vault_delete(f"ssh/roles/{role_name}")
                assert role_name not in vault_list("ssh/roles")


@pytest.mark.usefixtures("roles_setup")
def test_read_role(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.read_role", "userrole")
    assert res.returncode == 0
    expected = {
        "algorithm_signer": "default",
        "allow_bare_domains": False,
        "allow_host_certificates": False,
        "allow_subdomains": False,
        "allow_user_certificates": True,
        "allow_user_key_ids": False,
        "allowed_critical_options": "",
        "allowed_domains": "",
        "allowed_domains_template": False,
        "allowed_extensions": "*",
        "allowed_user_key_lengths": {},
        "allowed_users": "*",
        "allowed_users_template": False,
        "default_critical_options": {},
        "default_extensions": {},
        "default_extensions_template": False,
        "default_user": "",
        "default_user_template": False,
        "key_id_format": "",
        "key_type": "ca",
        "max_ttl": 86400,
        "ttl": 3600,
    }
    for var, val in expected.items():
        assert var in res.data
        assert res.data[var] == val


@pytest.fixture
def _temp_role():
    name = "testrole"
    try:
        yield name
    finally:
        vault_delete(f"ssh/roles/{name}")


def test_write_role_ca(salt_ssh_cli, userrole, _temp_role):
    key_type = userrole.pop("key_type")
    res = salt_ssh_cli.run("vault_ssh.write_role_ca", _temp_role, **userrole)
    assert res.returncode == 0
    assert res.data is True
    data = vault_read(f"ssh/roles/{_temp_role}")["data"]
    assert data["key_type"] == key_type
    for var, val in userrole.items():
        assert var in data
        assert data[var] == val


def test_write_role_otp(salt_ssh_cli, iprole, _temp_role):
    key_type = iprole.pop("key_type")
    res = salt_ssh_cli.run("vault_ssh.write_role_otp", _temp_role, **iprole)
    assert res.returncode == 0
    assert res.data is True
    data = vault_read(f"ssh/roles/{_temp_role}")["data"]
    assert data["key_type"] == key_type
    for var, val in iprole.items():
        assert var in data
        assert data[var] == val


@pytest.mark.usefixtures("roles_setup")
def test_delete_role(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.delete_role", "userrole")
    assert res.returncode == 0
    assert res.data is True
    assert "userrole" not in vault_list("ssh/roles")


@pytest.mark.usefixtures("roles_setup")
def test_list_roles(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.list_roles")
    assert res.returncode == 0
    for role in ("userrole", "hostrole", "iprole"):
        assert role in res.data


@pytest.mark.usefixtures("roles_setup")
def test_list_roles_ip(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.list_roles_ip", "10.1.0.1")
    assert res.returncode == 0
    assert res.data == ["iprole"]


@pytest.mark.usefixtures("roles_setup")
def test_zeroaddress_roles(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.list_roles_zeroaddr")
    assert res.returncode == 0
    assert res.data == []
    res = salt_ssh_cli.run("vault_ssh.write_zeroaddr_roles", ["iprole"])
    assert res.returncode == 0
    assert res.data is True
    res = salt_ssh_cli.run("vault_ssh.list_roles_zeroaddr")
    assert res.returncode == 0
    assert res.data == ["iprole"]
    res = salt_ssh_cli.run("vault_ssh.delete_zeroaddr_roles")
    assert res.returncode == 0
    assert res.data is True
    res = salt_ssh_cli.run("vault_ssh.list_roles_zeroaddr")
    assert res.returncode == 0
    assert res.data == []


@pytest.fixture
def _temp_ca():
    try:
        yield
    finally:
        vault_delete("ssh/config/ca")


@pytest.mark.usefixtures("_temp_ca")
def test_create_ca(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.create_ca")
    assert res.returncode == 0
    assert res.data.startswith("ssh-rsa ")
    assert "public_key" in vault_read("ssh/config/ca")["data"]


@pytest.mark.usefixtures("_temp_ca")
def test_create_ca_key_spec(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.create_ca", key_type="ec", key_bits=384)
    assert res.returncode == 0
    assert res.data.startswith("ecdsa-")
    assert "p384" in res.data
    assert "public_key" in vault_read("ssh/config/ca")["data"]


@pytest.mark.usefixtures("_temp_ca")
def test_create_ca_with_keys(salt_ssh_cli, ec_pub, ec_priv_file):
    res = salt_ssh_cli.run("vault_ssh.create_ca", public_key=ec_pub, private_key=ec_priv_file)
    assert res.returncode == 0
    assert res.data == ec_pub
    assert "public_key" in vault_read("ssh/config/ca")["data"]


@pytest.fixture
def ca_setup(ec_priv, ec_pub):
    vault_write("ssh/config/ca", private_key=ec_priv, public_key=ec_pub)
    assert vault_read("ssh/config/ca", default=False)
    try:
        yield
    finally:
        vault_delete("ssh/config/ca")


@pytest.mark.usefixtures("ca_setup")
def test_read_ca(salt_ssh_cli, ec_pub):
    res = salt_ssh_cli.run("vault_ssh.read_ca")
    assert res.returncode == 0
    assert res.data == ec_pub


@pytest.mark.usefixtures("ca_setup")
def test_destroy_ca(salt_ssh_cli):
    res = salt_ssh_cli.run("vault_ssh.destroy_ca")
    assert res.returncode == 0
    assert res.data is True
    try:
        res = vault_read("ssh/config/ca", raise_errors=True)
    except RuntimeError as err:
        assert "keys haven't been configured yet" in str(err)
    else:
        raise AssertionError(f"CA has not been deleted: {res}")


@pytest.mark.usefixtures("ca_setup", "roles_setup")
def test_sign_key_user(salt_ssh_cli, ec_pub):
    res = salt_ssh_cli.run(
        "vault_ssh.sign_key",
        "userrole",
        ec_pub,
        critical_options={"force-command": "rm -rf /"},
        extensions={"permit-pty": ""},
        valid_principals=["foobar"],
    )
    assert res.returncode == 0
    assert set(res.data) == {"serial_number", "signed_key"}
    if CERT_CHECK:
        cert = load_cert(res.data["signed_key"])
        assert cert.type == SSHCertificateType.USER
        assert cert.critical_options == {b"force-command": b"rm -rf /"}
        assert cert.extensions == {b"permit-pty": b""}
        assert cert.valid_principals == [b"foobar"]


@pytest.mark.usefixtures("ca_setup", "roles_setup")
def test_sign_key_host(salt_ssh_cli, ec_pub):
    res = salt_ssh_cli.run(
        "vault_ssh.sign_key", "hostrole", ec_pub, cert_type="host", valid_principals=["foo.bar.biz"]
    )
    assert res.returncode == 0
    assert set(res.data) == {"serial_number", "signed_key"}
    if CERT_CHECK:
        cert = load_cert(res.data["signed_key"])
        assert cert.type == SSHCertificateType.HOST
        assert not cert.critical_options
        assert cert.valid_principals == [b"foo.bar.biz"]


@pytest.mark.usefixtures("ca_setup", "roles_setup")
def test_generate_key_cert_user(salt_ssh_cli):
    res = salt_ssh_cli.run(
        "vault_ssh.generate_key_cert",
        "userrole",
        critical_options={"force-command": "rm -rf /"},
        extensions={"permit-pty": ""},
        valid_principals=["foobar"],
    )
    assert res.returncode == 0
    assert set(res.data) == {"private_key", "private_key_type", "serial_number", "signed_key"}
    assert res.data["private_key_type"] == "ssh-rsa"
    assert res.data["private_key"].startswith("-----BEGIN")
    if CERT_CHECK:
        cert = load_cert(res.data["signed_key"])
        assert cert.type == SSHCertificateType.USER
        assert cert.critical_options == {b"force-command": b"rm -rf /"}
        assert cert.extensions == {b"permit-pty": b""}
        assert cert.valid_principals == [b"foobar"]


@pytest.mark.usefixtures("ca_setup", "roles_setup")
def test_generate_key_cert_host(salt_ssh_cli):
    res = salt_ssh_cli.run(
        "vault_ssh.generate_key_cert",
        "hostrole",
        cert_type="host",
        valid_principals=["foo.bar.biz"],
    )
    assert res.returncode == 0
    assert set(res.data) == {"private_key", "private_key_type", "serial_number", "signed_key"}
    assert res.data["private_key_type"] == "ssh-rsa"
    assert res.data["private_key"].startswith("-----BEGIN")
    if CERT_CHECK:
        cert = load_cert(res.data["signed_key"])
        assert cert.type == SSHCertificateType.HOST
        assert not cert.critical_options
        assert cert.valid_principals == [b"foo.bar.biz"]


def load_cert(data):
    return load_ssh_public_identity(data.encode())
