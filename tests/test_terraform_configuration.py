import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERRAFORM = ROOT / "terraform"


def test_terraform_declares_partial_s3_backend() -> None:
    versions = (TERRAFORM / "versions.tf").read_text()

    assert re.search(r'backend\s+"s3"\s*\{\s*\}', versions)


def test_executable_terraform_has_no_previous_account_id() -> None:
    terraform = "\n".join(path.read_text() for path in TERRAFORM.glob("*.tf"))

    assert "264040538379" not in terraform


def test_lambda_execution_role_is_required_and_validated() -> None:
    variables = (TERRAFORM / "variables.tf").read_text()
    role_block = variables.split('variable "lambda_execution_role_arn"', maxsplit=1)[1]

    assert "default" not in role_block
    assert "validation" in role_block
    assert "iam::[0-9]{12}:role/" in role_block


def test_aws_region_is_required_and_validated() -> None:
    variables = (TERRAFORM / "variables.tf").read_text()
    region_block = variables.split('variable "aws_region"', maxsplit=1)[1].split(
        'variable "lambda_function_name"', maxsplit=1
    )[0]

    assert "default" not in region_block
    assert "validation" in region_block
