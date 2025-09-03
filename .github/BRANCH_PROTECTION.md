# Branch Protection Rules

To ensure code quality and prevent broken code from being merged, the following branch protection rules should be configured for the `main` branch:

## Required Status Checks

The following status checks must pass before a PR can be merged:

1. **Static Code Analysis** - Ensures code quality standards
2. **Unit Tests** - Validates individual component functionality
3. **Integration Tests** - Tests component interactions
4. **End-to-End Tests** - Validates complete system functionality

## Configuration Steps

### 1. Go to Repository Settings
- Navigate to your GitHub repository
- Click on "Settings" tab
- Click on "Branches" in the left sidebar

### 2. Add Branch Protection Rule
- Click "Add rule" or "Add branch protection rule"
- In "Branch name pattern", enter: `main`

### 3. Configure Protection Settings
Enable the following options:

#### ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Require review from code owners (if you have a CODEOWNERS file)

#### ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Select the following required status checks:
  - `Static Code Analysis`
  - `Unit Tests`
  - `Integration Tests`
  - `End-to-End Tests`

#### ✅ Require conversation resolution before merging
- ✅ Require conversation resolution before merging

#### ✅ Require signed commits (optional but recommended)
- ✅ Require signed commits

#### ✅ Require linear history (optional)
- ✅ Require linear history

#### ✅ Include administrators
- ✅ Include administrators

### 4. Save the Rule
- Click "Create" or "Save changes"

## What This Achieves

1. **Code Quality**: Static analysis ensures consistent code style and catches potential issues
2. **Test Coverage**: All test types must pass, ensuring functionality works at all levels
3. **Review Process**: At least one approval required before merge
4. **Up-to-date Code**: Branches must be current with main before merging
5. **Clean History**: Linear history makes the git log easier to follow

## CI Workflow Integration

The CI workflow is designed to work with these protection rules:

- **Static Analysis Job**: Runs flake8, black, isort, pylint, and bandit
- **Unit Tests Job**: Runs unit tests with coverage reporting
- **Integration Tests Job**: Runs integration tests with Redis service
- **End-to-End Tests Job**: Runs full system tests using Docker Compose
- **PR Status Check**: Validates all jobs passed before allowing merge

## Troubleshooting

If a PR is blocked from merging:

1. Check the "Checks" tab in the PR to see which jobs failed
2. Fix any issues in your code
3. Push new commits to update the PR
4. Wait for all checks to pass
5. The PR will then be eligible for merge

## Local Development

To ensure your code passes CI checks locally, use the Makefile commands:

```bash
make check        # Run all static analysis
make test-unit    # Run unit tests
make test-integration  # Run integration tests (requires Redis)
make test-e2e     # Run end-to-end tests
make test-all     # Run all tests
```
