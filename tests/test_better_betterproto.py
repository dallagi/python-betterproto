from __future__ import annotations

from typing import Any, Self
import pytest

from enum import Enum, auto
from tests.output_betterproto import simple as betterproto_simple_pb2

from tests.output_reference.simple import simple_pb2


# nested messages
# Both binary & JSON serialization is built-in --> orjson
# Enums
# Dataclasses
# async/await
# Timezone-aware datetime and timedelta objects
# Relative imports
# Mypy type checking


class Unique:
    ...

DEFAULT = Unique()

class OurTestEnum(Enum):
    UNSPECIFIED = 0
    ONE = 1
    TWO = 2

class OurSibling:
    def __init__(
        self,
        field: int = 0
    ) -> None:
        self.instance = simple_pb2.Sibling(field=field)

    @classmethod
    def from_instance(cls, instance: simple_pb2.Sibling) -> Self:
        obj = cls.__new__(cls)
        obj.instance = instance

        return obj

    @property
    def field(self) -> int:
        return self.instance.field

    @field.setter
    def field(self, value: int) -> None:
        self.instance.field = value

    def __bytes__(self) -> bytes:
        return self.instance.SerializeToString()

    @classmethod
    def parse(cls, binary_payload: bytes) -> Self:
        result = cls()
        result.instance.ParseFromString(binary_payload)

        return result


class OurTest:
    def __init__(
        self,
        field: int = 0,
        optional_field: int | None = None,
        enum_field: OurTestEnum = OurTestEnum.UNSPECIFIED,
            # add other fields
    ) -> None:
        self.instance = simple_pb2.Test(field=field, enum_field=enum_field.value)
        if optional_field is not None:
            self.instance.optional_field = optional_field

        # TODO:
        # - parse classmethod? betterproto doesn't
        # - how to set default values for nested objects 

    @classmethod
    def from_instance(cls, instance: simple_pb2.Test) -> Self:
        obj = cls.__new__(cls)
        obj.instance = instance

        return obj

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
    def int_variant(self) -> int:
        if not self.instance.HasField("int_variant"):
            raise AttributeError()

        return self.instance.int_variant

    @int_variant.setter
    def int_variant(self, value: int) -> None:
        self.instance.int_variant = value

    @property
    def string_variant(self) -> str:
        if not self.instance.HasField("string_variant"):
            raise AttributeError()

        return self.instance.string_variant

    @string_variant.setter
    def string_variant(self, value: str) -> None:
        self.instance.string_variant = value

    @property
    def sibling(self) -> OurSibling:
        return OurSibling.from_instance(self.instance.sibling)

    @sibling.setter
    def sibling(self, value: OurSibling) -> None:
        self.instance.sibling.CopyFrom(value.instance)

    def __bytes__(self) -> bytes:
        return self.instance.SerializeToString()

    @classmethod
    def parse(cls, binary_payload: bytes) -> Self:
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

    message.string_variant = "test"
    assert "test" == message.string_variant


def test_raises_attribute_error_when_accessing_unset_oneof_fields():
    google_serialized = simple_pb2.Test(int_variant=123).SerializeToString()
    message = OurTest.parse(google_serialized)

    with pytest.raises(AttributeError):
        message.string_variant

    message.string_variant = "test"
    with pytest.raises(AttributeError):
        message.int_variant


def test_can_match_over_oneof_fields():
    google_serialized = simple_pb2.Test(int_variant=123).SerializeToString()
    message = OurTest.parse(google_serialized)

    match message:
        case OurTest(string_variant=value):
            pytest.fail("Should not match over string variant when int variant is set")
        case OurTest(int_variant=value):
            assert 123 == value
        case _:
            pytest.fail("Should have matched over int variant")

def test_handles_nested_messages():
    google_serialized = simple_pb2.Test(sibling=simple_pb2.Sibling(field=123)).SerializeToString()
    message = OurTest.parse(google_serialized)

    assert 123 == message.sibling.field

    message.sibling.field = 234
    assert 234 == message.sibling.field

    message.sibling = OurSibling(field=111)
    assert 111 == message.sibling.field


def test_stable_instance_in_nested_message():
    google_serialized = simple_pb2.Test(sibling=simple_pb2.Sibling(field=123)).SerializeToString()
    message = OurTest.parse(google_serialized)

    sibling1 = message.sibling
    sibling2 = message.sibling

    assert sibling1 != sibling2
    assert sibling1.instance == sibling2.instance
