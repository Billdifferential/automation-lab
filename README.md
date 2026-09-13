# Automation Lab

A collection of automation scripts and tools built while upskilling in IT
automation, scripting, and AI-assisted development.

## User Audit Report (`Get-UserAuditReport.ps1`)

A PowerShell script that connects to Microsoft Graph and generates a bulk
audit report of every user account in a Microsoft Entra ID tenant —
account status, assigned licenses, last sign-in date, and MFA registration
status — exported to CSV.

### Requirements

- PowerShell 7+
- `Microsoft.Graph` PowerShell module (`Install-Module Microsoft.Graph -Scope CurrentUser`)
- A Microsoft Entra ID app registration with **Application** (not Delegated)
  permissions: `User.Read.All`, `AuditLog.Read.All`, `UserAuthenticationMethod.Read.All`,
  with admin consent granted

### Setup

The script authenticates using app-only (client credentials) auth rather
than interactive sign-in, so it can run unattended. Set these environment
variables before running:

```powershell
$env:GRAPH_CLIENT_ID     = "your-app-client-id"
$env:GRAPH_TENANT_ID     = "your-tenant-id"
$env:GRAPH_CLIENT_SECRET = "your-client-secret"
```

### Usage

```powershell
.\Get-UserAuditReport.ps1
```

Output is saved as a timestamped CSV in `output/` (excluded from Git via
`.gitignore`).

### Notes

- `LastSignIn` requires an Azure AD Premium (P1/P2) license on the tenant.
  On tenants without one, the script detects this automatically and falls
  back to reporting `N/A (requires Premium license)` for that field rather
  than failing.
- App-only auth was chosen deliberately over interactive sign-in: recent
  versions of the Microsoft.Graph PowerShell SDK made Windows' Web Account
  Manager the default sign-in broker, which introduced authentication
  failures for many users on Windows. App-only auth sidesteps this
  entirely and is the more appropriate pattern for an unattended
  automation script anyway.
