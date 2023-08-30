#!/bin/bash

# Function for commit and push
commit_and_push() {
  local commitMessage="$1"
  local currentBranch=$(git symbolic-ref --short HEAD)
  local location=$(basename "$PWD")
  echo "Commited $currentBranch in $location"
  git add .
  git commit -m "$commitMessage"
  git push origin "$currentBranch"
}

# Check for commit message
if [ -z "$1" ]; then
  echo "Commit message is required"
  exit 1
fi

commitMessage="$1"

# Commit specified folders in the main repository
currentBranch=$(git symbolic-ref --short HEAD)
git add ./cursor ./scripts ./examples ./docs ./firmware ./tools
git commit -m "$commitMessage"
git push origin "$currentBranch"

# Change directory and commit changes
cd ./data/compositions || {
  echo "Directory ./data/compositions does not exist"
  exit 1
}
commit_and_push "$commitMessage"
cd ../..

cd ./data/recordings || {
  echo "Directory ./data/recordings does not exist"
  exit 1
}
commit_and_push "$commitMessage"
cd ../..

# Commit the updated submodules to the main repository
git add ./data/compositions ./data/recordings
git commit -m "Updated submodules with commit: $commitMessage"
git push origin "$currentBranch"

echo "Updated submodules with commit: $commitMessage"
