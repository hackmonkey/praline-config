from dataclasses import dataclass
from typing import Type

from praline.config.model import HasInit, HasReify, WrappedValue, SecureValue


class MyClass(HasInit):
    def __init__(self, your_value: str, *args, **kwargs):
        self.your_value = your_value
        self.my_value: str | None = None
        super().__init__(*args, **kwargs)

    def init(self):
        self.my_value = "Something else."
        super().init()


@dataclass
class MyDataClass(HasInit):
    instance_field: str | None = None
    custom_field: str | None = None

    def init(self):
        self.instance_field = "A very important string."
        super().init()


def test_has_init():
    my_class = MyClass(your_value="Theirs.")
    assert my_class.my_value == "Something else."
    assert my_class.your_value == "Theirs."

    my_dataclass = MyDataClass(custom_field="Mine.")
    assert my_dataclass.instance_field == "A very important string."
    assert my_dataclass.custom_field == "Mine."


@dataclass
class ReifiableClass(HasReify):
    custom_field: str | None = None

    @classmethod
    def reify_type(cls) -> Type:
        return MyDataClass

    def reify(self) -> MyDataClass:
        return MyDataClass(custom_field=self.custom_field)


def test_has_reify():
    reifiable = ReifiableClass(custom_field="A rose by another name...")
    assert ReifiableClass.reify_type() == MyDataClass

    my_dataclass = reifiable.reify()
    # The definition for this ReifiableClass should populate the instance with the value it was constructed with.
    assert my_dataclass.custom_field == "A rose by another name..."
    # The init() function for `MyDataClass` should still populate this statically.
    assert my_dataclass.instance_field == "A very important string."


def test_wrapped_value():
    wrapped: WrappedValue = WrappedValue("Some string")
    assert wrapped.value() == "Some string"


class RedactedValue(SecureValue):
    mask_str: str = "REDACTED"


def test_secure_value():
    wrapped: SecureValue = SecureValue("Some string")
    assert wrapped.value() == "Some string"
    assert str(wrapped) == SecureValue.mask_str

    redacted: RedactedValue = RedactedValue("Some string")
    assert redacted.value() == "Some string"
    assert str(redacted) == "REDACTED"
