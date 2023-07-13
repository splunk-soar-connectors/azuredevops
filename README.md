[comment]: # "Auto-generated SOAR connector documentation"
# Azure DevOps

Publisher: Splunk  
Connector Version: 2.0.0  
Product Vendor: Microsoft  
Product Name: Azure DevOps  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 6.0.0  

This app integrates with Azure DevOps to perform investigative and generic actions

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2022-2023 Splunk Inc."
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


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Azure DevOps asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**organization** |  required  | string | The name of the Azure DevOps organization
**project** |  required  | string | Project name
**api version** |  required  | string | Version of the API to use
**auth_type** |  required  | string | Auth Type
**username** |  optional  | string | User name (Basic Auth)
**access token** |  optional  | password | Access token (Basic Auth)
**client_id** |  optional  | string | Client ID (Interactive Auth)
**client_secret** |  optional  | password | Client Secret (Interactive Auth)

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[get work item](#action-get-work-item) - Get information about a single work item  
[add work item](#action-add-work-item) - Creates a single work item  
[list iterations](#action-list-iterations) - Get team's iteration  
[add comment](#action-add-comment) - Add a comment on a work item  
[add user](#action-add-user) - Add a user to a project  
[delete user](#action-delete-user) - Delete a user  
[search users](#action-search-users) - Search user(s)  
[add attachment](#action-add-attachment) - Add an attachment to a project  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'get work item'
Get information about a single work item

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**work_item_id** |  required  | The work item id | numeric |  `work item id` 
**expand** |  required  | The expand parameters for work item attributes (Possible options are { None, Relations, Fields, Links, All }) | string | 
**asof** |  optional  | AsOf UTC date time string | string | 
**fields** |  optional  | Comma-separated list of requested fields | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.asof | string |  |  
action_result.parameter.expand | string |  |  
action_result.parameter.fields | string |  |  
action_result.parameter.work_item_id | numeric |  `work item id`  |   123 
action_result.data | string |  |  
action_result.data.\*._links.fields.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/fields 
action_result.data.\*._links.html.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_workitems/edit/1 
action_result.data.\*._links.self.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1 
action_result.data.\*._links.workItemComments.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1/comments 
action_result.data.\*._links.workItemRevisions.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1/revisions 
action_result.data.\*._links.workItemType.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItemTypes/Epic 
action_result.data.\*._links.workItemUpdates.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1/updates 
action_result.data.\*.commentVersionRef.commentId | numeric |  |   1985876 
action_result.data.\*.commentVersionRef.url | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1/comments/1985876/versions/1 
action_result.data.\*.commentVersionRef.version | numeric |  |   1 
action_result.data.\*.fields.Microsoft.VSTS.Common.Priority | numeric |  |   1 
action_result.data.\*.fields.Microsoft.VSTS.Common.StateChangeDate | string |  |   2023-01-02T11:53:05.303Z 
action_result.data.\*.fields.System-AreaPath | string |  |   test 
action_result.data.\*.fields.System-ChangedBy._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-ChangedBy.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-ChangedBy.displayName | string |  |   test Edwards 
action_result.data.\*.fields.System-ChangedBy.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-ChangedBy.imageUrl | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-ChangedBy.uniqueName | string |  |   test@test.com 
action_result.data.\*.fields.System-ChangedBy.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-ChangedDate | string |  |   2023-02-07T08:33:56.447Z 
action_result.data.\*.fields.System-CommentCount | numeric |  |   5 
action_result.data.\*.fields.System-CreatedBy._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-CreatedBy.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-CreatedBy.displayName | string |  |   test Edwards 
action_result.data.\*.fields.System-CreatedBy.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-CreatedBy.imageUrl | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-CreatedBy.uniqueName | string |  |   test@test.com 
action_result.data.\*.fields.System-CreatedBy.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-CreatedDate | string |  |   2023-01-02T11:53:05.303Z 
action_result.data.\*.fields.System-Description | string |  |   <div>Test description </div> 
action_result.data.\*.fields.System-History | string |  |   test 
action_result.data.\*.fields.System-IterationPath | string |  |   test 
action_result.data.\*.fields.System-Reason | string |  |   Added to backlog 
action_result.data.\*.fields.System-State | string |  |   To Do 
action_result.data.\*.fields.System-TeamProject | string |  |   test 
action_result.data.\*.fields.System-Title | string |  |   Test Epic Title 
action_result.data.\*.fields.System-WorkItemType | string |  |   Epic 
action_result.data.\*.id | numeric |  |   1 
action_result.data.\*.relations.\*.attributes.isLocked | boolean |  |   True  False 
action_result.data.\*.relations.\*.attributes.name | string |  |   Child 
action_result.data.\*.relations.\*.rel | string |  |   System.LinkTypes.Hierarchy-Forward 
action_result.data.\*.relations.\*.url | string |  |   https://dev.azure.com/abc/c24261f4-hkufh-kfhgi-2fcc3da9/_apis/wit/workItems/59 
action_result.data.\*.rev | numeric |  |   6 
action_result.data.\*.url | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1 
action_result.summary | string |  |  
action_result.summary.status | string |  |   Work item {work_item_id} retrieved successfully 
action_result.message | string |  |   Status: Work item added successfully 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add work item'
Creates a single work item

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**work_item_type** |  required  | The work item type of the work item to create | string | 
**post_body** |  required  | Payload to be sent to be created | string | 
**expand** |  optional  | The expand parameters for work item attributes (Possible options are { None, Relations, Fields, Links, All }) | string | 
**bypass_rules** |  optional  | Do not enforce the work item type rules on this update | boolean | 
**suppress_notifications** |  optional  | Do not fire any notifications for this change | boolean | 
**validate_only** |  optional  | Indicate if you only want to validate the changes without saving the work item | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.bypass_rules | boolean |  |   True  False 
action_result.parameter.expand | string |  |  
action_result.parameter.post_body | string |  |  
action_result.parameter.suppress_notifications | boolean |  |   True  False 
action_result.parameter.validate_only | boolean |  |   True  False 
action_result.parameter.work_item_type | string |  |  
action_result.data | string |  |  
action_result.data.\*._links.fields.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/fields 
action_result.data.\*._links.html.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_workitems/edit/9 
action_result.data.\*._links.self.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/9 
action_result.data.\*._links.workItemComments.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/9/comments 
action_result.data.\*._links.workItemRevisions.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/9/revisions 
action_result.data.\*._links.workItemType.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItemTypes/Epic 
action_result.data.\*._links.workItemUpdates.href | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/9/updates 
action_result.data.\*.fields.Microsoft.VSTS.Common.Priority | numeric |  |   2 
action_result.data.\*.fields.Microsoft.VSTS.Common.StateChangeDate | string |  |   2023-02-07T08:34:37.39Z 
action_result.data.\*.fields.System-AreaId | numeric |  |   4 
action_result.data.\*.fields.System-AreaLevel1 | string |  |   test 
action_result.data.\*.fields.System-AreaPath | string |  |   test 
action_result.data.\*.fields.System-AuthorizedAs._links.avatar.href | string |  |   https://dev.azure.com/herman0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-AuthorizedAs.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-AuthorizedAs.displayName | string |  |   ABC XYZ 
action_result.data.\*.fields.System-AuthorizedAs.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-AuthorizedAs.imageUrl | string |  |   https://dev.azure.com/abc/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-AuthorizedAs.uniqueName | string |  |   test@test.com 
action_result.data.\*.fields.System-AuthorizedAs.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-AuthorizedDate | string |  |   2023-04-14T12:33:31.437Z 
action_result.data.\*.fields.System-ChangedBy._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-ChangedBy.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-ChangedBy.displayName | string |  |   test Edwards 
action_result.data.\*.fields.System-ChangedBy.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-ChangedBy.imageUrl | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-ChangedBy.uniqueName | string |  |   test@test.com 
action_result.data.\*.fields.System-ChangedBy.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-ChangedDate | string |  |   2023-02-07T08:34:37.39Z 
action_result.data.\*.fields.System-CommentCount | numeric |  |  
action_result.data.\*.fields.System-CreatedBy._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-CreatedBy.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-CreatedBy.displayName | string |  |   test Edwards 
action_result.data.\*.fields.System-CreatedBy.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-CreatedBy.imageUrl | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.fields.System-CreatedBy.uniqueName | string |  |   test@test.comment 
action_result.data.\*.fields.System-CreatedBy.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.fields.System-CreatedDate | string |  |   2023-02-07T08:34:37.39Z 
action_result.data.\*.fields.System-Description | string |  |   <div>This is a sample description added via REST API </div> 
action_result.data.\*.fields.System-Id | numeric |  `work item id`  |   61 
action_result.data.\*.fields.System-IterationId | numeric |  |   1 
action_result.data.\*.fields.System-IterationLevel1 | string |  |   test 
action_result.data.\*.fields.System-IterationPath | string |  |   test 
action_result.data.\*.fields.System-NodeName | string |  |   test 
action_result.data.\*.fields.System-PersonId | numeric |  |   253932606 
action_result.data.\*.fields.System-Reason | string |  |   Added to backlog 
action_result.data.\*.fields.System-Rev | numeric |  |   1 
action_result.data.\*.fields.System-RevisedDate | string |  |   9999-01-01T00:00:00Z 
action_result.data.\*.fields.System-State | string |  |   To Do 
action_result.data.\*.fields.System-TeamProject | string |  |   test 
action_result.data.\*.fields.System-Title | string |  |   This task title is created via REST API 
action_result.data.\*.fields.System-Watermark | numeric |  |   119 
action_result.data.\*.fields.System-WorkItemType | string |  |   Epic 
action_result.data.\*.id | numeric |  |   9 
action_result.data.\*.rev | numeric |  |   1 
action_result.data.\*.url | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/9 
action_result.summary | string |  |  
action_result.summary.status | string |  |   Work item added successfully 
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list iterations'
Get team's iteration

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**team** |  optional  | Team ID or team name | string | 
**timeframe** |  optional  | A filter for which iterations are returned based on relative time (Only Current is supported currently) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.team | string |  |  
action_result.parameter.timeframe | string |  |  
action_result.data | string |  |  
action_result.data.\*.count | numeric |  |   1 
action_result.data.\*.value.\*.attributes.finishDate | string |  |  
action_result.data.\*.value.\*.attributes.startDate | string |  |  
action_result.data.\*.value.\*.attributes.timeFrame | string |  |   current 
action_result.data.\*.value.\*.id | string |  |   8f75ec99-73f5-401c-8c9d-7ac14e9de431 
action_result.data.\*.value.\*.name | string |  |   Sprint 1 
action_result.data.\*.value.\*.path | string |  |   Sprint 1 
action_result.data.\*.value.\*.url | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/c124ba33-cc3e-42b0-b9d1-7d29c1812c34/_apis/work/teamsettings/iterations/8f75ec99-73f5-401c-8c9d-7ac14e9de431 
action_result.summary | string |  |  
action_result.summary.num_data | numeric |  |   2 
action_result.summary.status | string |  |   Data retrieved successfully 
action_result.summary.total_iterations | numeric |  |   1 
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add comment'
Add a comment on a work item

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**work_item_id** |  required  | Id of a work item | numeric | 
**comment** |  required  | The text of the comment | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.comment | string |  |  
action_result.parameter.work_item_id | string |  |  
action_result.data | string |  |  
action_result.data.\*.createdBy._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.createdBy.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.createdBy.displayName | string |  |   test Edwards 
action_result.data.\*.createdBy.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.createdBy.imageUrl | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.createdBy.uniqueName | string |  |   test@test.com 
action_result.data.\*.createdBy.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.createdDate | string |  |   2023-02-07T08:33:56.447Z 
action_result.data.\*.id | numeric |  |   1985876 
action_result.data.\*.modifiedBy._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.modifiedBy.descriptor | string |  |   aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.modifiedBy.displayName | string |  |   test Edwards 
action_result.data.\*.modifiedBy.id | string |  |   a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.modifiedBy.imageUrl | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.YTQ1ODc0MzgtZWYwOC03YzNhLWJiMGUtOTQyNmNmZjM2YTcy 
action_result.data.\*.modifiedBy.uniqueName | string |  |   test@test.com 
action_result.data.\*.modifiedBy.url | string |  |   https://spsprodsin2.vssps.visualstudio.com/A0ec3bd2d-0567-4fc0-bd83-8a95ff980ce7/_apis/Identities/a4587438-ef08-6c3a-bb0e-9426cff36a72 
action_result.data.\*.modifiedDate | string |  |   2023-02-07T08:33:56.447Z 
action_result.data.\*.text | string |  |   test 
action_result.data.\*.url | string |  |   https://dev.azure.com/test0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/workItems/1/comments/1985876 
action_result.data.\*.version | numeric |  |   1 
action_result.data.\*.workItemId | numeric |  |   1 
action_result.summary | string |  |  
action_result.summary.status | string |  |   Comment added successfully 
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add user'
Add a user to a project

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**user_email** |  required  | The email address of the user to add to the organization | string |  `email` 
**account_license_type** |  required  | The type of account license. Possible values are: express, stakeholder, advanced, earlyAdopter, professional | string | 
**group_type** |  required  | The project group type. Possible values are: projectReader, projectContributor, projectAdministrator, projectStakeholder | string | 
**project_name** |  required  | The name of the project | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.account_license_type | string |  |  
action_result.parameter.group_type | string |  |  
action_result.parameter.project_name | string |  |  
action_result.parameter.user_email | string |  `email`  |  
action_result.data.\*.isSuccess | boolean |  |   True  False 
action_result.data.\*.operationResult.errors.\*.key | numeric |  |   5000 
action_result.data.\*.operationResult.errors.\*.value | string |  |   abc 
action_result.data.\*.operationResult.isSuccess | boolean |  |   True  False 
action_result.data.\*.operationResult.result | string |  |  
action_result.data.\*.operationResult.result.accessLevel.accountLicenseType | string |  |   stakeholder 
action_result.data.\*.operationResult.result.accessLevel.assignmentSource | string |  |   unknown 
action_result.data.\*.operationResult.result.accessLevel.licenseDisplayName | string |  |   Stakeholder 
action_result.data.\*.operationResult.result.accessLevel.licensingSource | string |  |   account 
action_result.data.\*.operationResult.result.accessLevel.msdnLicenseType | string |  |   none 
action_result.data.\*.operationResult.result.accessLevel.status | string |  |   pending 
action_result.data.\*.operationResult.result.accessLevel.statusMessage | string |  |  
action_result.data.\*.operationResult.result.dateCreated | string |  |   2023-01-25T09:43:42.8909935Z 
action_result.data.\*.operationResult.result.id | string |  |   1556eb14-2da0-46cb-8425-e9a11dcee3ac 
action_result.data.\*.operationResult.result.lastAccessedDate | string |  |   0001-01-01T00:00:00Z 
action_result.data.\*.operationResult.result.user._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.operationResult.result.user._links.membershipState.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/MembershipStates/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.operationResult.result.user._links.memberships.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Memberships/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.operationResult.result.user._links.self.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.operationResult.result.user._links.storageKey.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/StorageKeys/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.operationResult.result.user.descriptor | string |  |   bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.operationResult.result.user.displayName | string |  |   test@testazure.com 
action_result.data.\*.operationResult.result.user.domain | string |  |   140fe46d-819d-4b6d-b7ef-1c0a8270f4f0 
action_result.data.\*.operationResult.result.user.mailAddress | string |  |   dhruv@testazure.com 
action_result.data.\*.operationResult.result.user.origin | string |  |   aad 
action_result.data.\*.operationResult.result.user.originId | string |  |  
action_result.data.\*.operationResult.result.user.principalName | string |  |   dhruv@testazure.com 
action_result.data.\*.operationResult.result.user.subjectKind | string |  |   user 
action_result.data.\*.operationResult.result.user.url | string |  |   https://www.abc.com 
action_result.data.\*.operationResult.userId | string |  `userid`  |   1556eb14-2da0-46cb-8425-e9a11dcee3ac 
action_result.data.\*.userEntitlement | string |  |  
action_result.data.\*.userEntitlement.accessLevel.accountLicenseType | string |  |   stakeholder 
action_result.data.\*.userEntitlement.accessLevel.assignmentSource | string |  |   unknown 
action_result.data.\*.userEntitlement.accessLevel.licenseDisplayName | string |  |   Stakeholder 
action_result.data.\*.userEntitlement.accessLevel.licensingSource | string |  |   account 
action_result.data.\*.userEntitlement.accessLevel.msdnLicenseType | string |  |   none 
action_result.data.\*.userEntitlement.accessLevel.status | string |  |   pending 
action_result.data.\*.userEntitlement.accessLevel.statusMessage | string |  |  
action_result.data.\*.userEntitlement.dateCreated | string |  |   2023-01-25T09:43:42.8909935Z 
action_result.data.\*.userEntitlement.id | string |  |   1556eb14-2da0-46cb-8425-e9a11dcee3ac 
action_result.data.\*.userEntitlement.lastAccessedDate | string |  |   0001-01-01T00:00:00Z 
action_result.data.\*.userEntitlement.user._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.userEntitlement.user._links.membershipState.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/MembershipStates/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.userEntitlement.user._links.memberships.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Memberships/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.userEntitlement.user._links.self.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.userEntitlement.user._links.storageKey.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/StorageKeys/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.userEntitlement.user.descriptor | string |  |   bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.data.\*.userEntitlement.user.displayName | string |  |   dhruv@testazure.com 
action_result.data.\*.userEntitlement.user.domain | string |  |   140fe46d-819d-4b6d-b7ef-1c0a8270f4f0 
action_result.data.\*.userEntitlement.user.mailAddress | string |  |   dhruv@testazure.com 
action_result.data.\*.userEntitlement.user.origin | string |  |   aad 
action_result.data.\*.userEntitlement.user.originId | string |  |  
action_result.data.\*.userEntitlement.user.principalName | string |  |   dhruv@testazure.com 
action_result.data.\*.userEntitlement.user.subjectKind | string |  |   user 
action_result.data.\*.userEntitlement.user.url | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/bnd.dXBuOjE0MGZlNDZkLTgxOWQtNGI2ZC1iN2VmLTFjMGE4MjcwZjRmMFxkaHJ1dkB0ZXN0YXp1cmUuY29t 
action_result.summary.status | string |  |   User with given data added successfully 
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'delete user'
Delete a user

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**user_id** |  required  | ID of the user | string |  `userid` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.user_id | string |  `userid`  |  
action_result.data | string |  |  
action_result.summary.status | string |  |   User deleted successfully 
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'search users'
Search user(s)

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**filter** |  optional  | Equality operators relating to searching user entitlements separated by and clauses | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.filter | string |  |  
action_result.data.\*.items.\*.accessLevel.accountLicenseType | string |  |   stakeholder 
action_result.data.\*.items.\*.accessLevel.assignmentSource | string |  |   unknown 
action_result.data.\*.items.\*.accessLevel.licenseDisplayName | string |  |   Stakeholder 
action_result.data.\*.items.\*.accessLevel.licensingSource | string |  |   account 
action_result.data.\*.items.\*.accessLevel.msdnLicenseType | string |  |   none 
action_result.data.\*.items.\*.accessLevel.status | string |  |   pending 
action_result.data.\*.items.\*.accessLevel.statusMessage | string |  |  
action_result.data.\*.items.\*.dateCreated | string |  |   2023-01-17T13:06:14.1509397Z 
action_result.data.\*.items.\*.id | string |  |   35aff9fa-f21a-4ddd-b3b8-ddb8ecaa0f4c 
action_result.data.\*.items.\*.lastAccessedDate | string |  |   0001-01-01T00:00:00Z 
action_result.data.\*.items.\*.user._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.items.\*.user._links.membershipState.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/MembershipStates/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.items.\*.user._links.memberships.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Memberships/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.items.\*.user._links.self.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.items.\*.user._links.storageKey.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/StorageKeys/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.items.\*.user.descriptor | string |  |   aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.items.\*.user.directoryAlias | string |  |   test7user_user.com#EXT# 
action_result.data.\*.items.\*.user.displayName | string |  |   test7user@user.com 
action_result.data.\*.items.\*.user.domain | string |  |   140fe46d-819d-4b6d-b7ef-1c0a8270f4f0 
action_result.data.\*.items.\*.user.mailAddress | string |  `email`  |   test7user@user.com 
action_result.data.\*.items.\*.user.metaType | string |  |   member 
action_result.data.\*.items.\*.user.origin | string |  |   aad 
action_result.data.\*.items.\*.user.originId | string |  |   c760eedc-c387-48d5-b736-ad415114c523 
action_result.data.\*.items.\*.user.principalName | string |  |   test7user@user.com 
action_result.data.\*.items.\*.user.subjectKind | string |  |   user 
action_result.data.\*.items.\*.user.url | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.accessLevel.accountLicenseType | string |  |   stakeholder 
action_result.data.\*.members.\*.accessLevel.assignmentSource | string |  |   unknown 
action_result.data.\*.members.\*.accessLevel.licenseDisplayName | string |  |   Stakeholder 
action_result.data.\*.members.\*.accessLevel.licensingSource | string |  |   account 
action_result.data.\*.members.\*.accessLevel.msdnLicenseType | string |  |   none 
action_result.data.\*.members.\*.accessLevel.status | string |  |   pending 
action_result.data.\*.members.\*.accessLevel.statusMessage | string |  |  
action_result.data.\*.members.\*.dateCreated | string |  |   2023-01-17T13:06:14.1509397Z 
action_result.data.\*.members.\*.id | string |  |   35aff9fa-f21a-4ddd-b3b8-ddb8ecaa0f4c 
action_result.data.\*.members.\*.lastAccessedDate | string |  |   0001-01-01T00:00:00Z 
action_result.data.\*.members.\*.user._links.avatar.href | string |  |   https://dev.azure.com/test0828/_apis/GraphProfile/MemberAvatars/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.user._links.membershipState.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/MembershipStates/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.user._links.memberships.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Memberships/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.user._links.self.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.user._links.storageKey.href | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/StorageKeys/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.user.descriptor | string |  |   aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.data.\*.members.\*.user.directoryAlias | string |  |   test7user_user.com#EXT# 
action_result.data.\*.members.\*.user.displayName | string |  |   test7user@user.com 
action_result.data.\*.members.\*.user.domain | string |  |   140fe46d-819d-4b6d-b7ef-1c0a8270f4f0 
action_result.data.\*.members.\*.user.mailAddress | string |  |   test7user@user.com 
action_result.data.\*.members.\*.user.metaType | string |  |   member 
action_result.data.\*.members.\*.user.origin | string |  |   aad 
action_result.data.\*.members.\*.user.originId | string |  |   c760eedc-c387-48d5-b736-ad415114c523 
action_result.data.\*.members.\*.user.principalName | string |  |   test7user@user.com 
action_result.data.\*.members.\*.user.subjectKind | string |  |   user 
action_result.data.\*.members.\*.user.url | string |  |   https://vssps.dev.azure.com/test0828/_apis/Graph/Users/aad.NmZmNDFiNDktY2VmYS03M2VkLWI1ZmYtN2EyOWQzMDI3MTA1 
action_result.summary.status | string |  |   Data retrieved successfully 
action_result.summary.total_users | numeric |  |   127 
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add attachment'
Add an attachment to a project

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vault_id** |  required  | SOAR Vault ID of the attachment | string |  `vault id` 
**api_version** |  required  | Version of the API to use (overwrites config) | string | 
**filename** |  required  | Name of the file to be uploaded | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.api_version | string |  |  
action_result.parameter.filename | string |  |  
action_result.parameter.vault_id | string |  `vault id`  |  
action_result.data | string |  |  
action_result.data.\*.id | string |  |   b95793e6-9b27-4ea0-92ea-431b3e048395 
action_result.data.\*.url | string |  |   https://dev.azure.com/herman0828/c24261f4-f968-445c-a9b6-3e0e2fcc3da9/_apis/wit/attachments/b95793e6-9b27-4ea0-92ea-431b3e048395 
action_result.data.0.id | string |  |  
action_result.data.0.url | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 