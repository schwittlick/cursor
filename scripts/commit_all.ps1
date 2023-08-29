# Function to handle committing and pushing for each repository
Function Commit-And-Push {
    Param (
        [string]$commitMessage
    )
    git add .
    git commit -m "$commitMessage"
    git push origin master
}

# Commit changes in the main repository
Write-Host "Committing main repository..."
Commit-And-Push "Your main repository commit message here"

# Commit changes in the first submodule
Write-Host "Committing first submodule..."
Set-Location .\submodule1_directory
Commit-And-Push "Your first submodule commit message here"
Set-Location ..

# Commit changes in the second submodule
Write-Host "Committing second submodule..."
Set-Location .\submodule2_directory
Commit-And-Push "Your second submodule commit message here"
Set-Location ..

# Commit changes in the third submodule
Write-Host "Committing third submodule..."
Set-Location .\submodule3_directory
Commit-And-Push "Your third submodule commit message here"
Set-Location ..

# Commit updated submodules to the main repository
Write-Host "Committing updated submodules to main repository..."
Commit-And-Push "Updated submodules"

Write-Host "All commits and pushes done!"