# PowerShell script to configure advanced RDP settings with improved error handling and file path corrections.

function Configure-RDPSecurity {
    param (
        [string]$username,
        [int]$port
    )

    # Ensure running as Administrator
    if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
    {
        Write-Host "Please run this script as an Administrator." -ForegroundColor Red
        return
    }

    # Enable Remote Desktop
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -name "fDenyTSConnections" -Value 0

    # Set the RDP listening port
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -name "PortNumber" -Value $port

    # Configure Windows Firewall
    Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
    New-NetFirewallRule -DisplayName "Custom RDP Port $port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -Profile Any

    # Temporary file path for security settings
    $tempFilePath = "$env:TEMP\scesettings.inf"

    # Configure Local Security Policy for user rights assignment
    $secRights = @"
[Unicode]
Unicode=yes
[Version]
signature="$CHICAGO$"
Revision=1
[System Access]
[Event Audit]
[Registry Keys]
[Registry Values]
[Privilege Rights]
SeRemoteInteractiveLogonRight = $username
"@
    $secRights | Out-File -FilePath $tempFilePath
    secedit /configure /db secpol.sdb /cfg "$tempFilePath" /areas USER_RIGHTS

    # Remove the temporary file
    Remove-Item $tempFilePath -Force

    # Set client encryption level to High
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name "MinEncryptionLevel" -Value 3

    # Set security layer to SSL
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name "SecurityLayer" -Value 2

    # Require use of specific security layer (SSL)
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name "UserAuthentication" -Value 1

    # Add user to Remote Desktop Users group (if not already added)
    try {
        Add-LocalGroupMember -Group "Remote Desktop Users" -Member $username -ErrorAction Stop
    } catch {
        Write-Host "User $username may already be in the group or does not exist." -ForegroundColor Red
    }
}

# Main script starts here
$username = Read-Host "Enter the username to grant RDP access"
$port = Read-Host "Enter the new RDP port number"

# Call the function to configure RDP
Configure-RDPSecurity -username $username -port $port
