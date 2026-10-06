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

from test_support import Result, connector


class RefreshTests(unittest.TestCase):
    def exercise(self, statuses, password=None, refresh_status=0, misleading=False):
        c = connector("get_work_item")
        c._password = password
        count = []
        refreshes = []
        statuses = iter(statuses)
        result = Result({})

        def request(endpoint, action_result, *args, **kwargs):
            status = next(statuses)
            c._last_http_status = status
            count.append(kwargs["headers"]["Authorization"])
            action_result.set_status(0 if status == 200 else -1, "contains 401" if misleading else f"HTTP {status}")
            return action_result.get_status(), {"id": 1} if status == 200 else None

        def refresh(action_result):
            refreshes.append(True)
            c._access_token = "new"
            if refresh_status:
                action_result.set_status(-1, "Refresh failed")
            return refresh_status

        c._make_rest_call = request
        c._get_token = refresh
        status, data = c._make_rest_call_helper("/items", result)
        return status, data, count, refreshes

    def test_401_refreshes_and_retries_once(self):
        self.assertEqual(self.exercise([401, 200]), (0, {"id": 1}, ["Bearer old", "Bearer new"], [True]))

    def test_basic_auth_never_refreshes(self):
        self.assertEqual(self.exercise([401], password="pat")[3], [])  # pragma: allowlist secret

    def test_refresh_failure_stops_retry(self):
        self.assertEqual(self.exercise([203], refresh_status=-1)[2:], (["Bearer old"], [True]))

    def test_failed_retry_does_not_refresh_again(self):
        self.assertEqual(self.exercise([401, 401])[2:], (["Bearer old", "Bearer new"], [True]))

    def test_error_text_does_not_trigger_refresh(self):
        self.assertEqual(self.exercise([500], misleading=True)[3], [])

    def test_real_response_processing_drives_refresh(self):
        from types import SimpleNamespace

        c = connector("get_work_item")
        result = Result({})
        statuses = iter([401, 200])
        refreshes = []

        def process_json(response, action_result):
            status = 0 if response.status_code == 200 else -1
            action_result.set_status(status)
            return status, {"id": 1} if status == 0 else None

        def request(endpoint, action_result, *args, **kwargs):
            return c._process_response(SimpleNamespace(status_code=next(statuses), headers={"Content-Type": "application/json"}), action_result)

        def refresh(action_result):
            refreshes.append(True)
            c._access_token = "new"
            return 0

        c._process_json_response = process_json
        c._make_rest_call = request
        c._get_token = refresh
        self.assertEqual(c._make_rest_call_helper("/items", result), (0, {"id": 1}))
        self.assertEqual(refreshes, [True])
