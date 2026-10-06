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


class UpdateTests(unittest.TestCase):
    def test_patch_and_normalized_result(self):
        c = connector("update_work_item")
        calls = responses(c, [{"id": 12, "fields": {"System.Title": "Changed"}}])
        self.assertEqual(c.handle_action({"work_item_id": 12, "post_body": '[{"op":"add","path":"/fields/System.Title","value":"Changed"}]'}), 0)
        self.assertEqual(calls[0][0:2], ("/_apis/wit/workitems/12", "patch"))
        self.assertEqual(calls[0][2]["json"][0]["value"], "Changed")
        self.assertEqual(c.result.data[0]["fields"]["System-Title"], "Changed")

    def test_invalid_inputs_do_not_send_http(self):
        for item, body in [(12, "invalid"), (12, "{}"), ("../x", "[]")]:
            with self.subTest(item=item, body=body):
                c = connector("update_work_item")
                calls = responses(c, [])
                self.assertEqual(c.handle_action({"work_item_id": item, "post_body": body}), -1)
                self.assertEqual(calls, [])

    def test_failed_patch_propagates(self):
        c = connector("update_work_item")
        responses(c, [RuntimeError()])
        self.assertEqual(c.handle_action({"work_item_id": 12, "post_body": "[]"}), -1)
