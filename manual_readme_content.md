[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2022-2024 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
## Interactive Auth

This app requires creating an app on Microsoft Azure Application. To register your app, navigate to
<https://app.vsaex.visualstudio.com/app/register> in a browser and log in with a Microsoft account.

1.  ### Register your app

      

    -   Go to <https://app.vsaex.visualstudio.com/app/register> to register your app.

        Add the Application website which will be under the "POST incoming for Azure DevOps to this
        location" field of your Splunk-SOAR asset. It would look like :  
        https://{soar_instance}/rest/handler/{app_name}\_{app_id}/{asset_name}  
        Authorisation URL would look like :  
        https://{soar_instance}/rest/handler/{app_name}\_{app_id}/{asset_name}/result

    -   Select the following scopes while registering your app:  
        vso.entitlements  
        vso.memberentitlementmanagement_write  
        vso.work_full  
        Use the same scopes when you authorize your app. If you registered your app using the
        preview APIs, re-register because the scopes that you used are now deprecated.

    -   Select **Create Application**

2.  ### Authorize your app

    Call the authorization URL and pass your app ID and authorized scopes when you want to have a
    user authorize your app to access their organization. Call the access token URL when you want to
    get an access token to call an Azure DevOps Services REST API.

    -   If your user hasn't yet authorized your app to access their organization, call the
        authorization URL. It calls you back with an authorization code, if the user approves the
        authorization.

          

        > https://app.vssps.visualstudio.com/oauth2/authorize  
        > ?client_id={app ID}  
        > &response_type={Assertion}  
        > &state={state}  
        > &scope={scope}  
        > &redirect_uri={callback URL}

    | Parameter     | Type   | Notes                                                                                                                        |
    |---------------|--------|------------------------------------------------------------------------------------------------------------------------------|
    | client_id     | GUID   | The ID assigned to your app when it was registered.                                                                          |
    | response_type | string | Assertion                                                                                                                    |
    | state         | string | Can be any value. Typically a generated string value that correlates the callback with its associated authorization request. |
    | scope         | string | Scopes registered with the app. Space-separated.                                                                             |
    | redirect_uri  | URL    | Callback URL for your app. Must exactly match the URL registered with the app.                                               |

3.  Assuming the user accepts, Azure DevOps Services redirects the user's browser to your callback
    URL, including a short-lived authorization code and the state value provided in the
    authorization URL:

    > https://fabrikam.azurewebsites.net/myapp/oauth-callback  
    > ?code={authorization code}  
    > &state=User1

    ## Configure the Azure Devops Splunk SOAR app Asset

    When creating an asset for the **Azure Devops** app, go to asset settings and place the
    **Application ID** of the app created during the previous step in the **Client ID** field and
    place the Client Secret generated during the previous step in the **Client Secret** field. Then,
    after filling out the **The name of the Azure DevOps organization** and **Project name** fields
    , click **SAVE** .  
      
    After saving, a new field will appear in the **Asset Settings** tab. Take the URL found in the
    **POST incoming for Azure DevOps to this location** field and place it in the **Application
    website** field mentioned in a previous step. Add the same url to the **Authorization callback
    URL** and add **/result** to ths URL. After doing so the URL should look something like:  
      

    https://\<soar_host>/rest/handler/azureadgraph_c6d3b801-5c26-4abd-9e89-6d8007e2778f/\<asset_name>/result

      
    Once again, click on Save.

    ## Method to Run Test Connectivity

    After setting up the asset and user, click the **TEST CONNECTIVITY** button. A window should pop
    up and display a URL. Navigate to this URL in a separate browser tab. This new tab will redirect
    to a Microsoft login page. Log in to a Microsoft account with administrator privileges to the
    Azure Devops environment. After logging in, review the requested permissions listed, then click
    **Accept** . Finally, close that tab. The test connectivity window should show a success.  
      
    The app should now be ready to use.  
      
    If username and password is entered than priority will be given to the basic auth then
    Interactive Auth.  
      
    We have tested all action for the api version 7.0 but it might be supported in other versions as
    well.

    ## State File Permissions

    Please check the permissions for the state file as mentioned below.

    #### State Filepath

    -   For Non-NRI Instance:
        /opt/phantom/local_data/app_states/c6d3b801-5c26-4abd-9e89-6d8007e2778f/{asset_id}\_state.json
    -   For NRI Instance:
        /\<PHANTOM_HOME_DIRECTORY>/local_data/app_states/c6d3b801-5c26-4abd-9e89-6d8007e2778f/{asset_id}\_state.json

    #### State File Permissions

    -   File Rights: rw-rw-r-- (664) (The phantom user should have read and write access for the
        state file)
    -   File Owner: appropriate phantom user

    ## Port Information

    The app uses HTTP/ HTTPS protocol for communicating with the Azure AD server. Below are the
    default ports used by Splunk SOAR.

    |         Service Name | Transport Protocol | Port |
    |----------------------|--------------------|------|
    |         http         | tcp                | 80   |
    |         https        | tcp                | 443  |

    ## Basic Authentication

    This app requires two params for the basic authentication which is username and access
    token(password). username will be email id. To generate the access token follow
    [this](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows#create-a-pat)
    steps and select Entitlements - Read (vso.entitlements), User Profile -
    Read&Write(vso.memberentitlementmanagement_write) and work item - Read&Write(vso.work_full)
    scopes.
