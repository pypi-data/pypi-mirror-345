from ward import test

from pu_utils.namer import Namer

for stage, region, instance, prefix, description, expected in [
    ("dev", "apse1", None, None, None, "dev-api-apse1"),
    ("dev", "apse1", "main", None, None, "dev-api-apse1-main"),
    ("dev", "apse1", "main", "my-app", None, "my-app-dev-api-apse1-main"),
    ("dev", "apse1", "main", "my-app", "abc", "my-app-dev-api-apse1-main-abc"),
    ("dev", "apse1", "main", None, "abc", "dev-api-apse1-main-abc"),
    ("dev", "apse1", "main", None, None, "dev-api-apse1-main"),
    ("dev", "apse1", None, "pre", None, "pre-dev-api-apse1"),
    ("dev", "apse1", None, None, "desc", "dev-api-apse1-desc"),
]:

    @test("Name part combinations")
    def _(
        stage: str = stage,
        region: str = region,
        instance: str | None = instance,
        prefix: str | None = prefix,
        description: str | None = description,
        expected: str = expected,
    ) -> None:
        namer = Namer(stage, region, instance, prefix)
        assert namer.api(description) == expected


@test("_ is transformed to -")
def _() -> None:
    assert Namer("dev", "apse1").a_b_c("ex") == "dev-a-b-c-apse1-ex"


@test("'lambda_function' is mapped to 'lambda'")
def _() -> None:
    assert Namer("dev", "apse1").lambda_function() == "dev-lambda-apse1"


@test("'lambda_layer' is mapped to 'layer'")
def _() -> None:
    assert Namer("dev", "apse1").lambda_layer() == "dev-layer-apse1"
