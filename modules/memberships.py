import yaml
from pulumi import ResourceOptions
from pulumi_github import Membership, Provider


def create_members(provider: Provider):
    with open("config/platform_team_values.yaml") as f:
        data = yaml.safe_load(f)

    for member in data.get("github_organization_members", []):
        username = member["github-username"]
        role = member.get("github-role", "member")

        Membership(
            f"github-membership-{username}",
            username=username,
            role=role,
            opts=ResourceOptions(provider=provider),
        )
