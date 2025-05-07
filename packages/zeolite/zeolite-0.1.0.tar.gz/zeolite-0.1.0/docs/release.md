# Release Process

This document describes the release process for this project, including both release candidates (RC) and final releases.

## Overview

The release process follows a GitOps approach with two main phases:
1. Release Candidate (RC) phase for testing
2. Final Release phase for production releases

## Release Workflow

### 1. Creating a Release Candidate

1. Create a new branch from `main` following the format `release/X.Y.Z`:
   ```bash
   git checkout main
   git pull
   git checkout -b release/1.2.3  # Replace with your version
   git push -u origin release/1.2.3
   ```

2. This will automatically trigger the pre-release workflow which:
   - Validates the version number format
   - Runs all tests
   - Builds the package
   - Creates a GitHub Release marked as "pre-release"
   - Tags the release as `v1.2.3-rc`
   - Uploads build artifacts (wheels and tarballs)

3. Test the release candidate:
   - Install and test the RC package
   - Make any necessary fixes on the release branch
   - Each push to the release branch will create a new RC

### 2. Creating the Final Release

1. Once the RC is tested and approved:
   - Update `pyproject.toml` with the final version number
   - Commit and push the changes to the release branch

2. Create a Pull Request:
   - Source: `release/X.Y.Z` branch
   - Target: `main` branch
   - Title: "Release vX.Y.Z"
   - Description: Include release notes and changelog

3. After the PR is approved and merged to `main`:
   - The release workflow automatically triggers
   - Creates a GitHub Release (not marked as pre-release)
   - Tags the release as `vX.Y.Z`
   - Uploads build artifacts

## Version Numbers

- All version numbers must follow semantic versioning (X.Y.Z format)
- Release branches must be named `release/X.Y.Z`
- Release tags will be:
  - `vX.Y.Z-rc` for release candidates
  - `vX.Y.Z` for final releases

## GitHub Actions Workflows

Two workflows handle the release process:

### Pre-Release Workflow (`.github/workflows/prerelease.yml`)
- Triggers on push to `release/*` branches
- Creates release candidates
- Runs tests and builds
- Creates pre-release with RC tag

### Release Workflow (`.github/workflows/release.yml`)
- Triggers on push to `main`
- Creates final releases
- Runs tests and builds
- Creates release with final tag

## Example Release Flow

```bash
# Start a new release
git checkout main
git pull
git checkout -b release/1.2.3

# Test and fix issues
# ... make changes if needed ...
git commit -am "fix: address RC feedback"
git push

# Once RC is approved, update version
# Update pyproject.toml version to 1.2.3
git commit -am "chore: bump version to 1.2.3"
git push

# Create PR to main
# After PR is merged, final release is automated
```

## Troubleshooting

If a workflow fails:
1. Check the GitHub Actions logs
2. Verify version number format
3. Ensure all tests are passing
4. Check if the branch name follows the correct format 