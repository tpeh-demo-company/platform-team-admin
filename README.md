# The Platform Engineer's Handbook - Platform Team Administration

[![Pulumi Infrastructure](https://github.com/tpeh-demo-company/platform-team-admin/actions/workflows/pulumi.yml/badge.svg)](https://github.com/tpeh-demo-company/platform-team-admin/actions/workflows/pulumi.yml)

Follow-along repository for *The Platform Engineer's Handbook*.

This repo demonstrates how a platform team can manage GitHub as code using Pulumi. Instead of clicking through the GitHub UI, all repositories, branch protection rules, and deployment environments are declared in a single YAML file (`config/platform_team_values.yaml`) and applied automatically via a CI/CD pipeline.

The workflow is tag-driven: pushing a `v*` tag triggers a Pulumi preview, waits for manual approval, then runs `pulumi up` to reconcile the declared state with GitHub.

## Prerequisites

| Tool | Purpose |
| ---- | ------- |
| [Pulumi CLI](https://www.pulumi.com/docs/install/) | Deploy and manage infrastructure state |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Python toolchain and dependency management |
| [bws](https://bitwarden.com/help/secrets-manager-cli/) | Bitwarden Secrets Manager CLI for secret injection |
| GitHub PAT | Personal access token with `repo` and `admin:org` scopes |

## Managed Repositories

| Repository | Description |
| ---------- | ----------- |
| [platform-team-admin](https://github.com/tpeh-demo-company/platform-team-admin) | Repository to manage platform team membership and admin artifacts |
| [platform-core](https://github.com/tpeh-demo-company/platform-core) | Core platform runtime |
| [platform-demo-app](https://github.com/tpeh-demo-company/platform-demo-app) | Demo application for testing the platform |
| [platform-gitops](https://github.com/tpeh-demo-company/platform-gitops) | FluxCD App-of-Apps Repository |
| [platform-helm-chart](https://github.com/tpeh-demo-company/platform-helm-chart) | Generic Helm Chart for Company-Wide Use |
| [platform-services](https://github.com/tpeh-demo-company/platform-services) | Platform Services Tenant Repository |

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure secrets

Copy `.env.example` to `.env` and fill in your Bitwarden Secrets Manager credentials (`BWS_ACCESS_TOKEN`, `BWS_PROJECT_ID`). If you are on the EU server, also add `BWS_SERVER_URL=https://vault.bitwarden.eu`.

### 3. Populate Bitwarden Secrets Manager (first time only)

Copy `secrets-setup/secrets.json_example` to `secrets-setup/secrets.json`, fill in your values, then push them to Bitwarden:

```bash
cd secrets-setup
./inject_secrets.sh
```

### 4. Inject secrets into Pulumi

Pull the secrets from Bitwarden and set them as Pulumi config values:

```bash
cd secrets-setup
./fetch_secrets.sh
```

## Configure repositories

Edit `config/platform_team_values.yaml` to define your repositories, environments, and branch protection rules:

```yaml
github_repositories:
  - name: my-repo
    description: "My repository"
    visibility: public
    branch_protection:
      pattern: "main"
      enforce_admins: true
      require_signed_commits: true
      required_pull_request_reviews:       # optional
        required_approving_review_count: 1
        dismiss_stale_reviews: false
        require_code_owner_reviews: false
        require_last_push_approval: false
    environments:
      - name: production
        reviewers:
          - your-github-username
```

## Deploy

Preview changes locally before triggering the pipeline:

```bash
pulumi preview
```

To deploy, trigger the **Tag** workflow manually from GitHub Actions. This auto-generates a versioned tag (`vYYYY.MM.DD.i`) which kicks off the pipeline:

1. Lint and static analysis
2. `pulumi preview` runs and posts the plan
3. Manual approval gate (requires review in the `pulumi-production` environment)
4. `pulumi up` runs automatically after approval
