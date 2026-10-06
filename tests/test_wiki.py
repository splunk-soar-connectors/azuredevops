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


class WikiTests(unittest.TestCase):
    def test_wiki_path_and_recursion_are_forwarded(self):
        c = connector("get_wiki_pages")
        calls = responses(c, [{"id": 1, "path": "/Guide", "content": "Hello", "subPages": []}])
        self.assertEqual(c.handle_action({"wikiidentifier": "A/B", "path": "/Guide", "recursionlevel": "full"}), 0)
        self.assertEqual(calls[0][0], "/_apis/wiki/wikis/A%2FB/pages")
        self.assertEqual(calls[0][2]["params"], {"path": "/Guide", "recursionLevel": "full", "includeContent": "true"})
        self.assertEqual(c.result.data[0]["content"], "Hello")

    def test_wiki_failure_propagates(self):
        c = connector("get_wiki_pages")
        responses(c, [RuntimeError()])
        self.assertEqual(c.handle_action({"wikiidentifier": "missing"}), -1)
