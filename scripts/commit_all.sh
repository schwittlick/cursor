#!/bin/bash

# Function to handle committing and pushing for each repository
commit_and_push() {
  git add .
  git commit -m "$1"
  git push origin master
}

# Commit changes in the main repository
echo "Committing main repository..."
commit_and_push "Your main repository commit message here"

# Commit changes in the first submodule
echo "Committing first submodule..."
cd submodule1_directory
commit_and_push "Your first submodule commit message here"
cd ..

# Commit changes in the second submodule
echo "Committing second submodule..."
cd submodule2_directory
commit_and_push "Your second submodule commit message here"
cd ..

# Commit changes in the third submodule
echo "Committing third submodule..."
cd submodule3_directory
commit_and_push "Your third submodule commit message here"
cd ..

# Commit updated submodules to the main repository
echo "Committing updated submodules to main repository..."
git add .
git commit -m "Updated submodules"
git push origin master

echo "All commits and pushes done!"