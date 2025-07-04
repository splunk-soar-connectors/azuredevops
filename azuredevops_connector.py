# File: azuredevops_connector.py
#
# Copyright (c) 2022-2025 Splunk Inc.
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

import grp
import json
import os
import pwd
import sys
import time
import urllib.parse as urlparse

import encryption_helper
import phantom.app as phantom
import phantom.rules as phantom_rules
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

import azuredevops_consts as consts


def _save_app_state(state, asset_id, app_connector):
    """This function is used to save current state in file.

    :param state: Dictionary which contains data to write in state file
    :param asset_id: asset_id
    :param app_connector: Object of app_connector class
    :return: status: phantom.APP_SUCCESS
    """

    asset_id = str(asset_id)
    if not asset_id or not asset_id.isalnum():
        debug_print_invalid_asset_id(app_connector)
        return

    app_dir = os.path.split(__file__)[0]
    state_file = f"{app_dir}/{asset_id}_state.json"

    real_state_file_path = os.path.abspath(state_file)
    if os.path.dirname(real_state_file_path) != app_dir:
        debug_print_invalid_asset_id(app_connector)
        return

    if app_connector:
        app_connector.debug_print("Saving state: ", state)

    try:
        with open(real_state_file_path, "w") as state_file_obj:
            state_file_obj.write(json.dumps(state))
    except Exception as e:
        if app_connector:
            app_connector.error_print(f"Unable to save state file: {e!s}")
    return


def _load_app_state(asset_id, app_connector=None):
    """This function is used to load the current state file.

    :param asset_id: asset_id
    :param app_connector: Object of app_connector class
    :return: state: Current state file as a dictionary
    """

    asset_id = str(asset_id)
    if not asset_id or not asset_id.isalnum():
        debug_print_invalid_asset_id(app_connector)
        return {}

    app_dir = os.path.dirname(os.path.abspath(__file__))
    state_file = f"{app_dir}/{asset_id}_state.json"
    real_state_file_path = os.path.abspath(state_file)

    if os.path.dirname(real_state_file_path) != app_dir:
        debug_print_invalid_asset_id(app_connector)
        return {}

    state = {}
    try:
        with open(real_state_file_path) as state_file_obj:
            state = json.load(state_file_obj)
    except Exception as e:
        if app_connector:
            app_connector.debug_print(f"In _load_app_state: Exception: {e!s}")

    if app_connector:
        app_connector.debug_print("Loaded state: ", state)

    return state


def debug_print_invalid_asset_id(app_connector):
    if app_connector:
        app_connector.debug_print("Invalid asset_id")


def _get_dir_name_from_app_name(app_name):
    """Get name of the directory for the app.
    :param app_name: Name of the application for which directory name is required
    :return: app_name: Name of the directory for the application
    """

    app_name = "".join([x for x in app_name if x.isalnum()])
    app_name = app_name.lower()
    if not app_name:
        app_name = "app_for_phantom"
    return app_name


def _handle_login_redirect(request, key):
    """This function is used to redirect login request to microsoft login page.

    :param request: Data given to REST endpoint
    :param key: Key to search in state file
    :return: response authorization_url/admin_consent_url
    """

    asset_id = request.GET.get("asset_id")
    if not asset_id:
        return HttpResponseBadRequest(  # nosemgrep
            f"ERROR: Asset ID not found in URL, {request.GET}",
            content_type=consts.TEXT_PLAIN,
        )

    state = _load_app_state(asset_id)
    if not state:
        return HttpResponseBadRequest("ERROR: Invalid asset_id", content_type=consts.TEXT_PLAIN)

    url = state.get(key)
    if not url:
        return HttpResponseBadRequest(
            f"App state is invalid, {key} not found",
            content_type=consts.TEXT_PLAIN,
        )

    return HttpResponseRedirect(redirect_to=url)


def _handle_login_response(request):
    """This function is used to get the login response of authorization request from microsoft login page.

    :param request: Data given to REST endpoint
    :return: HttpResponse. The response displayed on authorization URL page
    """

    asset_id = request.GET.get("state")
    if not asset_id:
        return HttpResponseBadRequest(  # nosemgrep
            f"ERROR: Asset ID not found in URL, {request.GET}",
            content_type=consts.TEXT_PLAIN,
        )

    # Check for error in URL
    error = request.GET.get("error")
    error_description = request.GET.get("error_description")

    # If there is an error in response
    if error:
        message = f"Error: {error}"

        if error_description:
            message = f"{message} Details: {error_description}"

        return HttpResponseBadRequest(
            f"Server returned {message}",
            content_type=consts.TEXT_PLAIN,
        )

    code = request.GET.get("code")
    if not code:
        return HttpResponseBadRequest(
            f"Error while authenticating\n{json.dumps(request.GET)}",
            content_type=consts.TEXT_PLAIN,
        )

    state = _load_app_state(asset_id)
    try:
        state["code"] = AzureDevopsConnector().encrypt_state(code)
        state["is_encrypted"] = True
    except Exception as e:
        return HttpResponseBadRequest(
            f"{consts.AZURE_DEVOPS_DECRYPTION_ERROR}: {e!s}",
            content_type=consts.TEXT_PLAIN,
        )

    _save_app_state(state, asset_id, None)

    return HttpResponse(  # nosemgrep
        "Code received. Please close this window, the action will continue to get new token.",
        content_type=consts.TEXT_PLAIN,
    )


