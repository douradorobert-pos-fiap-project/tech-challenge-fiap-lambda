variable "aws_region" {
  description = "AWS region where the infrastructure will be deployed"
  type        = string

  validation {
    condition     = can(regex("^[a-z]{2}(-gov)?-[a-z]+-[0-9]+$", var.aws_region))
    error_message = "aws_region must be a valid AWS region name."
  }
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "CpfValidatorTest"
}

variable "lambda_execution_role_arn" {
  description = "ARN of existing IAM role for Lambda execution"
  type        = string

  validation {
    condition     = can(regex("^arn:aws[a-zA-Z-]*:iam::[0-9]{12}:role/.+$", var.lambda_execution_role_arn))
    error_message = "lambda_execution_role_arn must be an AWS IAM role ARN."
  }
}
