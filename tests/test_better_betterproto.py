from enum import Enum, auto
from tests.output_betterproto.simple import Test, TestEnum

from tests.output_reference.simple import simple_pb2


# which_one_of
# nested messages
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

    @property
    def int_variant(self) -> int | None:
        if not self.instance.HasField("int_variant"):
            return None

        return self.instance.int_variant

    @int_variant.setter
    def int_variant(self, value: int) -> None:
        self.instance.int_variant = value

    @property
    def string_variant(self) -> str | None:
        if not self.instance.HasField("string_variant"):
            return None

        return self.instance.string_variant

    @string_variant.setter
    def string_variant(self, value: str) -> None:
        self.instance.string_variant = value

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
    serialized = bytes(OurTest(enum_field=OurTestEnum.ONE))
    google_serialized = simple_pb2.Test(
        enum_field=simple_pb2.TestEnum.ONE
    ).SerializeToString()

    assert google_serialized == serialized


def test_can_get_and_set_oneof_fields():
    google_serialized = simple_pb2.Test(int_variant=123).SerializeToString()
    message = OurTest.parse(google_serialized)

    assert 123 == message.int_variant
    assert None == message.string_variant

    message.string_variant = "test"

    assert None == message.int_variant
    assert "test" == message.string_variant
