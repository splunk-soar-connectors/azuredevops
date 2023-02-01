# File: azuredevops_consts.py
#
# Copyright (c) 2022 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
from collections import namedtuple

TC_FILE = "oauth_task.out"

AZURE_DEVOPS_PHANTOM_BASE_URL = "{phantom_base_url}rest"
AZURE_DEVOPS_PHANTOM_ASSET_INFO_URL = "/asset/{asset_id}"
AZURE_DEVOPS_PHANTOM_SYS_INFO_URL = "/system_info"
AZURE_DEVOPS_BASE_URL_NOT_FOUND_MESSAGE = "Phantom Base URL not found in System Settings. Please specify this value in System Settings."
AZURE_DEVOPS_ERROR_MESSAGE_UNAVAILABLE = "Error message unavailable. Please check the asset configuration and|or action parameters."
AZURE_DEVOPS_STATE_FILE_CORRUPT_ERROR = (
    "Error occurred while loading the state file due to its unexpected format."
)

AZURE_DEVOPS_AUTHORIZE_TROUBLESHOOT_MESSAGE = (
    "If authorization URL fails to communicate with your Phantom instance, check whether you have:  "
    " 1. Specified the Web Redirect URL of your App -- The Redirect URL should be <POST URL>/result . "
    " 2. Configured the base URL of your Phantom Instance at Administration -> Company Settings -> Info"
)
AZURE_DEVOPS_DEVOPS_DECRYPTION_ERROR = "Error occurred while decrypting the state file"
AZURE_DEVOPS_REST_URL_NOT_AVAILABLE_MESSAGE = "Rest URL not available. Error: {error}"
AZURE_DEVOPS_GENERATING_ACCESS_TOKEN_MESSAGE = "Generating access token"
AZURE_DEVOPS_OAUTH_URL_MESSAGE = "Using OAuth URL:\n"
AZURE_DEVOPS_CODE_GENERATION_SCOPE = (
    "vso.entitlements vso.memberentitlementmanagement_write vso.work_full"
)
PERMISSION_CODE = "0664"
AZURE_DEVOPS_TC_STATUS_SLEEP = 2


# For encryption and decryption
AZURE_DEVOPS_ENCRYPT_TOKEN = "Encrypting the {} token"
AZURE_DEVOPS_DECRYPT_TOKEN = "Decrypting the {} token"
AZURE_DEVOPS_ENCRYPTION_ERROR = "Error occurred while encrypting the state file"
AZURE_DEVOPS_DECRYPTION_ERROR = "Error occurred while decrypting the state file"
AZURE_DEVOPS_STATE_IS_ENCRYPTED = "is_encrypted"


AZURE_DEVOPS_TOKEN_STRING = "token"
AZURE_DEVOPS_ACCESS_TOKEN_STRING = "access_token"

AUTH_FAILURE_MESSAGES = (
    "token is invalid",
    "token has expired",
    "ExpiredAuthenticationToken",
    "AuthenticationFailed",
)

GrantTypeNamespace = namedtuple(
    "GrantTypeNamespace",
    ["JWT_BEARER_TOKEN", "REFRESH_TOKEN"]
)

grant_types = GrantTypeNamespace(
    "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "refresh_token"
)

AssertionTypeNamespace = namedtuple(
    "AssertionTypeNamespace",
    ["CLIENT_ASSERTION"]
)

assertion_types = AssertionTypeNamespace(
    "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
)

ContentTypeNamespace = namedtuple(
    "ContentTypeNamespace",
    ["TEXT_PLAIN", "APPLICATION_JSON", "FORM_URLENCODED", "DEFAULT"],
)

content_types = ContentTypeNamespace(
    "text/plain", "application/json", "application/x-www-form-urlencoded", "*/*"
)

EndpointsNamespace = namedtuple(
    "EndpointsNamespace",
    ["ITERATIONS", "ITERATIONS_TEAM", "WORK_ITEMS", "COMMENTS", "USER_ENTITLEMENTS"],
)

endpoints = EndpointsNamespace(
    "/_apis/work/teamsettings/iterations",
    "/{team}/_apis/work/teamsettings/iterations",
    "/_apis/wit/workitems",
    "/_apis/wit/workItems/{workItemId}/comments",
    "/_apis/userentitlements",
)


BaseUrlNamespace = namedtuple(
    "BaseUrlNamespace",
    ["PROJECT_BASE_URL", "USER_ENTITLEMENT_URL", "TOKEN_URL", "AUTHORIZATION_URL"],
)

base_urls = BaseUrlNamespace(
    "https://dev.azure.com/{organization}/{project}",
    "https://vsaex.dev.azure.com/{organization}",
    "https://app.vssps.visualstudio.com/oauth2/token",
    "https://app.vssps.visualstudio.com/oauth2/authorize",
)
