import json
import os
import sys
from unittest.mock import patch

import pytest

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)  # noqa: E402
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402

import etcd3  # noqa: E402

sys.modules.pop("flow_manager", None)  # noqa: E402
sys.modules.pop("flow_manager.etcd", None)  # noqa: E402

from etcd3mock import Etcd3Client  # noqa: E402
from flow_manager.config import Settings  # noqa: E402
from flow_manager.etcd.client import SecureETCDClient  # noqa: E402


@pytest.fixture()
def fm_client() -> SecureETCDClient:
    etcd = Etcd3Client()
    settings = Settings(domain_id="42")
    return SecureETCDClient(etcd, settings)


@pytest.mark.parametrize("name", ["host1", "sw1"])
def test_put_objects(fm_client: SecureETCDClient, name: str) -> None:
    if name.startswith("host"):
        fm_client.put_host(name, {"mac": "aa:bb"})
        val, _ = fm_client.client.get(f"/domain/42/hosts/{name}")
    else:
        fm_client.put_switch(name, {"dpid": "1"})
        val, _ = fm_client.client.get(f"/domain/42/switches/{name}")
    assert json.loads(val)


def test_schema_validation_error(fm_client: SecureETCDClient) -> None:
    bad_value = {"mac": "not-a-mac", "dpid": "1", "port": 0}
    with pytest.raises(ValueError):
        fm_client.put_host("10.0.0.99", bad_value)


def flaky_put(*_: object, **__: object) -> None:
    raise etcd3.exceptions.ConnectionFailedError("BOOM")


def test_retry_backoff(fm_client: SecureETCDClient) -> None:
    with patch.object(fm_client.client, "put", side_effect=flaky_put):
        with pytest.raises(RuntimeError):
            fm_client.put_host(
                "10.0.0.50",
                {"mac": "aa:bb:cc:dd:ee:ff", "dpid": "000...0001", "port": 1},
            )


def test_cas_success(fm_client: SecureETCDClient) -> None:
    key = "/domain/42/hosts/10.0.0.1"
    initial = {"mac": "aa:bb:cc:dd:ee:ff", "dpid": "000...0001", "port": 1}
    updated = initial | {"port": 2}
    fm_client.put(key, initial)
    assert fm_client.cas(key, initial, updated) is True
    assert fm_client.get(key)["port"] == 2
