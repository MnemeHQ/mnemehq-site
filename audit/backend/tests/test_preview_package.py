"""No cloud access or database connection: preview package safety/routing."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.preview import PreviewSite, require_preview_database, MIGRATOR_USER


@pytest.mark.parametrize('url', ['', 'not-a-url',
    'postgresql+asyncpg://mneme_audit_user:test@localhost/mneme_audit_preview',
    'postgresql+asyncpg://mneme_audit_preview_runtime:test@localhost/mneme_audit',
    'postgresql+asyncpg://mneme_audit_preview_runtime@localhost/mneme_audit_preview',
    'sqlite:///mneme_audit_preview'])
def test_preview_rejects_missing_admin_or_production_credentials(monkeypatch, url):
    monkeypatch.setenv('DATABASE_URL', url)
    with pytest.raises(RuntimeError, match='explicit restricted preview') as error:
        require_preview_database()
    assert 'postgresql' not in str(error.value)


def test_preview_runtime_and_migration_credentials_are_separate(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql+asyncpg://mneme_audit_preview_runtime:test@localhost/mneme_audit_preview')
    assert require_preview_database().database == 'mneme_audit_preview'
    with pytest.raises(RuntimeError):
        require_preview_database(MIGRATOR_USER)
    monkeypatch.setenv('DATABASE_URL', 'postgresql+asyncpg://mneme_audit_preview_migrator:test@localhost/mneme_audit_preview')
    assert require_preview_database(MIGRATOR_USER).username == MIGRATOR_USER
    with pytest.raises(RuntimeError):
        require_preview_database()
    monkeypatch.setenv('DB_ECHO', 'true')
    with pytest.raises(RuntimeError):
        require_preview_database(MIGRATOR_USER)


@pytest.mark.parametrize('custom_404', [False, True])
def test_preview_clean_deep_links_do_not_swallow_api_or_asset_errors(tmp_path, custom_404):
    workspace = tmp_path / 'audit/workspace'
    workspace.mkdir(parents=True)
    (workspace / 'index.html').write_text('<main>Workspace shell</main>')
    (tmp_path / 'audit/index.html').write_text('<main>Architecture Protection</main>')
    if custom_404:
        (tmp_path / '404.html').write_text('<main>Site not found</main>')
    app = FastAPI()

    @app.get('/api/check')
    def check():
        return {'real_api': True}

    app.mount('/', PreviewSite(directory=str(tmp_path), html=True))
    with TestClient(app) as client:
        for path in ('/audit/workspace/', '/audit/workspace/project/abc',
                     '/audit/workspace/project/abc/compare', '/audit/workspace/audit/abc/decisions/one'):
            response = client.get(path)
            assert response.status_code == 200
            assert 'Workspace shell' in response.text
        assert 'Architecture Protection' in client.get('/audit/').text
        assert client.get('/api/check').json() == {'real_api': True}
        assert client.get('/api/missing').status_code == 404
        assert client.get('/audit/workspace/assets/missing.js').status_code == 404
