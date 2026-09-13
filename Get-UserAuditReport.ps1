<#
.SYNOPSIS
    Generates a bulk user audit report from Microsoft Entra ID (Azure AD) via Microsoft Graph.

.DESCRIPTION
    Connects to Microsoft Graph and pulls every user account in the tenant, along with
    account status, assigned licenses, last sign-in date, and MFA registration status.
    Exports the results to a timestamped CSV file.

.NOTES
    Author: William Thurkle
    Requires: Microsoft.Graph PowerShell module (Install-Module Microsoft.Graph -Scope CurrentUser)
    Permissions needed (delegated): User.Read.All, AuditLog.Read.All, UserAuthenticationMethod.Read.All
#>

# --- Configuration ---
$OutputFolder = ".\output"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$OutputFile = Join-Path $OutputFolder "UserAuditReport_$Timestamp.csv"

# --- Ensure output folder exists ---
if (-not (Test-Path $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

# --- Connect to Microsoft Graph ---
Write-Host "Connecting to Microsoft Graph..." -ForegroundColor Cyan
Connect-MgGraph -Scopes "User.Read.All", "AuditLog.Read.All", "UserAuthenticationMethod.Read.All" -NoWelcome

# --- Friendly names for common license SKUs (extend as needed) ---
$LicenseFriendlyNames = @{
    "6fd2c87f-b296-42f0-b197-1e91e994b900" = "Microsoft 365 E3"
    "c7df2760-2c81-4ef7-b578-5b5392b571df" = "Microsoft 365 E5"
    "3b555118-da6a-4418-894f-7df1e2f96f17" = "Microsoft 365 Business Standard"
    "05e9a617-0261-4cee-bb44-138d3ef5d965" = "Microsoft 365 Business Premium"
}

Write-Host "Fetching all users..." -ForegroundColor Cyan
$Users = Get-MgUser -All -Property "DisplayName,UserPrincipalName,AccountEnabled,AssignedLicenses,SignInActivity,Id"

$Report = foreach ($User in $Users) {

    # Map license SKUs to friendly names where known, otherwise show the raw ID
    $Licenses = $User.AssignedLicenses | ForEach-Object {
        if ($LicenseFriendlyNames.ContainsKey($_.SkuId)) {
            $LicenseFriendlyNames[$_.SkuId]
        } else {
            $_.SkuId
        }
    }
    $LicenseList = if ($Licenses) { $Licenses -join "; " } else { "None" }

    # Check MFA registration status for this user
    $MfaStatus = "Unknown"
    try {
        $AuthMethods = Get-MgUserAuthenticationMethod -UserId $User.Id -ErrorAction Stop
        # A user has more than just the default password method if MFA is registered
        $MfaStatus = if ($AuthMethods.Count -gt 1) { "Registered" } else { "Not Registered" }
    } catch {
        $MfaStatus = "Error checking"
    }

    [PSCustomObject]@{
        DisplayName       = $User.DisplayName
        UserPrincipalName = $User.UserPrincipalName
        AccountEnabled    = $User.AccountEnabled
        Licenses          = $LicenseList
        LastSignIn        = $User.SignInActivity.LastSignInDateTime
        MfaStatus         = $MfaStatus
    }
}

# --- Export to CSV ---
$Report | Export-Csv -Path $OutputFile -NoTypeInformation -Encoding UTF8

Write-Host "Done. Report saved to $OutputFile" -ForegroundColor Green
Write-Host "$($Report.Count) user(s) processed." -ForegroundColor Green

Disconnect-MgGraph | Out-Null
