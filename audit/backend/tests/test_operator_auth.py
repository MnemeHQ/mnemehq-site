"""Operator-only endpoints refuse anonymous callers; the visitor flow does not
need a token. Mirrors security/data-handling: the audit database is
accessible only to Mneme HQ operators."""
import pytest

from app.core.operator_auth import TOKEN_ENV
from test_workspace_contract import workspace  # noqa: F401  (fixture)

TOKEN = "test-operator-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
REPO = "https://github.com/example/contract-fixture"


async def _visitor_audit(client):
    response = await client.post("/api/v1/audit", data={"repository_url": REPO})
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_operator_endpoints_fail_closed_without_configured_token(workspace, monkeypatch):
    monkeypatch.delenv(TOKEN_ENV, raising=False)
    client, _, _ = workspace
    assert (await client.get("/api/v1/projects")).status_code == 403
    assert (await client.get("/api/v1/projects", headers=AUTH)).status_code == 403


@pytest.mark.asyncio
async def test_operator_endpoints_require_the_token(workspace, monkeypatch):
    monkeypatch.setenv(TOKEN_ENV, TOKEN)
    client, _, _ = workspace
    result = await _visitor_audit(client)
    pid = result["project_id"]

    guarded = [
        ("get", "/api/v1/projects", {}),
        ("get", f"/api/v1/projects/{pid}/audits", {}),
        ("get", f"/api/v1/projects/{pid}/contacts", {}),
        ("patch", f"/api/v1/projects/{pid}", {"params": {"name": "renamed"}}),
        ("post", "/api/v1/contacts", {"params": {"email": "x@example.invalid"}}),
        ("post", "/api/v1/projects", {"json": {
            "name": "n", "slug": "s", "source_type": "github", "source_locator": REPO, "default_ref": None}}),
    ]
    for method, url, kwargs in guarded:
        anonymous = await getattr(client, method)(url, **kwargs)
        assert anonymous.status_code == 401, (method, url, anonymous.text)
        wrong = await getattr(client, method)(url, headers={"Authorization": "Bearer nope"}, **kwargs)
        assert wrong.status_code == 401, (method, url)

    listed = await client.get("/api/v1/projects", headers=AUTH)
    assert listed.status_code == 200
    assert [p["id"] for p in listed.json()] == [pid]


@pytest.mark.asyncio
async def test_visitor_flow_needs_no_token(workspace, monkeypatch):
    monkeypatch.setenv(TOKEN_ENV, TOKEN)
    client, _, _ = workspace
    result = await _visitor_audit(client)
    pid, aid = result["project_id"], result["audit_id"]

    assert (await client.get(f"/api/v1/audits/{aid}")).status_code == 200
    assert (await client.get(f"/api/v1/projects/{pid}")).status_code == 200
    assert (await client.get(f"/api/v1/audits/{aid}/export")).status_code == 200
    assert (await client.post("/api/v1/baselines", json={"audit_id": aid})).status_code == 200
    rerun = await client.post(f"/api/v1/projects/{pid}/audits", json={
        "repository_url": REPO, "trigger_type": "re_audit"})
    assert rerun.status_code == 201, rerun.text
    assert (await client.get(f"/api/v1/projects/{pid}/compare")).status_code in (200, 400, 404)
