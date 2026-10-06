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


class ListTests(unittest.TestCase):
    def test_large_iteration_uses_multiple_batches(self):
        c = connector("list_work_items")
        calls = responses(
            c, [{"workItems": [{"id": i} for i in range(1, 202)]}, {"value": [{"id": 1, "fields": {"System.Title": "Item"}}]}, {"value": []}]
        )
        self.assertEqual(c.handle_action({"team": "Team", "iteration": "current", "fields": "System.Title"}), 0)
        self.assertEqual([len(x[2]["json"]["ids"]) for x in calls[1:]], [200, 1])
        self.assertIn("@currentIteration('[Example]\\Team')", calls[0][2]["json"]["query"])
        self.assertEqual(c.result.data[0]["workItems"][0]["fields"]["System-Title"], "Item")

    def test_future_skips_undated_iterations(self):
        c = connector("list_work_items")
        calls = responses(
            c,
            [
                {
                    "value": [
                        {"name": "Undated", "path": "Example\\Undated", "attributes": {}},
                        {"name": "Next", "path": "Example\\Next", "attributes": {"startDate": "2099-01-01T00:00:00Z"}},
                    ]
                },
                {"workItems": []},
            ],
        )
        self.assertEqual(c.handle_action({"team": "Team", "iteration": "future"}), 0)
        self.assertEqual(c.result.summary["resolved_iteration_name"], "Next")
        self.assertIn("Example\\Next", calls[1][2]["json"]["query"])

    def test_past_skips_undated_iterations(self):
        c = connector("list_work_items")
        responses(
            c,
            [
                {
                    "value": [
                        {"name": "Undated", "path": "Example\\Undated", "attributes": {}},
                        {"name": "Last", "path": "Example\\Last", "attributes": {"finishDate": "2001-01-01T00:00:00Z"}},
                    ]
                },
                {"workItems": []},
            ],
        )
        self.assertEqual(c.handle_action({"team": "Team", "iteration": "past"}), 0)
        self.assertEqual(c.result.summary["resolved_iteration_name"], "Last")

    def test_quotes_are_escaped(self):
        c = connector("list_work_items")
        calls = responses(c, [{"workItems": []}])
        c.handle_action({"team": "Team", "iteration": "Example\\User's Sprint", "work_item_type": "User's Story"})
        self.assertIn("User''s Sprint", calls[0][2]["json"]["query"])
        self.assertIn("User''s Story", calls[0][2]["json"]["query"])

    def test_fields_and_expand_are_exclusive(self):
        c = connector("list_work_items")
        calls = responses(c, [])
        self.assertEqual(c.handle_action({"team": "Team", "iteration": "current", "fields": "System.Title", "expand": "All"}), -1)
        self.assertEqual(calls, [])

    def test_iteration_response_counts_toward_byte_limit(self):
        c = connector("list_work_items")

        def request(endpoint, result, method="get", **kwargs):
            c._last_response_size = 9 * 1024 * 1024
            if "iterations" in endpoint:
                return 0, {"value": [{"name": "Next", "path": "Example\\Next", "attributes": {"startDate": "2099-01-01T00:00:00Z"}}]}
            if "wiql" in endpoint:
                return 0, {"workItems": [{"id": 1}]}
            return 0, {"value": [{"id": 1, "fields": {}}]}

        c._make_rest_call_helper = request
        self.assertEqual(c.handle_action({"team": "Team", "iteration": "future"}), -1)
