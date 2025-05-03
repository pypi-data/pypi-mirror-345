from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from functools import wraps
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from maleo_foundation.models.responses import BaseResponses
from maleo_foundation.models.transfers.results.service.general import BaseServiceGeneralResultsTransfers
from maleo_foundation.models.transfers.results.service.query import BaseServiceQueryResultsTransfers
from maleo_foundation.utils.logger import BaseLogger, LoggerFactory

class BaseExceptions:
    @staticmethod
    async def validation_exception_handler(request:Request, exc:RequestValidationError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=BaseResponses.ValidationError(other=exc.errors()).model_dump())

    @staticmethod
    async def http_exception_handler(request:Request, exc:StarletteHTTPException):
        if exc.status_code == 404:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=BaseResponses.NotFound().model_dump())

        #* Handle other HTTP exceptions normally
        return None

    @staticmethod
    def database_exception_handler(
        operation:str,
        logger:Optional[BaseLogger] = None,
        logger_factory:Optional[LoggerFactory] = None,
        fail_result_class:type[BaseServiceQueryResultsTransfers.Fail] = BaseServiceQueryResultsTransfers.Fail
    ):
        """Decorator to handle database-related exceptions consistently."""
        if logger is not None and logger_factory is not None:
            raise RuntimeError("Only one of 'logger' or 'logger_factory' should be provided, not both.")
        if logger is None and logger_factory is None:
            raise RuntimeError("One of 'logger' or 'logger_factory' must be provided.")
        logger = logger or logger_factory()
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except SQLAlchemyError as e:
                    logger.error("Database error occurred while %s: '%s'", operation, str(e), exc_info=True)
                    return fail_result_class(
                        message=f"Failed {operation}",
                        description=f"A database error occurred while {operation}. Please try again later or contact administrator.",
                        other="Database operation failed"
                    )
                except Exception as e:
                    logger.error("Unexpected error occurred while %s: '%s'", operation, str(e), exc_info=True)
                    return fail_result_class(
                        message=f"Failed {operation}",
                        description=f"An unexpected error occurred while {operation}. Please try again later or contact administrator.",
                        other="Internal processing error"
                    )
            return wrapper
        return decorator

    @staticmethod
    def service_exception_handler(
        operation:str,
        logger:Optional[BaseLogger] = None,
        logger_factory:Optional[LoggerFactory] = None,
        fail_result_class:type[BaseServiceGeneralResultsTransfers.Fail] = BaseServiceGeneralResultsTransfers.Fail
    ):
        """Decorator to handle service-related exceptions consistently."""
        if logger is not None and logger_factory is not None:
            raise RuntimeError("Only one of 'logger' or 'logger_factory' should be provided, not both.")
        if logger is None and logger_factory is None:
            raise RuntimeError("One of 'logger' or 'logger_factory' must be provided.")
        logger = logger or logger_factory()
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error("Unexpected error occurred while %s: '%s'", operation, str(e), exc_info=True)
                    return fail_result_class(
                        message=f"Failed {operation}",
                        description=f"An unexpected error occurred while {operation}. Please try again later or contact administrator.",
                        other="Internal processing error"
                    )
            return wrapper
        return decorator