def _handle_rest_request(request, path_parts):
    """Handle requests for authorization.

    :param request: Data given to REST endpoint
    :param path_parts: parts of the URL passed
    :return: dictionary containing response parameters
    """

    if len(path_parts) < 2:
        return HttpResponseBadRequest(
            "error: True, message: Invalid REST endpoint request",
            content_type=consts.TEXT_PLAIN,
        )

    call_type = path_parts[1]

    # To handle admin_consent request in get_admin_consent action
    if call_type == "admin_consent":
        return _handle_login_redirect(request, "admin_consent_url")

    # To handle authorize request in test connectivity action
    if call_type == "start_oauth":
        return _handle_login_redirect(request, "app_authorization_url")

    # To handle response from microsoft login page
    if call_type == "result":
        return_val = _handle_login_response(request)

        asset_id = request.GET.get("state")  # nosemgrep
        if asset_id and asset_id.isalnum():
            app_dir = os.path.dirname(os.path.abspath(__file__))
            auth_status_file_path = f"{app_dir}/{asset_id}_{consts.TC_FILE}"
            real_auth_status_file_path = os.path.abspath(auth_status_file_path)

            if os.path.dirname(real_auth_status_file_path) != app_dir:
                return HttpResponseBadRequest(
                    "Error: Invalid asset_id",
                    content_type=consts.TEXT_PLAIN,
                )

            open(auth_status_file_path, "w").close()

            try:
                change_file_mode_and_permission(auth_status_file_path)
            except Exception:
                pass

        return return_val

    return HttpResponseNotFound("error: Invalid endpoint", content_type=consts.TEXT_PLAIN)


