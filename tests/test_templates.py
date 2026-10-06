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

from test_support import connector, responses


class TemplateTests(unittest.TestCase):
    def test_get_template_encodes_identifiers(self):
        c = connector("get_template")
        calls = responses(c, [{"id": "template", "name": "Standard", "workItemTypeName": "Task"}])
        self.assertEqual(c.handle_action({"team": "A/B", "template_id": "id/part"}), 0)
        self.assertEqual(calls[0][0], "/A%2FB/_apis/wit/templates/id%2Fpart")
        self.assertEqual(c.result.summary["template_name"], "Standard")

    def test_list_templates_reports_count(self):
        c = connector("list_templates")
        responses(c, [{"count": 1, "value": [{"id": "one", "name": "Standard"}]}])
        self.assertEqual(c.handle_action({"team": "Team"}), 0)
        self.assertEqual(c.result.summary["total_templates"], 1)

    def test_template_failure_propagates(self):
        c = connector("get_template")
        responses(c, [RuntimeError()])
        self.assertEqual(c.handle_action({"team": "Team", "template_id": "missing"}), -1)
