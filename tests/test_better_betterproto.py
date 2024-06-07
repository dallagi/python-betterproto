from tests.output_betterproto.simple import Test

from tests.output_reference.simple import simple_pb2


# TODO: optional fields
# TODO: enums

# which_one_of
# Both binary & JSON serialization is built-in --> orjson
# Enums
# Dataclasses
# async/await
# Timezone-aware datetime and timedelta objects
# Relative imports
# Mypy type checking


class OurTest:
    def __init__(
        self,
        field: int = 0
    ) -> None:
        self.instance = simple_pb2.Test(field=field)

    @property
    def field(self) -> int:
        return self.instance.field

    @field.setter
    def field(self, field: int) -> None:
        self.instance.field = field

    def __bytes__(self) -> bytes:
        return self.instance.SerializeToString()


def test_serializes_correctly():
    serialized = bytes(Test(field=123))
    google_serialized = simple_pb2.Test(field=123).SerializeToString()

    instance = OurTest()
    print(instance.field)

    assert google_serialized == serialized
