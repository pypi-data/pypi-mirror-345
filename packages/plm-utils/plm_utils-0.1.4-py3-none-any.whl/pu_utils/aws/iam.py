import json
import os
from collections.abc import Sequence
from dataclasses import dataclass

from pulumi import Input, Output, ResourceOptions
from pulumi_aws.iam import (
    GetPolicyDocumentStatementArgs,
    GetPolicyDocumentStatementPrincipalArgs,
    RoleInlinePolicyArgs,
    get_policy_document,
)
from pulumi_aws.lambda_ import Permission

from pu_utils.namer import Namer

AWS_REGION = os.environ["AWS_REGION"]


def create_lambda_invoke_permission(
    name: str,
    function_name: Input[str],
    gateway_execution_arn: Input[str],
    path: Input[str] = "*/*",
    opts: ResourceOptions | None = None,
) -> Permission:
    return Permission(
        name,
        action="lambda:invokeFunction",
        function=function_name,
        principal="apigateway.amazonaws.com",
        source_arn=Output.concat(gateway_execution_arn, "/", path),
        opts=opts,
    )


def policy_json(*, actions: Sequence[str], resource: str, allow: bool = True) -> str:
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": actions,
                    "Effect": "Allow" if allow else "Deny",
                    "Resource": resource,
                }
            ],
        }
    )


def assume_role_policy() -> str:
    return get_policy_document(
        statements=[
            GetPolicyDocumentStatementArgs(
                effect="Allow",
                principals=[
                    GetPolicyDocumentStatementPrincipalArgs(
                        type="Service",
                        identifiers=["lambda.amazonaws.com"],
                    )
                ],
                actions=["sts:AssumeRole"],
            )
        ]
    ).json


@dataclass
class PolicyFactory:
    """A factory to quickly create policies following convention"""

    namer: Namer
    aws_account_id: Input[str]

    def lambda_log_policy(self, function_name: str) -> RoleInlinePolicyArgs:
        path = f"/aws/lambda/{function_name}:*"
        resource = f"arn:aws:logs:{AWS_REGION}:{self.aws_account_id}:log-group:{path}"
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("lambda-log"),
            policy=policy_json(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resource=resource,
            ),
        )

    def lambda_vpc_policy(self) -> RoleInlinePolicyArgs:
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("lambda-vpc"),
            policy=policy_json(
                actions=[
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "ec2:AssignPrivateIpAddresses",
                    "ec2:UnassignPrivateIpAddresses",
                ],
                resource="*",
            ),
        )

    def lambda_invoke_policy(self, function_name: str) -> RoleInlinePolicyArgs:
        resource = f"arn:aws:lambda:{AWS_REGION}:{self.aws_account_id}:function:{function_name}"
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("lambda-invoke"),
            policy=policy_json(
                actions=[
                    "lambda:InvokeFunction",
                    "lambda:InvokeAsync",
                ],
                resource=resource,
            ),
        )

    def secrets_manager_policy(self) -> RoleInlinePolicyArgs:
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("secretsmanager"),
            policy=policy_json(
                actions=[
                    "secretsmanager:GetSecretValue",
                ],
                resource="*",
            ),
        )

    def ssm_params_policy(self) -> RoleInlinePolicyArgs:
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("ssm-params"),
            policy=policy_json(
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath",
                ],
                resource="*",
            ),
        )

    def ses_policy(self, sender: str) -> RoleInlinePolicyArgs:
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("ses"),
            policy=policy_json(
                actions=[
                    "ses:SendEmail",
                    "ses:SendRawEmail",
                ],
                resource=f"arn:aws:ses:{AWS_REGION}:{self.aws_account_id}:identity/{sender}",
            ),
        )

    def sms_policy(self) -> RoleInlinePolicyArgs:
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("sms"),
            policy=policy_json(
                actions=[
                    "sns:Publish",
                ],
                resource="*",
            ),
        )

    def kms_policy(self) -> RoleInlinePolicyArgs:
        resource = f"arn:aws:kms:{AWS_REGION}:{self.aws_account_id}:key/*"
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy("kms"),
            policy=policy_json(
                actions=[
                    "kms:GenerateDataKey",
                    "kms:Encrypt",
                    "kms:Decrypt",
                ],
                resource=resource,
            ),
        )

    def s3_policy(
        self,
        name: str,
        bucket: str,
        *,
        prefix: str | None = None,
        path: str = "*",
    ) -> RoleInlinePolicyArgs:
        path = path or "*"
        if prefix:
            path = f"{prefix}/{path}"
        return RoleInlinePolicyArgs(
            name=self.namer.role_policy(name),
            policy=policy_json(
                actions=[
                    "s3:*",
                ],
                resource=f"arn:aws:s3:::{bucket}/{path}",
            ),
        )

    def email_policies(
        self,
        sender: str,
        email_bucket: str,
        email_prefix: str,
    ) -> list[RoleInlinePolicyArgs]:
        return [
            self.ses_policy(sender),
            self.s3_policy("email-templates", email_bucket, prefix=email_prefix),
            # Needed for decrypting S3 objects
            self.kms_policy(),
        ]
