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
git push origin $currentBranch

Set-Location .\data\compositions
Commit-And-Push $commitMessage
Set-Location ..\..

Set-Location .\data\recordings
Commit-And-Push $commitMessage
Set-Location ..\..

# Commit the updated submodules to the main repository
git add .\data\compositions
git add .\data\recordings
git commit -m "Updated submodules with commit: $commitMessage"
git push origin $currentBranch

Write-Host "Updated submodules with commit: $commitMessage"