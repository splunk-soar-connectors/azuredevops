[comment]: # "Auto-generated SOAR connector documentation"
# Azure DevOps

Publisher: Splunk Community  
Connector Version: 1\.0\.2  
Product Vendor: Microsoft  
Product Name: Azure DevOps  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.3\.4  

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
**expand** |  required  | The expand parameters for work item attributes \(Possible options are \{ None, Relations, Fields, Links, All \}\) | string | 
**asof** |  optional  | AsOf UTC date time string | string | 
**fields** |  optional  | Comma\-separated list of requested fields | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.asof | string | 
action\_result\.parameter\.expand | string | 
action\_result\.parameter\.fields | string | 
action\_result\.parameter\.id | numeric | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'add work item'
Creates a single work item

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**work\_item\_type** |  required  | The work item type of the work item to create | string | 
**expand** |  optional  | The expand parameters for work item attributes \(Possible options are \{ None, Relations, Fields, Links, All \}\) | string | 
**bypassrules** |  optional  | Do not enforce the work item type rules on this update | boolean | 
**suppressnotifications** |  optional  | Do not fire any notifications for this change | boolean | 
**validateonly** |  optional  | Indicate if you only want to validate the changes without saving the work item | boolean | 
**post\_body** |  required  | Payload to be sent to be created | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.bypassrules | boolean | 
action\_result\.parameter\.expand | string | 
action\_result\.parameter\.post\_body | string | 
action\_result\.parameter\.suppressnotifications | boolean | 
action\_result\.parameter\.validateonly | boolean | 
action\_result\.parameter\.work\_item\_type | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list iterations'
Get team's iteration

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**team** |  optional  | Team ID or team name | string | 
**timeframe** |  optional  | A filter for which iterations are returned based on relative time \(Only Current is supported currently\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.team | string | 
action\_result\.parameter\.timeframe | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'add comment'
Add a comment on a work item

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**work\_item\_id** |  required  | Id of a work item | string | 
**comment** |  required  | The text of the comment | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.work\_item\_id | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.team | string | 
action\_result\.parameter\.timeframe | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'add attachment'
Add an attachment to a project

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vault\_id** |  required  | Id of the vault item to upload | string | 
**api\_version** |  required  | Version of the API endpoint to use | string | 
**filename** |  required  | Name of the file to upload | string |

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.api\_version | string | 
action\_result\.parameter\.vault_id | string | 
action\_result\.parameter\.filename | string | 
action\_result\.data | string | 
action\_result\.data.0.id | string | 
action\_result\.data.0.url | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 