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
"""Exercise connector methods without installing the SOAR runtime.

Only the SDK result/base interfaces and external HTTP boundary are substituted.
The connector class and validation helpers are compiled directly from its source.
"""

import ast
import importlib.util
import json
import time
import urllib.parse as urlparse
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


class Result:
    def __init__(self, param):
        self.param = param
        self.status = 0
        self.message = ""
        self.data = []
        self.summary = {}

    def set_status(self, status, message=""):
        self.status, self.message = status, message
        return status

    def get_status(self):
        return self.status

    def get_message(self):
        return self.message

    def add_data(self, data):
        self.data.append(data)

    def update_summary(self, data):
        self.summary.update(data)
        return self.summary


class Base:
    action = ""

    def get_asset_id(self):
        return 1

    def add_action_result(self, result):
        self.result = result
        return result

    def get_action_identifier(self):
        return self.action

    def save_progress(self, *args):
        pass

    def debug_print(self, *args):
        pass


def connector(action):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("consts", root / "azuredevops_consts.py")
    consts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consts)
    tree = ast.parse((root / "azuredevops_connector.py").read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    namespace = {
        "BaseConnector": Base,
        "ActionResult": Result,
        "phantom": SimpleNamespace(APP_SUCCESS=0, APP_ERROR=-1, is_fail=lambda s: s != 0),
        "consts": consts,
        "json": json,
        "time": time,
        "datetime": datetime,
        "timezone": timezone,
        "urlparse": urlparse,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(root / "azuredevops_connector.py"), "exec"), namespace)
    obj = namespace["AzureDevopsConnector"]()
    obj.action = action
    obj._project = "Example"
    obj._organization = "example"
    obj._base_url = "https://dev.azure.com/example/Example"
    obj._api_version = "7.0"
    obj._password = None
    obj._access_token = "old"
    obj._last_http_status = None
    obj._state = {"token": {"access_token": "old"}}
    return obj


def responses(obj, replies):
    """Record actual connector requests and supply deterministic API responses."""
    calls = []
    replies = iter(replies)

    def request(endpoint, result, method="get", **kwargs):
        calls.append((endpoint, method, kwargs))
        reply = next(replies)
        if isinstance(reply, Exception):
            result.set_status(-1, "API failure")
            return -1, None
        return 0, reply

    obj._make_rest_call_helper = request
    return calls
