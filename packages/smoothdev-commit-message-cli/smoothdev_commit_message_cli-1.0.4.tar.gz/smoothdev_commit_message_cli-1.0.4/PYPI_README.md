# SmoothDev Commit Message CLI

A CLI tool that generates commit messages using AI. This tool integrates with your git workflow to analyze staged changes and generate meaningful commit messages.

## Features

- Generates commit messages from git diffs
- Supports branch name and issue key context
- Secure authentication via Auth0 device flow
- Debug logging for troubleshooting
- Handles compressed and encoded responses
- Configurable via config file or environment variables

## Installation

```bash
pip install smoothdev-commit-message-cli
```

## Quick Start

```bash
# Generate a commit message for staged changes
smoothdev-commit-message-cli

# Generate a commit message with an issue key
smoothdev-commit-message-cli -i JIRA-123

# Generate a commit message for a specific branch
smoothdev-commit-message-cli -b feature/my-branch
```

## Command Line Options

```
-d, --diff       Git diff content (if not using staged changes)
-f, --file       File containing git diff
-b, --branch     Branch name (defaults to current branch)
-i, --issue      Issue number or key
-c, --config     Custom config file path
--debug          Enable debug logging
```

## Authentication

The tool uses Auth0's device flow for secure authentication. On first run, you'll be prompted to authenticate through your browser. Tokens are securely stored and automatically refreshed when needed.

## Related Projects

- **VS Code Extension**: [SmoothDev Commit Message Generator](https://marketplace.visualstudio.com/items?itemName=smoothdevio.smoothdev-commit-message-generator)
- **Homebrew Formula**: `brew install smoothdev-io/tap/smoothdev-commit-message-cli`
- **GitHub Repository**: [smoothdev-io/commit-message-cli](https://github.com/smoothdev-io/commit-message-cli)

## License

MIT License - see LICENSE file for details
