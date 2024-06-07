from enum import Enum, auto
from tests.output_betterproto.simple import Test, TestEnum

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


class OurTestEnum(Enum):
    UNSPECIFIED = 0
    ONE = 1
    TWO = 2


class OurTest:
    def __init__(
        self,
        field: int = 0,
        optional_field: int | None = None,
        enum_field: OurTestEnum = OurTestEnum.UNSPECIFIED,
    ) -> None:
        self.instance = simple_pb2.Test(field=field, enum_field=enum_field.value)
        if optional_field is not None:
            self.instance.optional_field = optional_field

    @property
    def field(self) -> int:
        return self.instance.field

    @field.setter
    def field(self, value: int) -> None:
        self.instance.field = value

    @property
    def optional_field(self) -> int | None:
        if not self.instance.HasField("optional_field"):
            return None

        return self.instance.optional_field

    @optional_field.setter
    def optional_field(self, value: int) -> None:
        self.instance.optional_field = value

    @property
    def enum_field(self) -> OurTestEnum:
        return OurTestEnum(self.instance.enum_field)

    @enum_field.setter
    def enum_field(self, value: OurTestEnum) -> None:
        self.instance.enum_field = value.value

    def __bytes__(self) -> bytes:
        return self.instance.SerializeToString()

    @classmethod
    def parse(cls, binary_payload: bytes) -> "OurTest":
        result = cls()
        result.instance.ParseFromString(binary_payload)

        return result


def test_serializes_correctly():
    serialized = bytes(OurTest(field=123))
    google_serialized = simple_pb2.Test(field=123).SerializeToString()

    assert google_serialized == serialized


def test_handles_optional_fields():
    google_serialized_optional_set = simple_pb2.Test().SerializeToString()
    message_optional_set = OurTest.parse(google_serialized_optional_set)

    assert message_optional_set.optional_field is None

    google_serialized_optional_set = simple_pb2.Test(
        optional_field=123
    ).SerializeToString()
    message_optional_set = OurTest.parse(google_serialized_optional_set)

    assert 123 == message_optional_set.optional_field


def test_handles_enums():
    serialized = bytes(OurTestEnum.ONE)
    google_serialized = simple_pb2.TestEnum.ONE.to_bytes()

    assert google_serialized == serialized

    serialized = bytes(OurTest(enum_field=OurTestEnum.ONE))
    google_serialized = simple_pb2.Test(
        enum_field=simple_pb2.TestEnum.ONE
    ).SerializeToString()

    assert google_serialized == serialized
