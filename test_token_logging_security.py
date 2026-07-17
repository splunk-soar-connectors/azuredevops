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


def test_legacy_and_entra_token_responses_are_not_debugged():
    assert 'host == "app.vssps.visualstudio.com"' in CONNECTOR_SOURCE
    assert 'host == "login.microsoftonline.com"' in CONNECTOR_SOURCE
    assert "if not _is_oauth_token_response(r):" in CONNECTOR_SOURCE
