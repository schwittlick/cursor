param (
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$commitMessage
)

Function Commit-And-Push
{
    Param (
        [string]$commitMessage
    )
    $currentBranch = & git symbolic-ref --short HEAD
    $location = (Get-Location).Path.Split('\')[-1]
    Write-Host "Commited" $currentBranch "in" $location
    git add .
    git commit -m "$commitMessage"
    git push origin $currentBranch
}
$currentBranch = & git symbolic-ref --short HEAD

git add .\cursor
git add .\scripts
git add .\examples
git add .\docs
git add .\firmware
git add .\tools
git commit -m "$commitMessage"

Set-Location ..\cursor-data\compositions
Commit-And-Push $commitMessage
Set-Location ..

Set-Location .\recordings
Commit-And-Push $commitMessage
Set-Location ..\..

Write-Host "Updated submodules with commit: $commitMessage"