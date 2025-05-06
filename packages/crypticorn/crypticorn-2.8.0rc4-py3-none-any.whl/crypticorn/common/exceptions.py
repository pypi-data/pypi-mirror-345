from typing import Optional, Dict, Any, Literal
from enum import StrEnum
from pydantic import BaseModel, Field
from fastapi import HTTPException as FastAPIHTTPException, Request, FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from crypticorn.common import ApiError, ApiErrorIdentifier, ApiErrorType, ApiErrorLevel
import logging

logger = logging.getLogger(__name__)


class ExceptionType(StrEnum):
    HTTP = "http"
    WEBSOCKET = "websocket"


class ExceptionDetail(BaseModel):
    """This is the detail of the exception. It is used to enrich the exception with additional information by unwrapping the ApiError into its components."""

    message: Optional[str] = Field(None, description="An additional error message")
    code: ApiErrorIdentifier = Field(..., description="The unique error code")
    type: ApiErrorType = Field(..., description="The type of error")
    level: ApiErrorLevel = Field(..., description="The level of the error")
    status_code: int = Field(..., description="The HTTP status code")
    details: Any = Field(None, description="Additional details about the error")


class ExceptionContent(BaseModel):
    """This is the detail of the exception. Pass an ApiError to the constructor and an optional human readable message."""

    error: ApiError = Field(..., description="The unique error code")
    message: Optional[str] = Field(None, description="An additional error message")
    details: Any = Field(None, description="Additional details about the error")

    def enrich(
        self, _type: Optional[ExceptionType] = ExceptionType.HTTP
    ) -> ExceptionDetail:
        return ExceptionDetail(
            message=self.message,
            code=self.error.identifier,
            type=self.error.type,
            level=self.error.level,
            status_code=(
                self.error.http_code
                if _type == ExceptionType.HTTP
                else self.error.websocket_code
            ),
            details=self.details,
        )


class HTTPException(FastAPIHTTPException):
    """A custom HTTP exception wrapper around FastAPI's HTTPException.
    It allows for a more structured way to handle errors, with a message and an error code. The status code is being derived from the detail's error.
        The ApiError class is the source of truth for everything. If the error is not yet implemented, there are fallbacks to avoid errors while testing.
    """

    def __init__(
        self,
        content: ExceptionContent,
        headers: Optional[Dict[str, str]] = None,
        _type: Optional[ExceptionType] = ExceptionType.HTTP,
    ):
        self.content = content
        self.headers = headers
        assert isinstance(content, ExceptionContent)
        body = content.enrich(_type)
        super().__init__(
            status_code=body.status_code,
            detail=body.model_dump(mode="json"),
            headers=headers,
        )


class WebSocketException(HTTPException):
    """A WebSocketException is to be used for WebSocket connections. It is a wrapper around the HTTPException class to maintain the same structure, but using a different status code.
    To be used in the same way as the HTTPException.
    """

    def __init__(
        self, content: ExceptionContent, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(content, headers, _type=ExceptionType.WEBSOCKET)

    @classmethod
    def from_http_exception(cls, http_exception: HTTPException):
        """This is a helper method to convert an HTTPException to a WebSocketException."""
        return WebSocketException(
            content=http_exception.content,
            headers=http_exception.headers,
        )


async def general_handler(request: Request, exc: Exception) -> JSONResponse:
    """This is the default exception handler for all exceptions."""
    body = ExceptionContent(message=str(exc), error=ApiError.UNKNOWN_ERROR)
    res = JSONResponse(
        status_code=body.enrich().status_code,
        content=HTTPException(content=body).detail,
    )
    logger.error(f"Response validation error: {res}")
    return res


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """This is the exception handler for all request validation errors."""
    body = ExceptionContent(message=str(exc), error=ApiError.INVALID_DATA_REQUEST)
    res = JSONResponse(
        status_code=body.enrich().status_code,
        content=HTTPException(content=body).detail,
    )
    logger.error(f"Response validation error: {res}")
    return res


async def response_validation_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    """This is the exception handler for all response validation errors."""
    body = ExceptionContent(message=str(exc), error=ApiError.INVALID_DATA_RESPONSE)
    res = JSONResponse(
        status_code=body.enrich().status_code,
        content=HTTPException(content=body).detail,
    )
    logger.error(f"Response validation error: {res}")
    return res


async def http_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """This is the exception handler for HTTPExceptions. It unwraps the HTTPException and returns the detail in a flat JSON response."""
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


def register_exception_handlers(app: FastAPI):
    """Utility to register serveral exception handlers in one go. Catches Exception, HTTPException and Data Validation errors, logs them and responds with a unified json body."""
    app.add_exception_handler(Exception, general_handler)
    app.add_exception_handler(FastAPIHTTPException, http_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(ResponseValidationError, response_validation_handler)


exception_response = {
    "default": {"model": ExceptionDetail, "description": "Error response"}
}
