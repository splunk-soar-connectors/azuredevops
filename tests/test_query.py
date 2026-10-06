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


class QueryTests(unittest.TestCase):
    def test_flat_results_are_batched_and_normalized(self):
        c = connector("query_work_items")
        calls = responses(
            c,
            [
                {"workItems": [{"id": i} for i in range(1, 202)]},
                {"value": [{"id": 1, "fields": {"System.Title": "Item"}}]},
                {"value": [{"id": 201, "fields": {}}]},
            ],
        )
        self.assertEqual(c.handle_action({"wiql_query": "SELECT [System.Id] FROM WorkItems", "fields": "System.Title, System.State"}), 0)
        self.assertEqual([len(x[2]["json"]["ids"]) for x in calls[1:]], [200, 1])
        self.assertEqual(calls[1][2]["json"]["fields"], ["System.Title", "System.State"])
        self.assertEqual(c.result.data[0]["workItems"][0]["fields"]["System-Title"], "Item")
        self.assertEqual(c.result.summary["total_work_items"], 2)

    def test_relation_targets_are_deduplicated(self):
        c = connector("query_work_items")
        calls = responses(
            c, [{"workItemRelations": [{"target": {"id": 2}}, {"target": {"id": 2}}, {"target": None}, {"target": {"id": 3}}]}, {"value": []}]
        )
        c.handle_action({"wiql_query": "SELECT [System.Id] FROM WorkItemLinks"})
        self.assertEqual(calls[1][2]["json"]["ids"], [2, 3])

    def test_no_results_is_success(self):
        c = connector("query_work_items")
        responses(c, [{"workItems": []}])
        self.assertEqual(c.handle_action({"wiql_query": "SELECT [System.Id] FROM WorkItems"}), 0)
        self.assertEqual(c.result.summary["total_work_items"], 0)

    def test_batch_failure_propagates(self):
        c = connector("query_work_items")
        responses(c, [{"workItems": [{"id": 1}]}, RuntimeError()])
        self.assertEqual(c.handle_action({"wiql_query": "SELECT [System.Id] FROM WorkItems"}), -1)

    def test_too_many_results_are_bounded(self):
        c = connector("query_work_items")
        calls = responses(c, [{"workItems": [{"id": i} for i in range(1, 10002)]}])
        self.assertEqual(c.handle_action({"wiql_query": "SELECT [System.Id] FROM WorkItems"}), -1)
        self.assertEqual(len(calls), 1)

    def test_historical_query_hydrates_at_query_timestamp(self):
        c = connector("query_work_items")
        calls = responses(c, [{"asOf": "2020-01-01T00:00:00Z", "workItems": [{"id": 1}]}, {"value": []}])
        c.handle_action({"wiql_query": "SELECT [System.Id] FROM WorkItems ASOF '2020-01-01'"})
        self.assertEqual(calls[1][2]["json"].get("asOf"), "2020-01-01T00:00:00Z")
