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
CONSTS_SOURCE = Path("azuredevops_consts.py").read_text()


def test_search_users_has_page_and_result_limits():
    assert "AZURE_DEVOPS_MAX_PAGINATION_PAGES = 1000" in CONSTS_SOURCE
    assert "AZURE_DEVOPS_MAX_PAGINATION_ITEMS = 100000" in CONSTS_SOURCE
    assert "page_count >= consts.AZURE_DEVOPS_MAX_PAGINATION_PAGES" in CONNECTOR_SOURCE
    assert "total_items > consts.AZURE_DEVOPS_MAX_PAGINATION_ITEMS" in CONNECTOR_SOURCE


def test_search_users_rejects_repeated_continuation_tokens():
    assert "continuation_token in seen_continuation_tokens" in CONNECTOR_SOURCE