def change_file_mode_and_permission(auth_status_file_path):
    """changes the permission and mode of the file located at the given address.
    :param auth_status_file_path (string): file path
    """
    uid = pwd.getpwnam("apache").pw_uid
    gid = grp.getgrnam("phantom").gr_gid
    os.chown(auth_status_file_path, uid, gid)
    os.chmod(auth_status_file_path, consts.PERMISSION_CODE)


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class AzureDevopsConnector(BaseConnector):
    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

        self._state = None
        self._client_id = None
        self._client_secret = None
        self._access_token = None
        self._refresh_token = None
        self._asset_id = self.get_asset_id()
        self._base_url = None
        self._auth_type = None
        self._tenant_id = None

    def encrypt_state(self, encrypt_var):
        """Handle encryption of token.
        :param encrypt_var: Variable needs to be encrypted
        :return: encrypted variable
        """
        try:
            return encryption_helper.encrypt(encrypt_var, self._asset_id)
        except Exception:
            self.save_progress("Error in encrypting variable")

    def decrypt_state(self, decrypt_var):
        """Handle decryption of token.
        :param decrypt_var: Variable needs to be decrypted
        :return: decrypted variable
        """
        if self._state.get(consts.AZURE_DEVOPS_STATE_IS_ENCRYPTED):
            try:
                return encryption_helper.decrypt(decrypt_var, self._asset_id)
            except Exception:
                self.save_progress("Error in decrypting variable")
        else:
            return decrypt_var

    def _process_empty_response(self, response, action_result):
        # status_code 204 or 200 to handle empty response in case of a `DELETE` request
        if response.status_code in [200, 204]:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR, f"Empty response and no information in the header with status code {response.status_code}"
            ),
            None,
        )

    def _process_html_response(self, response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            for element in soup(["script", "style", "footer", "nav"]):
                element.extract()
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except Exception:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR,
                    f"Unable to parse JSON response. Error: {e!s}",
                ),
                None,
            )

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server. Status Code: {} Data from server: {}".format(r.status_code, r.text.replace("{", "{{").replace("}", "}}"))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            r.status_code, r.text.replace("{", "{{").replace("}", "}}")
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _get_token(self, action_result):
        """This function is used to get a token via REST Call.
        Supports both Azure DevOps OAuth (legacy) and Microsoft Entra ID OAuth.

        :param action_result: Object of action result
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        app_state = _load_app_state(self.get_asset_id(), self)

        # Determine which OAuth flow to use
        if self._auth_type == consts.AUTH_TYPE_INTERACTIVE_ENTRA:
            return self._get_token_entra_id(action_result, app_state)
        else:
            # Default to legacy Azure DevOps OAuth for backward compatibility
            return self._get_token_legacy(action_result, app_state)

    def _get_token_legacy(self, action_result, app_state):
        """Get token using legacy Azure DevOps OAuth."""
        self.save_progress("Acquiring access token using Azure DevOps OAuth...")

        data = {
            "client_assertion_type": consts.CLIENT_ASSERTION,
            "client_assertion": self._client_secret,
            "redirect_uri": self._state.get("redirect_uri"),
        }

        # If refresh_token is available, then use it to get new <access_token, refresh_token> pair
        # Else use code to get the same
        if self.get_action_identifier() != "test_connectivity" and self._refresh_token:
            data.update(
                {
                    "grant_type": consts.AZURE_DEVOPS_REFRESH_TOKEN_STRING,
                    "assertion": self._refresh_token,
                }
            )
        else:
            try:
                code = self.decrypt_state(app_state.get("code")) or None
            except Exception as e:
                self.error_print(f"{consts.AZURE_DEVOPS_DECRYPTION_ERROR}: {self._get_error_message_from_exception(e)}")
                return action_result.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_DECRYPTION_ERROR)

            data.update({"grant_type": consts.JWT_BEARER_TOKEN, "assertion": code})

        req_url = consts.TOKEN_URL
        headers = {"Content-Type": consts.FORM_URLENCODED}

        ret_val, resp_json = self._make_rest_call(
            req_url,
            action_result,
            data=data,
            method="post",
            headers=headers,
            skip_base_url=True,
        )

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        self.update_state_from_response(resp_json)
        self.save_progress("Access token generated successfully (Legacy OAuth)")

        return phantom.APP_SUCCESS

    def _get_token_entra_id(self, action_result, app_state):
        """Get token using Microsoft Entra ID OAuth."""
        self.save_progress("Acquiring access token using Microsoft Entra ID OAuth...")

        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "redirect_uri": self._state.get("redirect_uri"),
        }

        if self.get_action_identifier() != "test_connectivity" and self._refresh_token:
            data.update(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                    "scope": consts.AZURE_DEVOPS_DEFAULT_SCOPE,
                }
            )
        else:
            try:
                code = self.decrypt_state(app_state.get("code")) or None
            except Exception as e:
                self.error_print(f"{consts.AZURE_DEVOPS_DECRYPTION_ERROR}: {self._get_error_message_from_exception(e)}")
                return action_result.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_DECRYPTION_ERROR)

            data.update(
                {
                    "grant_type": "authorization_code",
                    "code": code,
                    "scope": consts.AZURE_DEVOPS_DEFAULT_SCOPE,
                }
            )

        req_url = consts.ENTRA_ID_TOKEN_URL.format(tenant_id=self._tenant_id)
        headers = {"Content-Type": consts.FORM_URLENCODED}

        ret_val, resp_json = self._make_rest_call(
            req_url,
            action_result,
            data=data,
            method="post",
            headers=headers,
            skip_base_url=True,
        )

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        self.update_state_from_response(resp_json)
        self.save_progress("Access token generated successfully (Entra ID OAuth)")

        return phantom.APP_SUCCESS

    def update_state_from_response(self, resp_json):
        """Utility function to update the state from response

        Args:
            resp_json (dict): response token data
        """
        self._access_token = resp_json[consts.AZURE_DEVOPS_ACCESS_TOKEN_STRING]
        self._refresh_token = resp_json.get(consts.AZURE_DEVOPS_REFRESH_TOKEN_STRING)
        self._state[consts.AZURE_DEVOPS_TOKEN_STRING] = resp_json

    def _get_request_headers(self):
        """Utility method that returns request headers.
        NOTE: always call this method after _get_token() method

        Returns:
            dict: request headers with access token
        """

        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "*/*",
            "Content-Type": consts.APPLICATION_JSON,
        }

    def _make_rest_call_helper(
        self,
        endpoint,
        action_result,
        verify=True,
        data=None,
        json=None,
        method="get",
        **kwargs,
    ):
        """Function that helps setting REST call to the app.
        :param endpoint: REST endpoint that needs to appended to the service address
        :param action_result: object of ActionResult class
        :param data: request body
        :param json: JSON object
        :param method: GET/POST/PUT/DELETE/PATCH (Default will be GET)
        :param verify: verify server certificate (Default True)
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        response obtained by making an API call
        """

        if not self._password:
            token = self._state.get("token", {})
            if consts.AZURE_DEVOPS_ACCESS_TOKEN_STRING not in token:
                ret_val = self._get_token(action_result)

                if phantom.is_fail(ret_val):
                    return action_result.get_status(), None
        headers = self._get_request_headers()
        params = {"api-version": self._api_version}
        skip_base_url = kwargs.get("skip_base_url", False)
        # if headers are already present, add them to headers dict
        if kwargs.get("headers"):
            headers.update(**kwargs.get("headers"))

        # if params are already present, add them to params dict
        if kwargs.get("params"):
            params.update(**kwargs.get("params"))

        ret_val, resp_json = self._make_rest_call(
            endpoint,
            action_result,
            method,
            verify=verify,
            headers=headers,
            params=urlparse.urlencode(params),
            data=data,
            json=json,
            skip_base_url=skip_base_url,
        )

        if consts.BAD_TOKEN_MATCH_STRING in action_result.get_message():
            self.save_progress("bad token")
            self._get_token(action_result=action_result)
            headers.update({"Authorization": f"Bearer {self._access_token}"})
            ret_val, resp_json = self._make_rest_call(
                endpoint,
                action_result,
                method,
                verify=verify,
                headers=headers,
                params=urlparse.urlencode(params),
                data=data,
                json=json,
                skip_base_url=skip_base_url,
            )

        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        return phantom.APP_SUCCESS, resp_json

    def _make_rest_call(self, endpoint, action_result, method="get", api_version=None, **kwargs):
        # **kwargs can be any additional parameters that requests.request accepts

        skip_base_url = kwargs.pop("skip_base_url", False)
        action_id = self.get_action_identifier()

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, f"Invalid method: {method}"),
                None,
            )

        # Create a URL to connect to
        if skip_base_url:
            url = endpoint
        else:
            base_url = self._get_base_url(action_id)
            if not base_url:
                return RetVal(
                    action_result.set_status(phantom.APP_ERROR, f"–on_id: {action_id}"),
                    None,
                )
            url = f"{base_url}{endpoint}"
        if api_version:
            kwargs["params"].update({"api-version": api_version})

        try:
            if self._auth_type == "Basic Auth":
                if not self._username or not self._password:
                    self.save_progress("Please provide username and access token for Basic Auth")
                    return phantom.APP_ERROR, None
                r = request_func(
                    url,
                    auth=(self._username, self._password),  # basic authentication
                    **kwargs,
                )
            else:
                if not self._client_id or not self._client_secret:
                    self.save_progress("Please provide Client ID or Client Secret for Interactive Auth")
                    return phantom.APP_ERROR, None
                r = request_func(
                    url,
                    **kwargs,
                )
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR,
                    f"Error Connecting to server. Details: {e!s}",
                ),
                None,
            )
        return self._process_response(r, action_result)

    def _get_asset_name(self, action_result):
        """Get name of the asset using Phantom URL.
        :param action_result: object of ActionResult class
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message), asset name
        """

        asset_id = self.get_asset_id()
        rest_endpoint = consts.AZURE_DEVOPS_PHANTOM_ASSET_INFO_URL.format(asset_id=asset_id)
        url = f"{consts.AZURE_DEVOPS_PHANTOM_BASE_URL.format(phantom_base_url=self._get_phantom_base_url())}{rest_endpoint}"
        ret_val, resp_json = self._make_rest_call(endpoint=url, action_result=action_result, verify=False, skip_base_url=True)  # nosemgrep

        if phantom.is_fail(ret_val):
            return ret_val, None

        asset_name = resp_json.get("name")
        if not asset_name:
            return (
                action_result.set_status(
                    phantom.APP_ERROR,
                    f"Asset Name for id: {asset_id} not found.",
                ),
                None,
            )
        return phantom.APP_SUCCESS, asset_name

    def _get_phantom_base_url_vmazure(self, action_result):
        """Get base url of phantom.
        :param action_result: object of ActionResult class
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        base url of phantom
        """

        url = f"{consts.AZURE_DEVOPS_PHANTOM_BASE_URL.format(phantom_base_url=self._get_phantom_base_url())}{consts.AZURE_DEVOPS_PHANTOM_SYS_INFO_URL}"

        ret_val, resp_json = self._make_rest_call(endpoint=url, action_result=action_result, verify=False, skip_base_url=True)  # nosemgrep

        if phantom.is_fail(ret_val):
            return ret_val, None

        phantom_base_url = resp_json.get("base_url").rstrip("/")
        if not phantom_base_url:
            return (
                action_result.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_BASE_URL_NOT_FOUND_MESSAGE),
                None,
            )
        return phantom.APP_SUCCESS, phantom_base_url

    def _get_app_rest_url(self, action_result):
        """Get URL for making rest calls.
        :param action_result: object of ActionResult class
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        URL to make rest calls
        """

        ret_val, phantom_base_url = self._get_phantom_base_url_vmazure(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        ret_val, asset_name = self._get_asset_name(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        self.save_progress(f"Using Phantom base URL: {phantom_base_url}")

        app_json = self.get_app_json()
        app_name = app_json["name"]

        app_dir_name = _get_dir_name_from_app_name(app_name)
        url_to_app_rest = "{}/rest/handler/{}_{}/{}".format(phantom_base_url, app_dir_name, app_json["appid"], asset_name)
        return phantom.APP_SUCCESS, url_to_app_rest

    def _handle_test_connectivity(self, param: dict):
        # Add an action result object to self (BaseConnector) to represent the action for this param
        # Progress
        # self.save_progress("Generating Authentication URL")
        app_state = {}
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Validate configuration for Entra ID authentication
        if self._auth_type == consts.AUTH_TYPE_INTERACTIVE_ENTRA:
            if not self._tenant_id:
                self.save_progress("Tenant ID is required for Entra ID authentication")
                return action_result.set_status(phantom.APP_ERROR, "Tenant ID is required when using Interactive Auth (Entra ID)")

        if self._auth_type == consts.AUTH_TYPE_BASIC:
            # NOTE: test connectivity does _NOT_ take any parameters
            # i.e. the param dictionary passed to this handler will be empty.
            # Also typically it does not add any data into an action_result either.
            # The status and progress messages are more important.

            self.save_progress("Connecting to endpoint")
            # make rest call
            ret_val, response = self._make_rest_call(consts.ITERATIONS, action_result, params=None, headers=None)

            if phantom.is_fail(ret_val):
                # the call to the 3rd party device or service failed, action result should contain all the error details
                # for now the return is commented out, but after implementation, return from here
                self.save_progress("Test Connectivity Failed.")
                return action_result.get_status()

            # Return success
            self.save_progress("Test Connectivity Passed")
            return action_result.set_status(phantom.APP_SUCCESS)

        self.save_progress("Getting App REST endpoint URL")

        ret_val, app_rest_url = self._get_app_rest_url(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress(consts.AZURE_DEVOPS_REST_URL_NOT_AVAILABLE_MESSAGE.format(error=action_result.get_status()))
            return action_result.set_status(phantom.APP_ERROR)

        # create the url that the oauth server should re-direct to after the auth is completed
        # (success and failure), this is added to the state so that the request handler will access
        # it later on
        redirect_uri = f"{app_rest_url}/result"
        app_state["redirect_uri"] = redirect_uri

        self.save_progress(consts.AZURE_DEVOPS_OAUTH_URL_MESSAGE)
        self.save_progress(redirect_uri)

        # Generate authorization URL based on auth type
        if self._auth_type == consts.AUTH_TYPE_INTERACTIVE_ENTRA:
            if not self._tenant_id:
                self.save_progress("Tenant ID is required for Entra ID authentication")
                return action_result.set_status(phantom.APP_ERROR, "Tenant ID is required for Entra ID authentication")

            self.save_progress("Using Microsoft Entra ID OAuth authentication")
            app_authorization_base_url = consts.ENTRA_ID_AUTHORIZATION_URL.format(tenant_id=self._tenant_id)

            app_authorization_url = (
                "{base_url}?client_id={client_id}&state={state}&response_type={response_type}&scope={scope}&redirect_uri={redirect_uri}".format(
                    base_url=app_authorization_base_url,
                    client_id=self._client_id,
                    state=self.get_asset_id(),
                    response_type="code",
                    scope=consts.AZURE_DEVOPS_DEFAULT_SCOPE,
                    redirect_uri=redirect_uri,
                )
            )
        else:
            # Default to legacy Azure DevOps OAuth for backward compatibility
            # Show deprecation warning for legacy OAuth
            if self._auth_type in [consts.AUTH_TYPE_INTERACTIVE_LEGACY, consts.AUTH_TYPE_INTERACTIVE_OLD]:
                self.save_progress("WARNING: Using legacy Azure DevOps OAuth (deprecated in 2026)")
                self.save_progress("Consider migrating to Interactive Auth (Entra ID) for new integrations")

            self.save_progress("Using Azure DevOps OAuth authentication (legacy)")
            app_authorization_base_url = consts.AUTHORIZATION_URL

            app_authorization_url = (
                "{base_url}?client_id={client_id}&state={state}&response_type={response_type}&scope={scope}&redirect_uri={redirect_uri}".format(
                    base_url=app_authorization_base_url,
                    client_id=self._client_id,
                    state=self.get_asset_id(),
                    response_type="Assertion",
                    scope=consts.AZURE_DEVOPS_CODE_GENERATION_SCOPE,
                    redirect_uri=redirect_uri,
                )
            )

        app_state["app_authorization_url"] = app_authorization_url

        # The URL that the user should open in a different tab.
        # This is pointing to a REST endpoint that points to the app
        url_to_show = f"{app_rest_url}/start_oauth?asset_id={self.get_asset_id()}&"

        # Save the state, will be used by the request handler
        _save_app_state(app_state, self.get_asset_id(), self)

        self.save_progress("==" * 40)
        self.save_progress("\nPlease connect to the following Url from a different tab to continue the connectivity process...\n")
        self.save_progress(url_to_show)
        self.save_progress("==" * 40)

        time.sleep(5)

        app_dir = os.path.dirname(os.path.abspath(__file__))
        auth_status_file_path = f"{app_dir}/{self.get_asset_id()}_{consts.TC_FILE}"

        self.save_progress("Waiting for authorization to complete...")

        completed = self.check_authorization(auth_status_file_path)

        if not completed:
            self.save_progress("The authentication process does not seem to be completed, timing out...")
            return action_result.set_status(phantom.APP_ERROR)

        # Load the state again, since the http request handlers would have saved the result of the app authorization
        self._state = _load_app_state(self.get_asset_id(), self)
        if not self._state:
            self.save_progress("Authorization not received")
            self.save_progress("Test Connectivity Failed")
            return action_result.set_status(phantom.APP_ERROR)

        self.save_progress(consts.AZURE_DEVOPS_GENERATING_ACCESS_TOKEN_MESSAGE)
        ret_val = self._get_token(action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        ret_val, response = self._make_rest_call_helper(
            endpoint=consts.ITERATIONS,
            action_result=action_result,
        )

        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed")
            return action_result.get_status()

        self.save_progress("Test Connectivity Passed")
        action_result.add_data(response)
        return action_result.set_status(phantom.APP_SUCCESS)

    def check_authorization(self, auth_status_file_path):
        """method that check for auth file creation
        :param auth_status_file_path (str): auth file path string
        :return: bool: True if file is found, else False
        """
        completed = False
        for i in range(0, 40):
            self.send_progress("{}".format("." * (i % 10)))

            if os.path.isfile(auth_status_file_path):
                completed = True
                os.unlink(auth_status_file_path)
                break

            time.sleep(consts.AZURE_DEVOPS_TC_STATUS_SLEEP)
        return completed

    def _handle_get_work_item(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        work_item_id = param["work_item_id"]
        expand = param["expand"]

        asof = param.get("asof")
        fields = param.get("fields")

        params = {"$expand": expand}
        if asof:
            params["asOf"] = asof
        if fields:
            params["fields"] = fields

        ret_val, response = self._make_rest_call_helper(
            f"{consts.WORK_ITEMS}/{work_item_id}",
            action_result,
            params=params,
        )

        if phantom.is_fail(ret_val):
            return action_result.get_status()
        temp_fields = {}
        for key, val in response.get("fields").items():
            temp_key = key.replace(".", "-")
            temp_fields[temp_key] = val
        response["fields"] = temp_fields
        action_result.add_data(response)

        summary = action_result.update_summary({})
        summary["status"] = f"Work item {work_item_id} retrieved successfully"

        self.debug_print(f"Work item {work_item_id} retrieved successfully")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_add_work_item(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        work_item_type = param["work_item_type"]

        params = self.get_work_item_optional_params(param)

        headers = {"Content-Type": consts.APPLICATION_JSON_PATCH_HEADER}

        try:
            post_body_json = json.loads(param["post_body"], strict=False)
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, "Failed to parse JSON")

        # make rest call
        ret_val, response = self._make_rest_call_helper(
            f"{consts.WORK_ITEMS}/${work_item_type}",
            action_result,
            method="post",
            data=json.dumps(post_body_json),
            params=params,
            headers=headers,
        )

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        temp_fields = {}
        for key, val in response.get("fields").items():
            temp_key = key.replace(".", "-")
            temp_fields[temp_key] = val
        response["fields"] = temp_fields
        action_result.add_data(response)

        summary = action_result.update_summary({})
        summary["status"] = "Work item added successfully"

        self.debug_print("Work item added successfully")

        return action_result.set_status(phantom.APP_SUCCESS)

    def get_work_item_optional_params(self, param: dict):
        expand = param.get("expand")
        bypass_rules = param.get("bypass_rules")
        suppress_notifications = param.get("suppress_notifications")
        validate_only = param.get("validate_only")

        params = {"$expand": expand}
        if bypass_rules:
            params["bypassRules"] = bypass_rules
        if suppress_notifications:
            params["suppressNotifications"] = suppress_notifications
        if validate_only:
            params["validateOnly"] = validate_only
        return params

    def _handle_list_iterations(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        team = param.get("team")
        time_frame = param.get("timeframe")

        if time_frame:
            params = {"$timeframe": time_frame}
        else:
            params = {}

        if team:
            endpoint = consts.ITERATIONS_TEAM.format(team=team)
        else:
            endpoint = consts.ITERATIONS

        ret_val, response = self._make_rest_call_helper(endpoint, action_result, method="get", params=params)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(response)

        summary = action_result.update_summary({})
        try:
            summary["total_iterations"] = action_result.get_data()[0]["count"]
        except Exception:
            self.save_progress("Iteration not found")
            return action_result.set_status(phantom.APP_ERROR)

        self.debug_print("Data retrieved successfully")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_add_comment(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        work_item_id = param["work_item_id"]
        comment = param["comment"]

        post_body = {"text": comment}
        params = {"api-version": "7.1-preview.3"}

        self.save_progress("Adding comment")
        # make rest call
        ret_val, response = self._make_rest_call_helper(
            consts.COMMENTS.format(work_item_id), action_result, method="post", data=json.dumps(post_body), params=params
        )

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        summary = action_result.update_summary({})
        summary["status"] = "Comment added successfully"

        self.debug_print("Comment added successfully")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_search_users(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        search_filter = param.get("filter", None)
        if search_filter:
            param["$filter"] = search_filter

        user_data = {"members": list(), "items": list()}

        ret_val, response = self._make_rest_call_helper(
            consts.USER_ENTITLEMENTS,
            action_result,
            method="get",
            params=param,
        )

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        user_data["members"].extend(response.get("members", []))
        user_data["items"].extend(response.get("items", []))

        while True:
            continuation_token = response.get("continuationToken", None)
            if not continuation_token:
                break
            else:
                param["continuationToken"] = continuation_token
                ret_val, response = self._make_rest_call_helper(
                    consts.USER_ENTITLEMENTS,
                    action_result,
                    method="get",
                    params=param,
                )

                if phantom.is_fail(ret_val):
                    return action_result.get_status()

                user_data["members"].extend(response.get("members", []))
                user_data["items"].extend(response.get("items", []))

        action_result.add_data(user_data)

        try:
            summary = action_result.update_summary({})
            summary["total_users"] = len(action_result.get_data()[0]["items"])
        except Exception:
            self.save_progress("Items not found")
            summary["total_users"] = 0
            return action_result.set_status(phantom.APP_SUCCESS, "Items not found")

        self.debug_print("Data retrieved successfully")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_delete_user(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        user_id = param["user_id"]

        ret_val, resp = self._make_rest_call_helper(
            f"{consts.USER_ENTITLEMENTS}/{user_id}",
            action_result,
            method="delete",
        )

        if "Status Code: 404" in action_result.get_message():
            return RetVal(action_result.set_status(phantom.APP_ERROR, "User with given id not found"), None)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "User has been deleted successfully")

    def _handle_add_user(self, param: dict):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))
        ret_val, response = self._make_rest_call_helper(
            consts.GET_PROJECT_LIST_URL.format(organization=self._organization),
            action_result,
            method="get",
            skip_base_url=True,
        )
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        user_email = param["user_email"]
        account_license_type = param["account_license_type"]
        group_type = param["group_type"]
        project_name = param["project_name"]

        project_id = None
        for project in response.get("value", []):
            if project_name.lower() == project["name"].lower():
                project_id = project["id"]
                break

        if project_id is None:
            return action_result.set_status(phantom.APP_ERROR, "No project found with given project name")

        data = {
            "accessLevel": {"accountLicenseType": account_license_type},
            "user": {"principalName": user_email, "subjectKind": "user"},
            "projectEntitlements": [
                {
                    "group": {"groupType": group_type},
                    "projectRef": {"id": project_id},
                }
            ],
        }

        # make the rest call
        ret_val, response = self._make_rest_call_helper(
            consts.USER_ENTITLEMENTS,
            action_result,
            json=data,
            method="post",
        )
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        if not bool(response.get("operationResult", {}).get("isSuccess", True)):
            return action_result.set_status(phantom.APP_ERROR, "Could not create a user")

        action_result.add_data(response)

        self.debug_print("User has been added successfully")

        return action_result.set_status(phantom.APP_SUCCESS, "User with given data added successfully")

    def _get_error_message_from_exception(self, e):
        """This function is used to get appropriate error message from the exception.
        :param e: Exception object
        :return: error message
        """
        error_code = None
        error_message = consts.AZURE_DEVOPS_ERROR_MESSAGE_UNAVAILABLE

        self.error_print("Error occurred: ", e)

        try:
            if hasattr(e, "args"):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_message = e.args[1]
                elif len(e.args) == 1:
                    error_message = e.args[0]
        except Exception as e:
            self.error_print(f"Error occurred while getting message from exception. Error: {e}")

        if not error_code:
            error_text = f"Error Message: {error_message}"
        else:
            error_text = f"Error Code: {error_code}. Error Message: {error_message}"

        return error_text

    def _get_base_url(self, action_id):
        """Utility method to get the base url for a given action.
        :param action_id (str): action identifier
        :return str: base url string
        """
        action_to_url_mapping_dict = {
            "delete_user": self._user_entitlement_base_url,
            "search_users": self._user_entitlement_base_url,
            "add_user": self._user_entitlement_base_url,
            "get_work_item": self._base_url,
            "add_work_item": self._base_url,
            "list_iterations": self._base_url,
            "add_comment": self._base_url,
            "test_connectivity": self._base_url,
            "add_attachment": self._base_url,
        }

        return action_to_url_mapping_dict.get(action_id, None)

    def _handle_add_attachment(self, param):
        # Implement the handler here
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary

        # Required values can be accessed directly
        vault_id = param["vault_id"]
        filename = param["filename"]

        try:
            success, msg, vault_info = phantom_rules.vault_info(vault_id=vault_id)
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, "Error occurred while fetching the vault information of the specified Vault ID")

        if not vault_info:
            try:
                error_msg = f"Error occurred while fetching the vault information of the Vault ID: {vault_id}"
            except Exception:
                error_msg = "Error occurred while fetching the vault information of the specified Vault ID"

            return action_result.set_status(phantom.APP_ERROR, error_msg)

        # Loop through the Vault information
        for item in vault_info:
            vault_path = item.get("path")
            if vault_path is None:
                return action_result.set_status(phantom.APP_ERROR, "Could not find a path associated with the provided Vault ID")
            try:
                # Open the file
                vault_file = open(vault_path, "rb").read()
                # Create the files data to send to the console
            except Exception as e:
                error_message = self._get_error_message_from_exception(e)
                return action_result.set_status(phantom.APP_ERROR, f"Unable to open vault file: {error_message}")

        headers = self._get_request_headers()
        headers.update(headers)
        headers["Content-Type"] = consts.OCTANT_HEADER_STRING

        params = {"fileName": filename}

        # Optional values should use the .get() function
        # optional_parameter = param.get('optional_parameter', 'default_value')

        # make rest call
        ret_val, response = self._make_rest_call(
            "/_apis/wit/attachments",
            action_result,
            headers=headers,
            method="post",
            params=params,
            data=vault_file,
            api_version=param["api_version"],
        )

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            # for now the return is commented out, but after implementation, return from here
            return action_result.get_status()
            # pass

        # Now post process the data,  uncomment code as you deem fit

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        # summary = action_result.update_summary({})
        # summary['num_data'] = len(action_result['data'])

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Successfully added the attachment")

        # For now return Error with a message, in case of success we don't set the message, but use the summary
        # return action_result.set_status(phantom.APP_ERROR, "Action not yet implemented")

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == "get_work_item":
            ret_val = self._handle_get_work_item(param)

        if action_id == "add_work_item":
            ret_val = self._handle_add_work_item(param)

        if action_id == "list_iterations":
            ret_val = self._handle_list_iterations(param)

        if action_id == "add_comment":
            ret_val = self._handle_add_comment(param)

        if action_id == "search_users":
            ret_val = self._handle_search_users(param)

        if action_id == "delete_user":
            ret_val = self._handle_delete_user(param)

        if action_id == "add_user":
            ret_val = self._handle_add_user(param)

        if action_id == "add_attachment":
            ret_val = self._handle_add_attachment(param)

        if action_id == "test_connectivity":
            ret_val = self._handle_test_connectivity(param)

        return ret_val

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        if not isinstance(self._state, dict):
            self.debug_print("Resetting the state file with the default format")
            self._state = {"app_version": self.get_app_json().get("app_version")}
            return self.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_STATE_FILE_CORRUPT_ERROR)

        # get the asset config
        config = self.get_config()

        self._organization = config["organization"]
        self._project = config["project"]
        self._api_version = config["api version"]
        self._client_id = config.get("client_id", None)
        self._client_secret = config.get("client_secret", None)
        self._username = config.get("username", None)
        self._password = config.get("access token", None)
        self._auth_type = config.get("auth_type")
        self._tenant_id = config.get("tenant_id", None)
        self._base_url = consts.PROJECT_BASE_URL.format(organization=self._organization, project=self._project)
        self._user_entitlement_base_url = consts.USER_ENTITLEMENT_URL.format(organization=self._organization)

        self._access_token = self._state.get(consts.AZURE_DEVOPS_TOKEN_STRING, {}).get(consts.AZURE_DEVOPS_ACCESS_TOKEN_STRING, None)
        if self._state.get(consts.AZURE_DEVOPS_STATE_IS_ENCRYPTED) and self._access_token:
            try:
                self._access_token = self.decrypt_state(self._access_token)
            except Exception as e:
                self.error_print(f"{consts.AZURE_DEVOPS_DECRYPTION_ERROR}: {self._get_error_message_from_exception(e)}")
                return self.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_DECRYPTION_ERROR)

        self._refresh_token = self._state.get(consts.AZURE_DEVOPS_TOKEN_STRING, {}).get(consts.AZURE_DEVOPS_REFRESH_TOKEN_STRING, None)
        if self._state.get(consts.AZURE_DEVOPS_STATE_IS_ENCRYPTED) and self._refresh_token:
            try:
                self._refresh_token = self.decrypt_state(self._refresh_token)
            except Exception as e:
                self.error_print(f"{consts.AZURE_DEVOPS_DECRYPTION_ERROR}: {self._get_error_message_from_exception(e)}")
                return self.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_DECRYPTION_ERROR)

        return phantom.APP_SUCCESS

    def finalize(self):
        try:
            if self._access_token:
                if consts.AZURE_DEVOPS_TOKEN_STRING not in self._state:
                    self._state[consts.AZURE_DEVOPS_TOKEN_STRING] = {}

                self._state[consts.AZURE_DEVOPS_TOKEN_STRING][consts.AZURE_DEVOPS_ACCESS_TOKEN_STRING] = self.encrypt_state(self._access_token)

                # Only encrypt refresh token if it exists (not always present)
                if self._refresh_token:
                    self._state[consts.AZURE_DEVOPS_TOKEN_STRING][consts.AZURE_DEVOPS_REFRESH_TOKEN_STRING] = self.encrypt_state(
                        self._refresh_token
                    )

                if self._state.get("code"):
                    self._state["code"] = self.encrypt_state(self._state["code"])
        except Exception as e:
            self.error_print(f"{consts.AZURE_DEVOPS_ENCRYPTION_ERROR}: {self._get_error_message_from_exception(e)}")
            return self.set_status(phantom.APP_ERROR, consts.AZURE_DEVOPS_ENCRYPTION_ERROR)

        # Save the state, this data is saved across actions and app upgrades
        self._state[consts.AZURE_DEVOPS_STATE_IS_ENCRYPTED] = True
        self.save_state(self._state)
        _save_app_state(self._state, self.get_asset_id(), self)
        return phantom.APP_SUCCESS


def main():
    import argparse

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)
    argparser.add_argument(
        "-v",
        "--verify",
        action="store_true",
        help="verify",
        required=False,
        default=False,
    )

    args = argparser.parse_args()
    session_id = None
    verify = args.verify

    username = args.username
    password = args.password

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = AzureDevopsConnector._get_phantom_base_url() + "/login"

            print("Accessing the Login page")
            r = requests.get(login_url, verify=verify, timeout=30)
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=verify, data=data, headers=headers, timeout=30)
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            sys.exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = AzureDevopsConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            connector._set_csrf_info(csrftoken, headers["Referer"])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)


if __name__ == "__main__":
    main()
