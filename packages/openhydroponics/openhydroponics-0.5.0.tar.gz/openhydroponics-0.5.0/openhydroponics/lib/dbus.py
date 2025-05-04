from typing import Any
from dbus_fast import Variant

def variant_from_val(value: Any):
    if isinstance(value, bool):
        return Variant("b", value)
    if isinstance(value, int):
        return Variant("i", value)
    if isinstance(value, float):
        return Variant("d", value)
    if isinstance(value, str):
        return Variant("s", value)
    raise ValueError(f"Unsupported type {type(value)}")


def dict_to_variant(d: dict[str, Any]) -> dict[str, Variant]:
    return {key: variant_from_val(value) for key, value in d.items()}

def unpack_variant(variant: Variant) -> Any:
    """
    Unpack a D-Bus Variant to its underlying value.
    """
    return {key: item.value for key, item in variant.items()}
