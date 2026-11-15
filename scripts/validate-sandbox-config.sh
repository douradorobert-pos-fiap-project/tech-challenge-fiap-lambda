#!/usr/bin/env bash
set -euo pipefail

require_value() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    printf 'Missing required configuration: %s\n' "$name" >&2
    exit 2
  fi
}

for name in AWS_REGION TF_STATE_BUCKET EXISTING_IAM_ROLE_ARN; do
  require_value "$name"
done

if [[ ! "$EXISTING_IAM_ROLE_ARN" =~ ^arn:aws[a-zA-Z-]*:iam::([0-9]{12}):role/(.+)$ ]]; then
  printf 'EXISTING_IAM_ROLE_ARN is not a valid IAM role ARN\n' >&2
  exit 2
fi

configured_account_id="${BASH_REMATCH[1]}"
role_name="${BASH_REMATCH[2]##*/}"
active_account_id="$(
  AWS_PAGER='' aws --no-cli-pager --region "$AWS_REGION" \
    sts get-caller-identity --query Account --output text
)"

if [[ "$configured_account_id" != "$active_account_id" ]]; then
  printf 'Configured role account does not match active AWS account\n' >&2
  exit 3
fi

actual_role_arn="$(
  AWS_PAGER='' aws --no-cli-pager --region "$AWS_REGION" \
    iam get-role --role-name "$role_name" --query Role.Arn --output text
)"
if [[ "$actual_role_arn" != "$EXISTING_IAM_ROLE_ARN" ]]; then
  printf 'Configured IAM role does not match the role returned by AWS\n' >&2
  exit 4
fi

if ! AWS_PAGER='' aws --no-cli-pager --region "$AWS_REGION" \
  s3api head-bucket --bucket "$TF_STATE_BUCKET" >/dev/null 2>&1; then
  printf 'Terraform state bucket is missing or inaccessible: %s\n' \
    "$TF_STATE_BUCKET" >&2
  exit 5
fi

printf 'AWS sandbox configuration validated for account %s in %s\n' \
  "$active_account_id" "$AWS_REGION"
