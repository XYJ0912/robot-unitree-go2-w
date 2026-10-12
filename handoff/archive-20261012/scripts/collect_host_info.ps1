$ErrorActionPreference = 'Continue'
Write-Output 'READ_ONLY: current Windows machine only; no SSH, DDS or robot commands.'
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,@{Name='RAM_GiB';Expression={[math]::Round($_.TotalPhysicalMemory/1GB,2)}}
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
foreach ($toolName in @('python','python3','rustc','cargo','git','ssh')) {
    $available = Get-Command $toolName -ErrorAction SilentlyContinue
    [pscustomobject]@{Tool=$toolName;Installed=($null -ne $available)}
}
