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
import unittest

from .test_support import connector, responses


class FieldsTests(unittest.TestCase):
    def test_spaced_fields_reach_api_without_spaces(self):
        c = connector("get_work_item")
        calls = responses(c, [{"id": 12, "fields": {"System.Title": "Example"}}])
        self.assertEqual(c.handle_action({"work_item_id": 12, "expand": "None", "fields": "System.Title, System.State"}), 0)
        self.assertEqual(calls[0][2]["params"]["fields"], "System.Title,System.State")

    def test_invalid_id_still_fails_before_http(self):
        c = connector("get_work_item")
        calls = responses(c, [])
        self.assertEqual(c.handle_action({"work_item_id": "../other", "expand": "None"}), -1)
        self.assertEqual(calls, [])
