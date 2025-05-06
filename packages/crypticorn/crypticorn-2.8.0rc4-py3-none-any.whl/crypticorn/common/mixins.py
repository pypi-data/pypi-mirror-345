from enum import EnumMeta
import logging

logger = logging.getLogger("uvicorn")


class ValidateEnumMixin:
    """
    Mixin for validating enum values manually.

    ⚠️ Note:
    This does NOT enforce validation automatically on enum creation.
    It's up to the developer to call `Class.validate(value)` where needed.

    Usage:
        >>> class Color(ValidateEnumMixin, StrEnum):
        >>>     RED = "red"
        >>>     GREEN = "green"

        >>> Color.validate("red")     # True
        >>> Color.validate("yellow")  # False

    Order of inheritance matters — the mixin must come first.
    """

    @classmethod
    def validate(cls, value) -> bool:
        """Validate if a value is in the enum. True if so, False otherwise."""
        try:
            cls(value)
            return True
        except ValueError:
            return False

#This Mixin will be removed in a future version. And has no effect from now on
class ExcludeEnumMixin:
    """Mixin to exclude enum from OpenAPI schema. We use this to avoid duplicating enums when generating client code from the openapi spec."""

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        #schema.pop("enum", None)
        return schema


class ApiErrorFallback(EnumMeta):
    """Fallback for enum members that are not yet published to PyPI."""

    def __getattr__(cls, name):
        # Let Pydantic/internal stuff pass silently ! fragile
        if name.startswith("__"):
            raise AttributeError(name)
        logger.warning(
            f"Unknown enum member '{name}' - update crypticorn package or check for typos"
        )
        return cls.UNKNOWN_ERROR
