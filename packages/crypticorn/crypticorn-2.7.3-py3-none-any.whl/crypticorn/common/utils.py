from typing import Any, Union
from decimal import Decimal
import string
import random
from fastapi import status
from typing_extensions import deprecated

from crypticorn.common import ApiError, HTTPException, ExceptionContent


def throw_if_none(
    value: Any,
    exception: ExceptionContent = ExceptionContent(error=ApiError.OBJECT_NOT_FOUND),
) -> None:
    """Throws an FastAPI HTTPException if the value is None. https://docs.python.org/3/library/stdtypes.html#truth-value-testing"""
    if value is None:
        raise HTTPException(content=exception)


def throw_if_falsy(
    value: Any,
    exception: ExceptionContent = ExceptionContent(error=ApiError.OBJECT_NOT_FOUND),
) -> None:
    """Throws an FastAPI HTTPException if the value is False. https://docs.python.org/3/library/stdtypes.html#truth-value-testing"""
    if not value:
        raise HTTPException(content=exception)


def gen_random_id(length: int = 20) -> str:
    """Generate a random base62 string (a-zA-Z0-9) of specified length.
    Kucoin max 40, bingx max 40"""
    charset = string.ascii_letters + string.digits
    return "".join(random.choice(charset) for _ in range(length))


@deprecated("Use math.isclose instead. Will be removed in a future version.")
def is_equal(
    a: float | Decimal,
    b: float | Decimal,
    rel_tol: float = 1e-9,
    abs_tol: float = 0.0,
) -> bool:
    """
    Compare two Decimal numbers for approximate equality.
    """
    if not isinstance(a, Decimal):
        a = Decimal(str(a))
    if not isinstance(b, Decimal):
        b = Decimal(str(b))

    # Convert tolerances to Decimal
    return Decimal(abs(a - b)) <= max(
        Decimal(str(rel_tol)) * max(abs(a), abs(b)), Decimal(str(abs_tol))
    )


def optional_import(module_name: str, extra_name: str) -> Any:
    """
    Import a module optionally.
    """
    try:
        return __import__(module_name)
    except ImportError as e:
        extra = f"[{extra_name}]"
        raise ImportError(
            f"Optional dependency '{module_name}' is required for this feature. "
            f"Install it with: pip install crypticorn{extra}"
        ) from e
