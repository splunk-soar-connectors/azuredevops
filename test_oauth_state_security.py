from pathlib import Path


CONNECTOR_SOURCE = Path("azuredevops_connector.py").read_text()


def test_oauth_callbacks_require_a_high_entropy_one_time_nonce():
    assert "secrets.token_hex(32)" in CONNECTOR_SOURCE
    assert "hmac.compare_digest(stored_nonce, presented_nonce)" in CONNECTOR_SOURCE
    assert "state.pop(consts.AZURE_DEVOPS_OAUTH_STATE_NONCE, None)" in CONNECTOR_SOURCE


def test_invalid_oauth_callbacks_do_not_signal_completion():
    assert "return_val.status_code < 400" in CONNECTOR_SOURCE
    assert "Invalid or expired OAuth state" in CONNECTOR_SOURCE
