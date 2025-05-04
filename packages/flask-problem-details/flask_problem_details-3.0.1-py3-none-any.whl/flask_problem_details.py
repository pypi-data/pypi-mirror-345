from __future__ import annotations
from flask import Flask, Response
from flask_openapi3 import OpenAPI
from pydantic import BaseModel, Field, ValidationError, AnyUrl
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError
from typing import Union, Callable
import traceback

WITH_TRACEBACK : bool = False

def activate_traceback():
    """
    Activate the inclusion of traceback information in problem details.
    """
    global WITH_TRACEBACK
    WITH_TRACEBACK = True

def deactivate_traceback():
    """
    Deactivate the inclusion of traceback information in problem details.
    """
    global WITH_TRACEBACK
    WITH_TRACEBACK = False

def configure_app(app: Union[Flask, Callable[[dict],OpenAPI]], with_traceback: bool = False) -> Union[Flask, OpenAPI]:
    """
    Configure the Flask or OpenAPI app to handle ProblemDetailsError and other exceptions.

    Parameters
    ----------
    app : Union[Flask, Callable[[dict],OpenAPI]]
        The Flask or OpenAPI application instance to configure.
    with_traceback : bool, optional
        If True, include traceback information in the problem details (default is False).

    Returns
    -------
    Union[Flask, OpenAPI]
        The configured Flask or OpenAPI application instance.
    """
    def handle(error: ProblemDetailsError) -> Response:
        """
        Handle a ProblemDetailsError and return an HTTP response.

        Parameters
        ----------
        error : ProblemDetailsError
            The raised problem.

        Returns
        -------
        Response
            An HTTP response representing the problem details.
        """
        return error.problem.to_http_response()
    def handle_validation_error(error: ValidationError) -> Response:
        """
        Handle a ValidationError and return an HTTP response.

        Parameters
        ----------
        error : ValidationError
            The raised validation error.

        Returns
        -------
        Response
            An HTTP response representing the validation error details.
        """
        bad_request_exception = BadRequest(f"Validation Failed! Error count: {error.error_count()}")
        return handle(from_exception(bad_request_exception, extras={"errors": error.errors()}))
    def handle_exception(exception: Exception)-> Response:
        """
        Handle any exception and return an HTTP response.

        Parameters
        ----------
        exception : Exception
            The raised exception.

        Returns
        -------
        Response
            An HTTP response representing the exception details.
        """
        return handle(from_exception(exception))
    
    if with_traceback:
        activate_traceback()
    
    #app is always a callable object, more specific check on Flask class
    if not isinstance(app, Flask):
        app : OpenAPI = app(
            {"validation_error_status" : 400, 
                "validation_error_model" : ProblemDetails, 
                    "validation_error_callback": handle_validation_error})
    
    app.register_error_handler(ProblemDetailsError, handle)
    app.register_error_handler(Exception, handle_exception)
    
    return app

def from_exception(exception: Exception, extras: dict = {}) -> ProblemDetailsError:
    """
    Create a ProblemDetailsError from an exception.

    Parameters
    ----------
    exception : Exception
        The exception that caused the problem.
    extras : dict, optional
        Additional information to include in the problem details (default is {}).

    Returns
    -------
    ProblemDetailsError
        The created ProblemDetailsError instance.
    """
    problem = ProblemDetails(
        status=InternalServerError.code,
        title= InternalServerError.__name__,
        detail= str(exception),
        **extras
    )
    
    if isinstance(exception, HTTPException):
        problem.status = exception.code
        problem.title = exception.__class__.__name__
        problem.detail = exception.description
    
    return ProblemDetailsError(problem=problem, exception=exception)

class ProblemDetails(BaseModel, extra="allow"):
    status: int = Field(..., description = "HTTP status code")
    title: str  = Field(..., description = "A short, human-readable summary of the problem type")
    detail: Union[str|None]  = Field(None, description = "An human readable explanation specific to this occurrence of the problem")
    type: Union[AnyUrl|None]  = Field(None, description = "An absolute URI that identifies the problem type")
    instance: Union[AnyUrl|None] = Field(None, description = "An URI reference that identifies the specific occurrence of the problem")
    traceback : Union[str|None] = Field(None, description = "The stack trace of the problem")

    def to_dict(self, with_traceback: bool = None) -> dict:
        """
        Transform the ProblemDetailsError into a dictionary.

        Parameters
        ----------
        with_traceback : bool, optional
            If True, include the last exception traceback (default is None).

        Returns
        -------
        dict
            The problem details as a dictionary.
        """
        with_traceback: bool = WITH_TRACEBACK if with_traceback is None else with_traceback

        if with_traceback:
            self.traceback = traceback.format_exc()
        return self.model_dump(exclude_none=True)

    def to_json(self, with_traceback: bool = None) -> str:
        """
        Transform the ProblemDetailsError into a JSON string.

        Parameters
        ----------
        with_traceback : bool, optional
            If True, include the last exception traceback (default is None).

        Returns
        -------
        str
            The problem details as a JSON string.
        """
        with_traceback: bool = WITH_TRACEBACK if with_traceback is None else with_traceback

        if with_traceback:
            self.traceback = traceback.format_exc()
        return self.model_dump_json(exclude_none=True)

    def to_http_response(self, with_traceback: bool = None) -> Response:
        """
        Transform the ProblemDetailsError into an HTTP response.

        Parameters
        ----------
        with_traceback : bool, optional
            If True, include the last exception traceback (default is None).

        Returns
        -------
        Response
            The problem details as an HTTP response.
        """
        with_traceback: bool = WITH_TRACEBACK if with_traceback is None else with_traceback
        return Response(status=self.status, response=self.to_json(with_traceback),
                        mimetype="application/problem+json")

class ProblemDetailsError(Exception):

    def __init__(self, problem: ProblemDetails, exception: Exception = None):
        """
        Initialize a ProblemDetailsError.

        Parameters
        ----------
        problem : ProblemDetails
            The problem details.
        exception : Exception, optional
            The original exception that caused the problem (default is None).
        """
        self.problem: ProblemDetails = problem
        self.inner_exception: Exception = exception