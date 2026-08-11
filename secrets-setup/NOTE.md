## Get the private key into Bitwarden Secrets Manager

Don't hand-type the private key into `secrets.json` — it's multi-line and manually escaping newlines in a JSON string is error-prone. Build the file with `jq --rawfile` instead, which handles escaping for you:

```bash
# e.g 
jq -n --rawfile key ~/Downloads/tpeh-release-bot.2026-08-11.private-key.pem '[{
  "name": "APP_PRIVATE_KEY",
  "value": $key,
  "note": "GitHub App private key (.pem contents) for tpeh-release-bot"
}]' > secrets.json
```

Then run `./inject_secrets.sh` to push it into Bitwarden Secrets Manager.
