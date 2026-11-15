import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"
VALIDATOR = ROOT / "scripts" / "validate-sandbox-config.sh"


def test_workflow_validates_pull_requests_and_deploys_only_manually() -> None:
    workflow = WORKFLOW.read_text()

    assert "pull_request:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "environment: sandbox" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow


def test_workflow_uses_repository_variables_and_partial_backend() -> None:
    workflow = WORKFLOW.read_text()

    for variable in ("AWS_REGION", "TF_STATE_BUCKET", "EXISTING_IAM_ROLE_ARN"):
        assert f"vars.{variable}" in workflow
    assert "init -backend=false" in workflow
    assert '-backend-config="key=lambda/terraform.tfstate"' in workflow
    assert "scripts/validate-sandbox-config.sh" in workflow


def _fake_aws(tmp_path: Path) -> Path:
    binary = tmp_path / "aws"
    binary.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
case " $* " in
  *" sts get-caller-identity "*) printf '%s\\n' "${FAKE_ACCOUNT_ID}" ;;
  *" iam get-role "*) printf '%s\\n' "${FAKE_ROLE_ARN}" ;;
  *" s3api head-bucket "*)
    [[ "${FAKE_BUCKET_ACCESS:-denied}" == allowed ]] || exit 44
    ;;
  *) exit 45 ;;
esac
"""
    )
    binary.chmod(0o755)
    return binary


def _run_validator(
    tmp_path: Path, **overrides: str
) -> subprocess.CompletedProcess[str]:
    _fake_aws(tmp_path)
    env = {
        **os.environ,
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "AWS_REGION": "us-east-1",
        "TF_STATE_BUCKET": "terraform-state-891377055171-us-east-1",
        "EXISTING_IAM_ROLE_ARN": "arn:aws:iam::891377055171:role/LabRole",
        "FAKE_ACCOUNT_ID": "891377055171",
        "FAKE_ROLE_ARN": "arn:aws:iam::891377055171:role/LabRole",
        "FAKE_BUCKET_ACCESS": "allowed",
    }
    env.update(overrides)
    return subprocess.run(
        ["bash", str(VALIDATOR)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_validator_rejects_missing_configuration(tmp_path: Path) -> None:
    result = _run_validator(tmp_path, TF_STATE_BUCKET="")

    assert result.returncode == 2
    assert "TF_STATE_BUCKET" in result.stderr


def test_validator_rejects_role_from_another_account(tmp_path: Path) -> None:
    result = _run_validator(
        tmp_path,
        EXISTING_IAM_ROLE_ARN="arn:aws:iam::000000000000:role/LabRole",
    )

    assert result.returncode == 3
    assert "does not match active AWS account" in result.stderr


def test_validator_rejects_inaccessible_state_bucket(tmp_path: Path) -> None:
    result = _run_validator(tmp_path, FAKE_BUCKET_ACCESS="denied")

    assert result.returncode == 5
    assert "state bucket is missing or inaccessible" in result.stderr


def test_validator_accepts_matching_sandbox_configuration(tmp_path: Path) -> None:
    result = _run_validator(tmp_path)

    assert result.returncode == 0
    assert "sandbox configuration validated" in result.stdout
