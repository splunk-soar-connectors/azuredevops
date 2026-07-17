# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path


CONNECTOR_SOURCE = Path("azuredevops_connector.py").read_text()


def test_oauth_callbacks_require_a_high_entropy_one_time_nonce():
    assert "secrets.token_hex(32)" in CONNECTOR_SOURCE
    assert "hmac.compare_digest(stored_nonce, presented_nonce)" in CONNECTOR_SOURCE
    assert "state.pop(consts.AZURE_DEVOPS_OAUTH_STATE_NONCE, None)" in CONNECTOR_SOURCE


def test_invalid_oauth_callbacks_do_not_signal_completion():
    assert "return_val.status_code < 400" in CONNECTOR_SOURCE
    assert "Invalid or expired OAuth state" in CONNECTOR_SOURCE
