import pulumi
from pulumi_github import Provider

from modules.memberships import create_members
from modules.repos import create_repos

github_provider = Provider(
    "platform-github-provider",
    token=pulumi.Config("github").require("token"),
    owner=pulumi.Config("github").require("owner"),
)

create_members(github_provider)
create_repos(github_provider)
