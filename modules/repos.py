import pulumi
import yaml
from pulumi import ResourceOptions, export
from pulumi_github import (
    BranchProtection,
    BranchProtectionRequiredPullRequestReviewArgs,
    Provider,
    Repository,
    RepositoryEnvironment,
    RepositoryEnvironmentReviewerArgs,
    get_user,
)


def _validate_reviewers(data: dict) -> None:
    org_members = {
        m["github-username"] for m in data.get("github_organization_members", [])
    }
    for repo in data.get("github_repositories", []):
        for env in repo.get("environments", []):
            for reviewer in env.get("reviewers", []):
                if reviewer not in org_members:
                    raise pulumi.RunError(
                        f"Reviewer '{reviewer}' in {repo['name']}/{env['name']} "
                        f"is not an org member. Add them to github_organization_members first."
                    )


def create_repos(provider: Provider):
    with open("config/platform_team_values.yaml") as f:
        data = yaml.safe_load(f)

    _validate_reviewers(data)

    # For simplicity reasons , let all admins be the reviewers of all environments by default.
    # In a real org would want more segregation.
    admin_usernames = [
        m["github-username"]
        for m in data.get("github_organization_members", [])
        if m.get("github-role") == "admin"
    ]

    for repo_def in data.get("github_repositories", []):
        repo_name = repo_def.get("name")
        repo_description = repo_def.get("description", "")
        visibility = repo_def.get("visibility", "private")

        repository = Repository(
            repo_name,
            name=repo_name,
            description=repo_description,
            visibility=visibility,
            opts=ResourceOptions(provider=provider, protect=True),
        )

        for bp_def in repo_def.get("branch_protection", []):
            pattern = bp_def.get("pattern", "main")

            pr_reviews = None
            pr_def = bp_def.get("required_pull_request_reviews")
            if pr_def is not None:
                # pull_request_bypassers: users="/login", teams="org/slug", apps=node_id
                bypass_def = pr_def.get("bypass_pull_request_allowances", {})
                bypassers = (
                    bypass_def.get("users", [])
                    + bypass_def.get("teams", [])
                    + bypass_def.get("apps", [])
                )
                pr_reviews = [
                    BranchProtectionRequiredPullRequestReviewArgs(
                        required_approving_review_count=pr_def.get(
                            "required_approving_review_count", 1
                        ),
                        dismiss_stale_reviews=pr_def.get(
                            "dismiss_stale_reviews", False
                        ),
                        require_code_owner_reviews=pr_def.get(
                            "require_code_owner_reviews", False
                        ),
                        require_last_push_approval=pr_def.get(
                            "require_last_push_approval", False
                        ),
                        pull_request_bypassers=bypassers or None,
                    )
                ]

            BranchProtection(
                f"{repo_name}-{pattern}-branch-protection",
                repository_id=repository.name,
                pattern=pattern,
                enforce_admins=bp_def.get("enforce_admins", True),
                require_signed_commits=bp_def.get("require_signed_commits", True),
                required_pull_request_reviews=pr_reviews,
                opts=ResourceOptions(provider=provider, delete_before_replace=True),
            )

        for env_def in repo_def.get("environments", []):
            reviewer_usernames = env_def.get("reviewers", admin_usernames)
            reviewers = []
            if reviewer_usernames:
                user_ids = [int(get_user(username=u).id) for u in reviewer_usernames]
                reviewers = [RepositoryEnvironmentReviewerArgs(users=user_ids)]

            RepositoryEnvironment(
                f"{repo_name}-{env_def['name']}-environment",
                repository=repo_name,
                environment=env_def["name"],
                reviewers=reviewers,
                opts=ResourceOptions(provider=provider, depends_on=[repository]),
            )

        export(f"{repo_name}_repo_name", repository.name)
