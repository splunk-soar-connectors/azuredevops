from pathlib import Path


CONNECTOR_SOURCE = Path("azuredevops_connector.py").read_text()


def test_legacy_and_entra_token_responses_are_not_debugged():
    assert 'host == "app.vssps.visualstudio.com"' in CONNECTOR_SOURCE
    assert 'host == "login.microsoftonline.com"' in CONNECTOR_SOURCE
    assert "if not _is_oauth_token_response(r):" in CONNECTOR_SOURCE
