# Environment paths from your poetry output
$envPath1 = "C:\Users\Shadow\AppData\Local\pypoetry\Cache\virtualenvs\polygpt-w11IFSUN-py3.11"
$envPath2 = "C:\Users\Shadow\AppData\Local\pypoetry\Cache\virtualenvs\polygpt-w11IFSUN-py3.12"

# Delete the first environment
if (Test-Path $envPath1) {
    Remove-Item -Recurse -Force $envPath1
    Write-Host "Deleted environment at $envPath1"
} else {
    Write-Host "Path not found: $envPath1"
}

# Delete the second environment
if (Test-Path $envPath2) {
    Remove-Item -Recurse -Force $envPath2
    Write-Host "Deleted environment at $envPath2"
} else {
    Write-Host "Path not found: $envPath2"
}
