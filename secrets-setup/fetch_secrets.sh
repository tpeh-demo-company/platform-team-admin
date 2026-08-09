#!/usr/bin/env bash
set -eou pipefail

ENV_FILE="../.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Can't find env file...exiting"
    exit 1
fi

set -o allexport
source "$ENV_FILE"
set +o allexport

github_token=$(bws secret list | jq -r '.[] | select(.key == "GITHUB_TOKEN") | .value')
github_owner=$(bws secret list | jq -r '.[] | select(.key == "GITHUB_OWNER") | .value')

(
    cd ..
    pulumi config set --secret github:token "$github_token"
    pulumi config set github:owner "$github_owner"
)

echo "Pulumi config updated."
