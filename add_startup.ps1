$startupPath = [Environment]::GetFolderPath('Startup')
$sourcePath = 'C:\Users\admin\Desktop\job apply\start_agent.bat'
$destPath = Join-Path $startupPath 'JobAgent.bat'
Copy-Item $sourcePath $destPath -Force
Write-Host "Added to startup: $destPath"
