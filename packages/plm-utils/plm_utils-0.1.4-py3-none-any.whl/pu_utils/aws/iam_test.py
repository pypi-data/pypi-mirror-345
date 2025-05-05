import json
import os

from ward import test

from pu_utils.namer import Namer

os.environ["AWS_REGION"] = "ap-southeast-1"


for policy_name, method, args, expected_name, expected_actions, expected_resource in [
    (
        "Lambda log",
        "lambda_log_policy",
        ["my-func"],
        "dev-role-policy-apse1-lambda-log",
        [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
        ],
        "arn:aws:logs:ap-southeast-1:012345678910:log-group:/aws/lambda/my-func:*",
    ),
    (
        "Lambda VPC",
        "lambda_vpc_policy",
        [],
        "dev-role-policy-apse1-lambda-vpc",
        [
            "ec2:CreateNetworkInterface",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DeleteNetworkInterface",
            "ec2:AssignPrivateIpAddresses",
            "ec2:UnassignPrivateIpAddresses",
        ],
        "*",
    ),
    (
        "Lambda invoke",
        "lambda_invoke_policy",
        ["my-func"],
        "dev-role-policy-apse1-lambda-invoke",
        [
            "lambda:InvokeFunction",
            "lambda:InvokeAsync",
        ],
        "arn:aws:lambda:ap-southeast-1:012345678910:function:my-func",
    ),
    (
        "SSM Parameters Store reader",
        "ssm_params_policy",
        [],
        "dev-role-policy-apse1-ssm-params",
        [
            "ssm:GetParameter",
            "ssm:GetParameters",
            "ssm:GetParametersByPath",
        ],
        "*",
    ),
    (
        "SecretsManager reader",
        "secrets_manager_policy",
        [],
        "dev-role-policy-apse1-secretsmanager",
        ["secretsmanager:GetSecretValue"],
        "*",
    ),
    (
        "SES",
        "ses_policy",
        ["me@localhost"],
        "dev-role-policy-apse1-ses",
        ["ses:SendEmail"],
        "arn:aws:ses:ap-southeast-1:012345678910:identity/me@localhost",
    ),
    (
        "KMS",
        "kms_policy",
        [],
        "dev-role-policy-apse1-kms",
        [
            "kms:GenerateDataKey",
            "kms:Encrypt",
            "kms:Decrypt",
        ],
        "arn:aws:kms:ap-southeast-1:012345678910:key/*",
    ),
    (
        "S3",
        "s3_policy",
        ["s3-obj", "my-bucket"],
        "dev-role-policy-apse1-s3-obj",
        ["s3:*"],
        "arn:aws:s3:::my-bucket/*",
    ),
]:

    @test(f"{policy_name} reader policy generation")
    def _(
        method: str = method,
        args: list = args,
        expected_name: str = expected_name,
        expected_actions: list[str] = expected_actions,
        expected_resource: str = expected_resource,
    ) -> None:
        from pu_utils.aws.iam import PolicyFactory

        factory = PolicyFactory(Namer("dev", "apse1"), aws_account_id="012345678910")
        policy = getattr(factory, method)(*args)

        assert policy.name == expected_name

        policy_json = json.loads(policy.policy)
        expected_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": expected_actions,
                    "Effect": "Allow",
                    "Resource": expected_resource,
                }
            ],
        }
        assert policy_json == expected_json


@test("Policy for S3 bucket with restricted prefix and path")
def _() -> None:
    from pu_utils.aws.iam import PolicyFactory

    factory = PolicyFactory(Namer("dev", "apse1"), aws_account_id="012345678910")
    policy = factory.s3_policy("email-templates", "emails", prefix="pre")

    assert policy.name == "dev-role-policy-apse1-email-templates"

    policy_json = json.loads(policy.policy)
    expected_json = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": ["s3:*"],
                "Effect": "Allow",
                "Resource": "arn:aws:s3:::emails/pre/*",
            }
        ],
    }
    assert policy_json == expected_json
