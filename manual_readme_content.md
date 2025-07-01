## Interactive Auth

**IMPORTANT NOTICE**: As of April 2025, Microsoft is no longer accepting new Azure DevOps OAuth app registrations. All new integrations must use Microsoft Entra ID OAuth. Existing Azure DevOps OAuth integrations will continue to work until the end-of-life date (announced for 2026).

### For New Integrations (Microsoft Entra ID OAuth)

This app now supports Microsoft Entra ID OAuth for new integrations. To register your app:

1. Navigate to the [Microsoft Entra admin center](https://entra.microsoft.com) and register a new application
1. Go to **App registrations** -> **New registration**
1. Provide a name for your application
1. **Leave the redirect URI empty for now** - you'll add it after creating the Splunk SOAR asset
1. Record your **Application (client) ID** and **Directory (tenant) ID**
1. Create a **Client secret** under **Certificates & secrets**
1. Under **API permissions**, add delegated permissions for **Azure DevOps**:
   - Click **"Add a permission"**
   - Select **"Microsoft APIs"** → **"Azure DevOps"** (or search for "Azure DevOps")
   - Choose **"Delegated permissions"**
   - Select the following permissions:
     - ✅ `vso.work` (Work items - Read & Write)
     - ✅ `vso.entitlements` (User entitlements - Read)
     - ✅ `vso.memberentitlementmanagement_write` (User Profile - Read & Write)
   - Click **"Add permissions"**
   - **Add offline access permission** (required for token refresh):
     - Click **"Add a permission"** again
     - Select **"Microsoft Graph"** → **"Delegated permissions"**
     - Search for and select **`offline_access`**
     - Click **"Add permissions"**
   - Click **"Grant admin consent"** (if you have admin privileges)

### For Existing Integrations (Legacy Support)

**Note**: This app continues to support existing Azure DevOps OAuth integrations created before April 2025. If you have an existing registration, you can continue using it unchanged. However, all new integrations should use the Entra ID method above.

## Configure the Azure DevOps Splunk SOAR app Asset

When creating an asset for the **Azure DevOps** app, fill in:

- **Organization**: Your Azure DevOps organization name
- **Project**: Your project name
- **API Version**: "7.0"
- **Auth Type**: "Interactive Auth (Entra ID)" for new integrations
- **Client ID**: From your Entra app registration
- **Client Secret**: From your Entra app registration
- **Tenant ID**: From your Entra app registration (required for Entra ID)

After saving, copy the callback URL from the **POST incoming for Azure DevOps to this location** field and add it as a redirect URI in your app registration:

1. Go back to your app registration in the [Microsoft Entra admin center](https://entra.microsoft.com)
1. Navigate to **Authentication** in the left menu
1. Under **Platform configurations**, click **"Add a platform"**
1. Select **"Web"**
1. In the **Redirect URIs** section, paste the callback URL you copied from Splunk SOAR
1. Click **"Configure"**
1. Click **"Save"**

## Method to Run Test Connectivity

After setting up the asset and user, click the **TEST CONNECTIVITY** button. A window should pop
up and display a URL. Navigate to this URL in a separate browser tab. This new tab will redirect
to a Microsoft login page. Log in to a Microsoft account with administrator privileges to the
Azure Devops environment. After logging in, review the requested permissions listed, then click
**Accept** . Finally, close that tab. The test connectivity window should show a success.

The app should now be ready to use. Token will last for 90 days without the need to run test connectivity again.

If username and password is entered than priority will be given to the basic auth then
Interactive Auth.

We have tested all action for the api version 7.0 but it might be supported in other versions as
well.

## State File Permissions

Please check the permissions for the state file as mentioned below.

#### State Filepath

- For Non-NRI Instance:
  /opt/phantom/local_data/app_states/c6d3b801-5c26-4abd-9e89-6d8007e2778f/{asset_id}\_state.json
- For NRI Instance:
  /\<PHANTOM_HOME_DIRECTORY>/local_data/app_states/c6d3b801-5c26-4abd-9e89-6d8007e2778f/{asset_id}\_state.json

#### State File Permissions

- File Rights: rw-rw-r-- (664) (The phantom user should have read and write access for the
  state file)
- File Owner: appropriate phantom user

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the Azure AD server. Below are the
default ports used by Splunk SOAR.

|         Service Name | Transport Protocol | Port |
|----------------------|--------------------|------|
|         http | tcp | 80 |
|         https | tcp | 443 |

## Basic Authentication

This app requires two params for the basic authentication which is username and access
token(password). username will be email id. To generate the access token follow
[this](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows#create-a-pat)
steps and select Entitlements - Read (vso.entitlements), User Profile -
Read&Write(vso.memberentitlementmanagement_write) and work item - Read&Write(vso.work_full)
scopes.
