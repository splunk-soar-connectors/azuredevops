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


def test_string_identifiers_are_encoded_as_path_segments():
    assert 'urlparse.quote(str(value), safe="")' in CONNECTOR_SOURCE
    assert "team=_quote_path_segment(team)" in CONNECTOR_SOURCE
    assert 'work_item_type = _quote_path_segment(param["work_item_type"])' in CONNECTOR_SOURCE
    assert 'user_id = _quote_path_segment(param["user_id"])' in CONNECTOR_SOURCE


def test_work_item_ids_are_coerced_to_integers_before_use():
    assert CONNECTOR_SOURCE.count('_parse_work_item_id(param["work_item_id"], action_result)') == 2
    assert "Work item ID must be an integer" in CONNECTOR_SOURCE
