import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402
sys.path.insert(0, base)  # noqa: E402

import pytest  # noqa: E402

pytest.skip("testclient unavailable", allow_module_level=True)

from flow_manager.app import create_app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def test_healthz() -> None:
    app = create_app()
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
