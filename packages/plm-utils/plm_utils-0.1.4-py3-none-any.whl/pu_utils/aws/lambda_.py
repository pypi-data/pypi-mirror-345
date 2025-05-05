from base64 import b64encode
from collections.abc import Iterable, Sequence
from hashlib import sha256
from pathlib import Path

from pulumi import ComponentResource, FileArchive, Input, Output, ResourceOptions
from pulumi_aws.cloudwatch import LogGroup
from pulumi_aws.iam import Role, RoleInlinePolicyArgs
from pulumi_aws.lambda_ import (
    Function,
    FunctionEnvironmentArgs,
    FunctionVpcConfigArgs,
    LayerVersion,
)
from pulumi_aws.s3 import BucketObjectv2

from pu_utils.aws.iam import PolicyFactory, assume_role_policy
from pu_utils.namer import Namer
from pu_utils.python_zip import pip_install, zip_source

# Helper functions


def b64sha256(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode()
    return b64encode(sha256(value).digest()).decode()


def create_source_zip(
    name: str,
    bucket: Input[str],
    source: str | Path,
    dest: str | Path,
    prefix: str | Path | None = None,
    key_prefix: str | None = None,
    opts: ResourceOptions | None = None,
) -> tuple[BucketObjectv2, str]:
    """
    Create a zip file containing the source code of the project located at `source`

    :param name:
        Resource name for the S3 object created for this zip file. This name is used
        by Pulumi only, not AWS

    :param bucket:
        The S3 bucket to store the result file

    :param key:
        Key for the S3 object to store this zip file

    :param source:
        The directory to be zipped

    :param dest:
        The directory to put the generated zip file into

    :param prefix:
        The prefix for files added to the zip file. For example, we can add `a.py`
        to the zip file as `x/a.py`

    :param key_prefix:
        The prefix for the S3 object created

    :return:
        A pair containing the S3 object and its base64-encoded hash ready to be used
        with Pulumi AWS
    """
    key_prefix = key_prefix or ""
    key = f"{key_prefix}{name}.zip"

    zip_path = zip_source(name, source, dest, prefix)
    source_hash = b64sha256(zip_path.read_bytes())
    s3_obj = BucketObjectv2(
        name,
        bucket=bucket,
        key=key,
        source=FileArchive(str(zip_path)),
        source_hash=source_hash,
        opts=opts,
    )
    return s3_obj, source_hash


class LambdaFunction(ComponentResource):
    @property
    def name(self) -> Output[str]:
        return self._function.name

    @property
    def arn(self) -> Output[str]:
        return self._function.arn

    @property
    def invoke_arn(self) -> Output[str]:
        return self._function.invoke_arn

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        namer: Namer,
        aws_account_id: str,
        build_dir: Path,
        deployment_bucket: Input[str],
        handler: Input[str],
        runtime: Input[str],
        source_dir: Path | None = None,
        source: BucketObjectv2 | None = None,
        source_hash: str | None = None,
        s3_key_prefix: str | None = None,
        log_retention_in_days: Input[int] | None = None,
        timeout: Input[int] = 6,
        memory_size: Input[int] = 1024,
        architectures: list[str] | None = None,
        vpc_config: FunctionVpcConfigArgs | None = None,
        layers: Sequence[Input[str]] | None = None,
        env_vars: dict[str, str] | None = None,
        policies: Iterable[RoleInlinePolicyArgs] | None = None,
        opts: ResourceOptions | None = None,
    ) -> None:
        """
        Wrapper to create a Lambda function with related resources

        A Lambda function has a dedicated log group and an execution role

        :param name:
            Resource name (internal to Pulumi)

        :param namer:
            Name provider, used to create names for AWS resources

        :param source_dir:
            Directory containing code of the Lambda function

        :param source:
            The S3 object representing the zip file containing the function code

            This option does not work with `source_dir`.

        :param build_dir:
            Directory to place build artifacts

        :param deployment_bucket:
            Name of the S3 bucket to upload zip file when deploy Lambda

        :param s3_key_prefix:
            Prefix for the S3 key of the uloaded zip file

        :param log_retention_in_days:
            Log retention in days for the Cloudwatch Log Group

        :param timeout:
            Function timeout in seconds

        :param memory_size:
            Function memory size. Larger value costs more but also give better CPU power

        :param architectures:
            Supported platform

        :param layers:
            ARN of the layers to link to this Lambda function

        :param policies:
            Extra policies for the execution role. By default it will only
            have access to the log and VPC (if VPC is used)
        """
        super().__init__("pu-utils:index:LambdaFunction", name, None, opts)
        self.function_name = namer.lambda_function(name)

        policy_factory = PolicyFactory(namer=namer, aws_account_id=aws_account_id)
        self._execution_role = self._create_execution_role(
            name,
            role_name=namer.role(name),
            policies=[
                policy_factory.lambda_log_policy(self.function_name),
                policy_factory.lambda_vpc_policy(),
                *(policies or []),
            ],
        )
        self._function = self._create_function(
            name,
            source_dir=source_dir,
            source=source,
            source_hash=source_hash,
            build_dir=build_dir,
            deployment_bucket=deployment_bucket,
            function_name=self.function_name,
            handler=handler,
            s3_key_prefix=s3_key_prefix,
            architectures=architectures,
            runtime=runtime,
            timeout=timeout,
            memory_size=memory_size,
            role_arn=self._execution_role.arn,
            vpc_config=vpc_config,
            layers=layers,
            env_vars=env_vars,
        )
        self._log_group = self._create_log_group(name, log_retention_in_days)
        self.register_outputs({})

    def _create_log_group(
        self,
        name: str,
        retention_in_days: Input[int] | None = None,
    ) -> LogGroup:
        return LogGroup(
            name,
            name=f"/aws/lambda/{self.function_name}",
            retention_in_days=retention_in_days,
            opts=ResourceOptions(parent=self),
        )

    def _create_execution_role(
        self,
        name: str,
        role_name: str,
        policies: Iterable[Input[RoleInlinePolicyArgs]],
    ) -> Role:
        return Role(
            name,
            name=role_name,
            assume_role_policy=assume_role_policy(),
            inline_policies=list(policies),
            opts=ResourceOptions(parent=self),
        )

    def _create_function(  # noqa: PLR0913
        self,
        name: str,
        *,
        source_dir: Path | None = None,
        source: BucketObjectv2 | None = None,
        source_hash: str | None = None,
        build_dir: Path,
        deployment_bucket: Input[str],
        function_name: str,
        role_arn: Input[str],
        handler: Input[str],
        runtime: Input[str],
        s3_key_prefix: str | None = None,
        architectures: Sequence[str] | None = None,
        timeout: Input[int] | None = None,
        memory_size: Input[int] | None = None,
        vpc_config: Input[FunctionVpcConfigArgs] | None = None,
        layers: Sequence[Input[str]] | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> Function:
        if source_dir:
            source, source_hash = create_source_zip(
                name,
                bucket=deployment_bucket,
                source=source_dir,
                dest=build_dir,
                key_prefix=s3_key_prefix,
                opts=ResourceOptions(parent=self),
            )
        if not source:
            raise ValueError("Need to provide `source_dir` or `(source, source_hash)`")
        return Function(
            name,
            name=function_name,
            role=role_arn,
            s3_bucket=deployment_bucket,
            s3_key=source.key,
            source_code_hash=source_hash,
            handler=handler,
            runtime=runtime,
            architectures=architectures,
            timeout=timeout,
            memory_size=memory_size,
            vpc_config=vpc_config,
            layers=layers,
            environment=FunctionEnvironmentArgs(variables=env_vars),
            opts=ResourceOptions(parent=self),
        )


class LambdaLayer(ComponentResource):
    @property
    def arn(self) -> Output[str]:
        return self._layer.arn

    def __init__(
        self,
        name: str,
        namer: Namer,
        source_dir: str | Path,
        build_dir: str | Path,
        deployment_bucket: Input[str],
        s3_key_prefix: str | None = None,
        architectures: Sequence[str] | None = None,
        runtime: str | None = None,
        opts: ResourceOptions | None = None,
    ) -> None:
        """
        A layer created from `requirements.txt`

        This component collect the dependencies and package into a layer, but it does
        not allow specifying arbitrary source. If you have custom packages, they should
        be added as dependencies of the Lambda functions instead, that way they will be
        included in the layer automatically too.
        """
        super().__init__("pu-utils:index:LambdaLayer", name, None, opts)

        # Collect dependencies
        source_dir = Path(source_dir)
        build_dir = Path(build_dir)
        target_dir = build_dir.joinpath(name)
        pip_install(source_dir.joinpath("requirements.txt"), target_dir)

        # then zip them
        source, source_hash = create_source_zip(
            name,
            bucket=deployment_bucket,
            source=target_dir,
            dest=build_dir,
            key_prefix=s3_key_prefix,
            prefix="python",
            opts=ResourceOptions(parent=self),
        )
        self._layer = LayerVersion(
            name,
            layer_name=namer.lambda_layer(name),
            s3_bucket=deployment_bucket,
            s3_key=source.key,
            source_code_hash=source_hash,
            compatible_architectures=architectures,
            compatible_runtimes=runtime,
            opts=ResourceOptions(parent=self),
        )


class ContainerLambda(ComponentResource):
    @property
    def name(self) -> Output[str]:
        return self._function.name

    @property
    def arn(self) -> Output[str]:
        return self._function.arn

    @property
    def invoke_arn(self) -> Output[str]:
        return self._function.invoke_arn

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        namer: Namer,
        aws_account_id: str,
        image_uri: Input[str],
        log_retention_in_days: Input[int] | None = None,
        timeout: Input[int] = 6,
        memory_size: Input[int] = 1024,
        architectures: list[str] | None = None,
        vpc_config: FunctionVpcConfigArgs | None = None,
        layers: Sequence[Input[str]] | None = None,
        env_vars: dict[str, str] | None = None,
        policies: Iterable[RoleInlinePolicyArgs] | None = None,
        opts: ResourceOptions | None = None,
    ) -> None:
        super().__init__("pu-utils:index:ContainerLambda", name, None, opts)
        self.function_name = namer.lambda_function(name)

        policy_factory = PolicyFactory(namer=namer, aws_account_id=aws_account_id)
        self._execution_role = self._create_execution_role(
            name,
            role_name=namer.role(name),
            policies=[
                policy_factory.lambda_log_policy(self.function_name),
                policy_factory.lambda_vpc_policy(),
                policy_factory.ssm_params_policy(),
                # For decrypting SSM parameters
                policy_factory.kms_policy(),
                *(policies or []),
            ],
        )
        self._function = self._create_function(
            name,
            image_uri=image_uri,
            function_name=self.function_name,
            architectures=architectures,
            timeout=timeout,
            memory_size=memory_size,
            role_arn=self._execution_role.arn,
            vpc_config=vpc_config,
            layers=layers,
            env_vars=env_vars,
        )
        self._log_group = self._create_log_group(name, log_retention_in_days)
        self.register_outputs({})

    def _create_log_group(
        self,
        name: str,
        retention_in_days: Input[int] | None = None,
    ) -> LogGroup:
        return LogGroup(
            name,
            name=f"/aws/lambda/{self.function_name}",
            retention_in_days=retention_in_days,
            opts=ResourceOptions(parent=self),
        )

    def _create_execution_role(
        self,
        name: str,
        role_name: str,
        policies: Iterable[Input[RoleInlinePolicyArgs]],
    ) -> Role:
        return Role(
            name,
            name=role_name,
            assume_role_policy=assume_role_policy(),
            inline_policies=list(policies),
            opts=ResourceOptions(parent=self),
        )

    def _create_function(  # noqa: PLR0913
        self,
        name: str,
        *,
        function_name: str,
        role_arn: Input[str],
        image_uri: Input[str],
        architectures: Sequence[str] | None = None,
        timeout: Input[int] | None = None,
        memory_size: Input[int] | None = None,
        vpc_config: Input[FunctionVpcConfigArgs] | None = None,
        layers: Sequence[Input[str]] | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> Function:
        return Function(
            name,
            publish=True,
            name=function_name,
            role=role_arn,
            image_uri=image_uri,
            package_type="Image",
            architectures=architectures,
            timeout=timeout,
            memory_size=memory_size,
            vpc_config=vpc_config,
            layers=layers,
            environment=FunctionEnvironmentArgs(variables=env_vars),
            opts=ResourceOptions(parent=self),
        )
