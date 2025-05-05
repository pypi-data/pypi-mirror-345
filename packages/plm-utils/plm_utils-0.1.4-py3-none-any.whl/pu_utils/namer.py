from collections.abc import Callable
from typing import ClassVar


class Namer:
    RESOURCE_TYPES: ClassVar = {
        "rest_api",
        "lambda_function",
        "lambda_layer",
        "authorizer",
        "role",
        "role_policy",
        "s3_zip_key",
    }

    def __init__(
        self,
        stage: str,
        region: str,
        instance: str | None = None,
        prefix: str | None = None,
    ) -> None:
        """
        A class to produce names following certain pattern

        All methods in this class takes in an optional description.
        This value will be put at the end of the name.
        """
        self._stage = stage
        self._region = region
        self._instance = instance
        self._prefix = prefix

    def __getattr__(self, name: str) -> Callable[[str | None], str]:
        return lambda desc: self._name(name.replace("_", "-"), desc)

    def lambda_function(self, description: str | None = None) -> str:
        return self._name("lambda", description)

    def lambda_layer(self, description: str | None = None) -> str:
        return self._name("layer", description)

    def s3_zip_key(self, name: str) -> str:
        return f"{self.instance}/{name}.zip"

    def _name(self, resource: str, description: str | None = None) -> str:
        if description:
            description = description.replace("_", "-")
        parts = [
            self._prefix,
            self._stage,
            resource,
            self._region,
            self._instance,
            description,
        ]
        return "-".join(part for part in parts if part)
