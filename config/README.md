# Configuration Files

This directory contains third-party tool configurations.

## Contents

- **.whitesource** - WhiteSource/Mend dependency scanning config
- **renovate.json** - Renovate automated dependency updates
- **CODEOWNERS** - GitHub code ownership definitions

## Descriptions

### .whitesource
Configures WhiteSource for automated dependency vulnerability scanning.
- Scans on every commit
- Automatic PR creation for vulnerability fixes

### renovate.json
Enables Renovate bot for automated dependency updates.
- Groups minor/patch updates
- Auto-merges passing tests
- Weekly update schedule

### CODEOWNERS
Defines code ownership for GitHub reviews.
- Ensures security team reviews security/ changes
- Automatic PR assignment

