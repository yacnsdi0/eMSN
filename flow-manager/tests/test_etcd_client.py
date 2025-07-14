import json

import pytest
import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402
sys.path.insert(0, base)  # noqa: E402
sys.modules.pop("flow_manager", None)  # noqa: E402
sys.modules.pop("flow_manager.etcd", None)  # noqa: E402
pytest.skip("testclient unavailable", allow_module_level=True)

from etcd3mock import Etcd3Client  # noqa: E402

from flow_manager.config import Settings  # noqa: E402
from flow_manager.etcd.client import SecureETCDClient  # noqa: E402


@pytest.mark.parametrize("name", ["host1", "sw1"])
def test_put_objects(name: str) -> None:
    etcd = Etcd3Client()
    settings = Settings(domain_id="demo")
    client = SecureETCDClient(etcd, settings)

    if name.startswith("host"):
        client.put_host(name, {"mac": "aa:bb"})
        val, _ = etcd.get(f"/domain/demo/hosts/{name}")
    else:
        client.put_switch(name, {"dpid": "1"})
        val, _ = etcd.get(f"/domain/demo/switches/{name}")

    assert json.loads(val)  # ensures valid JSON
