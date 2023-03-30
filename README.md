[comment]: # "Auto-generated SOAR connector documentation"
# Azure DevOps

Publisher: Splunk Community  
Connector Version: 1.1.0  
Product Vendor: Microsoft  
Product Name: Azure DevOps  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 5.5.0  

This app integrates with Azure DevOps to perform investigative and generic actions

### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Azure DevOps asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**organization** |  required  | string | The name of the Azure DevOps organization
**project** |  required  | string | Project ID or project name
**api version** |  required  | string | Version of the API to use
**username** |  required  | string | User name for the access token
**access token** |  required  | password | Access token

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[get work item](#action-get-work-item) - Get information about a single work item  
[add work item](#action-add-work-item) - Creates a single work item  
[list iterations](#action-list-iterations) - Get team's iteration  
[add comment](#action-add-comment) - Add a comment on a work item  
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
**id** |  required  | The work item id | numeric | 
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
action_result.parameter.id | numeric |  |  
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |  
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
**expand** |  optional  | The expand parameters for work item attributes (Possible options are { None, Relations, Fields, Links, All }) | string | 
**bypass_rules** |  optional  | Do not enforce the work item type rules on this update | boolean | 
**suppress_notifications** |  optional  | Do not fire any notifications for this change | boolean | 
**validate_only** |  optional  | Indicate if you only want to validate the changes without saving the work item | boolean | 
**post_body** |  required  | Payload to be sent to be created | string | 

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
action_result.summary | string |  |  
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
action_result.summary | string |  |  
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
**work_item_id** |  required  | Id of a work item | string | 
**comment** |  required  | The text of the comment | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.comment | string |  |  
action_result.parameter.work_item_id | string |  |  
action_result.data | string |  |  
action_result.summary | string |  |  
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
action_result.parameter.vault_id | string |  |  
action_result.parameter.api_version | string |  |  
action_result.parameter.filename | string |  |  
action_result.data.0.id | string |  |  
action_result.data.0.url | string |  |  
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 