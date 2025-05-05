import pulumi
from pulumi import ComponentResource, Input, Output, ResourceOptions
from pulumi_aws.apigateway import (
    Integration,
    IntegrationResponse,
    Method,
    MethodResponse,
    Resource,
)


def _cors_integration_headers() -> dict[str, str]:
    cors_methods = "OPTIONS,GET,POST,PUT,PATCH,DELETE"
    cors_headers = ",".join(  # noqa: FLY002
        [
            "Content-Type",
            "X-Amz-Date",
            "Authorization",
            "X-Api-Key",
            "X-Amz-Security-Token",
            "X-Amz-User-Agent",
            "X-Amzn-Trace-Id",
            "Content-Encoding",
            "Accept-Encoding",
        ]
    )
    return {
        "method.response.header.Access-Control-Allow-Headers": f"'{cors_headers}'",
        "method.response.header.Access-Control-Allow-Methods": f"'{cors_methods}'",
        "method.response.header.Access-Control-Allow-Origin": "'*'",
    }


class RestCorsResource(ComponentResource):
    @property
    def id(self) -> Output[str]:
        return self._resource.id

    def __init__(
        self,
        name: str,
        path_segment: Input[str],
        api_id: Input[str],
        parent_id: Input[str],
        opts: ResourceOptions | None = None,
    ) -> None:
        """
        REST resource with OPTIONS mock integration to enable CORS

        :param path_segment:
            The AWS REST API resource name

        :param api_id:
            ID of the AWS REST API

        :param parent_id:
            ID of the parent AWS REST API resource
        """

        super().__init__("pu-utils:index:RestCorsResource", name, None, opts)
        self._resource = Resource(
            name,
            path_part=path_segment,
            rest_api=api_id,
            parent_id=parent_id,
            opts=ResourceOptions(parent=self),
        )
        self._cors_method = Method(
            f"{name}-cors",
            http_method="OPTIONS",
            authorization="NONE",
            rest_api=api_id,
            resource_id=self._resource.id,
            opts=ResourceOptions(parent=self),
        )
        self._cors_integration = Integration(
            f"{name}-cors",
            type="MOCK",
            request_templates={"application/json": "{statusCode: 200}"},
            http_method=self._cors_method.http_method,
            rest_api=api_id,
            resource_id=self._resource.id,
            opts=ResourceOptions(parent=self),
        )
        self._cors_response = MethodResponse(
            f"{name}-cors",
            rest_api=api_id,
            http_method=self._cors_method.http_method,
            resource_id=self._resource.id,
            status_code="200",
            response_parameters={
                "method.response.header.Access-Control-Allow-Headers": True,
                "method.response.header.Access-Control-Allow-Methods": True,
                "method.response.header.Access-Control-Allow-Origin": True,
            },
            opts=ResourceOptions(parent=self),
        )
        self._cors_integration_response = IntegrationResponse(
            f"{name}-cors",
            status_code="200",
            response_templates={"application/json": ""},
            response_parameters=_cors_integration_headers(),
            http_method=self._cors_integration.http_method,
            resource_id=self._resource.id,
            rest_api=api_id,
            opts=ResourceOptions(parent=self),
        )
        self.register_outputs({})

    def resources(self) -> list[pulumi.Resource]:
        """Return the resources aggregated in this component"""
        return [
            self._resource,
            self._cors_method,
            self._cors_integration,
            self._cors_response,
            self._cors_integration_response,
        ]


class RestResourceNode:
    """
    A tree node to represent REST API Gateway resources

    Full path of the resource will be used as ID. The actual Pulumi resource and
    AWS resource ID are also stored as part of the node data.
    """

    full_path: str
    """Full path to the endpoint without a trailing slash, for example: `/users`"""

    aws_resource_id: Input[str]
    """ID of the REST resource on AWS"""

    resource: RestCorsResource | None = None
    """
    The Pulumi resource corresponding to this REST resource

    This may be `None` if `aws_resource_id` is pointing to a REST API root resource
    """

    children: dict[str, "RestResourceNode"]
    """List of children indexed by subresource name for convenient access"""

    def __init__(self, full_path: str, aws_resource_id: Input[str]) -> None:
        self.full_path = full_path
        self.aws_resource_id = aws_resource_id
        self.children = {}


def create_route(
    root: RestResourceNode,
    api_id: Input[str],
    path: str,
    parent: pulumi.Resource,
) -> RestResourceNode:
    """Create resources as needed to have `path` as an API endpoint"""
    node = root
    accumulated_segments = []
    for segment in path.removesuffix("/").removeprefix("/").split("/"):
        accumulated_segments.append(segment)
        res_name = "_".join(accumulated_segments)
        full_path = "/" + "/".join(accumulated_segments)
        if segment not in node.children:
            res = RestCorsResource(
                res_name,
                path_segment=segment,
                api_id=api_id,
                parent_id=node.aws_resource_id,
                opts=ResourceOptions(parent=parent),
            )
            node.children[segment] = RestResourceNode(
                full_path=full_path,
                aws_resource_id=res.id,
            )
        node = node.children[segment]
    return node
