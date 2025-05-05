import os
from datetime import UTC, datetime
from typing import Literal

from pulumi import ComponentResource, Input, Output, Resource, ResourceOptions, export
from pulumi_aws.apigateway import (
    Authorizer,
    Deployment,
    Integration,
    Method,
    MethodSettings,
    MethodSettingsSettingsArgs,
    RestApi,
    RestApiEndpointConfigurationArgs,
    Stage,
)
from pulumi_aws.lambda_ import Function

from pu_utils.aws.api._resource import RestResourceNode, create_route
from pu_utils.aws.iam import create_lambda_invoke_permission
from pu_utils.namer import Namer


class RestEndpoint(ComponentResource):
    """Create a lambda-backed REST API endpoint"""

    def __init__(
        self,
        name: str,
        path: str,
        lambda_version: str,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        api_id: Input[str],
        gateway_execution_arn: Input[str],
        resource_id: Input[str],
        function: Function,
        authorizer_id: Input[str] | None = None,
        opts: ResourceOptions | None = None,
    ) -> None:
        super().__init__("pu-utils:index:RestEndpoint", name, None, opts)
        self.function = function
        self._path = path
        self._gateway_execution_arn = gateway_execution_arn
        self.method = Method(
            name,
            authorization="CUSTOM" if authorizer_id else "NONE",
            authorizer_id=authorizer_id,
            http_method=method,
            rest_api=api_id,
            resource_id=resource_id,
            opts=ResourceOptions(parent=self),
        )

        # Conditionally set the ARN
        lambda_arn = (
            self.function.invoke_arn
            if lambda_version == "0"
            else self.function.invoke_arn.apply(
                lambda arn: arn.replace("/invocations", f":{lambda_version}/invocations")
            )
        )

        # Debugging: Print the resolved ARN
        lambda_arn.apply(lambda resolved_arn: print(f"Resolved Lambda ARN: {resolved_arn}"))

        self.integration = Integration(
            name,
            # Must read from method to enforce creation order, reading from args may
            # cause integration being created before method and thus causing the error
            # `NotFoundException: Invalid Method identifier specified`
            http_method=self.method.http_method,
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=lambda_arn,  # Use the conditionally resolved ARN
            rest_api=api_id,
            resource_id=resource_id,
            opts=ResourceOptions(parent=self),
        )
        self.register_outputs({})


    def resources(self) -> list[Resource]:
        return [self.integration, self.method]


class RestGateway(ComponentResource):
    @property
    def id(self) -> Output[str]:
        return self._api.id

    @property
    def execution_arn(self) -> Output[str]:
        return self._api.execution_arn

    def __init__(
        self,
        name: str,
        namer: Namer,
        authorizer_func: Function | None = None,
        gateway_id: Input[str] | None = None,
        opts: ResourceOptions | None = None,
    ) -> None:
        """
        Create a REST Gateway (API Gateway v1)

        Set `gateway_id` to use existing gateway or leave it `None` to create a new one.

        `finish()` must be called after endpoints are added
        """
        super().__init__("pu-utils:index:RestGateway", name, None, opts)

        self._namer = namer
        self._api = self._find_or_create_api(gateway_id)
        self._authorizer = (
            self._create_authorizer(authorizer_func) if authorizer_func else None
        )
        self._root_resource = RestResourceNode(
            full_path="/",
            aws_resource_id=self._api.root_resource_id,
        )
        self._endpoints = []
        # May also add catch-all route and return mock 404

    def add_endpoint(
        self,
        name: str,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        path: str,
        function: Function,
        lambda_version: str,
        *,
        authorized: bool = True,
    ) -> None:
        self._endpoints.append(
            RestEndpoint(
                name,
                path=path,
                resource_id=self._route_resource_id(path),
                lambda_version=lambda_version,
                method=method,
                api_id=self._api.id,
                gateway_execution_arn=self._api.execution_arn,
                function=function,
                authorizer_id=self._authorizer.id
                if authorized and self._authorizer
                else None,
                opts=ResourceOptions(parent=self),
            )
        )

    def finish(self, stage: Input[str]) -> None:
        deployment = Deployment(
            "api",
            rest_api=self._api.id,
            triggers={"redeployment": _deployment_hash()},
            opts=ResourceOptions(
                parent=self,
                depends_on=[
                    *_collect_resources_from_resource_tree(self._root_resource),
                    *_collect_resources_from_endpoints(self._endpoints),
                ],
            ),
        )
        self.stage = Stage(
            "api",
            stage_name=stage,
            rest_api=self._api.id,
            deployment=deployment.id,
            opts=ResourceOptions(parent=self),
        )
        MethodSettings(
            "api",
            rest_api=self._api.id,
            stage_name=self.stage.stage_name,
            method_path="*/*",
            settings=MethodSettingsSettingsArgs(logging_level="ERROR"),
            opts=ResourceOptions(parent=self),
        )
        self._export_outputs()
        self.register_outputs({})

    def _find_or_create_api(self, api_id: Input[str] | None) -> RestApi:
        if api_id:
            return RestApi.get("api", id=api_id)
        return RestApi(
            "api",
            name=self._namer.rest_api(""),
            endpoint_configuration=RestApiEndpointConfigurationArgs(types="REGIONAL"),
            opts=ResourceOptions(parent=self),
        )

    def _create_authorizer(self, authorizer_func: Function) -> Authorizer:
        authorizer = Authorizer(
            "authorizer",
            rest_api=self._api.id,
            authorizer_result_ttl_in_seconds=300,
            authorizer_uri=authorizer_func.arn.apply(_authorizer_invoke_uri),
            name=self._namer.authorizer("api"),
            type="TOKEN",
            identity_source="method.request.header.Authorization",
            opts=ResourceOptions(parent=self),
        )
        create_lambda_invoke_permission(
            "authorizer",
            authorizer_func.name,
            gateway_execution_arn=self._api.execution_arn,
            path=authorizer.id.apply(lambda id: f"authorizers/{id}"),
            opts=ResourceOptions(parent=self),
        )
        return authorizer

    def _route_resource_id(self, path: str) -> Input[str]:
        return create_route(
            self._root_resource,
            api_id=self._api.id,
            path=path,
            parent=self,
        ).aws_resource_id

    def _export_outputs(self) -> None:
        export("gateway_stage_url", self.stage.invoke_url)


def _authorizer_invoke_uri(arn: str) -> str:
    region = os.environ["AWS_REGION"]
    return f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations"


def _deployment_hash() -> str:
    return str(datetime.now(tz=UTC))


def _collect_resources_from_endpoints(endpoints: list[RestEndpoint]) -> list[Resource]:
    resources = []
    for endpoint in endpoints:
        resources.extend(endpoint.resources())
    return resources


def _collect_resources_from_resource_tree(root: RestResourceNode) -> list[Resource]:
    stacks = [root]
    resources = []
    while stacks:
        node = stacks.pop()
        if node.resource:
            resources.extend(node.resource.resources())
        stacks.extend(node.children.values())
    return resources
