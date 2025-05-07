from __future__ import annotations

import os.path
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast

import click
import flask
import flask.typing
import functions_framework
import gunicorn.app.base  # type: ignore[import-untyped]
from cloudevents.http.event import CloudEvent
from structlog.typing import FilteringBoundLogger
from typing_extensions import ParamSpec
from ucam_observe import get_structlog_logger  # type: ignore[import-untyped]
from ucam_observe.gunicorn import logconfig_dict  # type: ignore[import-untyped]
from werkzeug.exceptions import InternalServerError

from ucam_faas.exceptions import UCAMFAASException

if TYPE_CHECKING:
    from _typeshed.wsgi import WSGIApplication

P = ParamSpec("P")
T = TypeVar("T")

# As well as making a logger available this should setup logging before the flask app is created
logger: FilteringBoundLogger = get_structlog_logger(__name__)


def _common_function_wrapper(function: Callable[P, T]) -> Callable[P, T]:
    def _common_function_wrapper_internal(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return function(*args, **kwargs)
        except UCAMFAASException as exception:
            exception_name = exception.__class__.__name__

            logger.warning("function_failed_gracefully", exception_name=exception_name)

            raise InternalServerError(description=f"The function raised {exception_name}.")

        except Exception as exception:
            exception_name = exception.__class__.__name__

            logger.exception("function_failed_uncaught_exception", exception_name=exception_name)

            raise exception

    return _common_function_wrapper_internal


class RawEventHandlerFn(Protocol):
    def __call__(self, event: bytes, /) -> flask.typing.ResponseReturnValue | None: ...

    @property
    def __name__(self) -> str: ...


class RegisteredRawEventHandlerFn(Protocol):
    __wrapped__: RawEventHandlerFn

    def __call__(self, request: flask.Request, /) -> flask.typing.ResponseReturnValue: ...

    @property
    def __name__(self) -> str: ...


def raw_event(function: RawEventHandlerFn) -> RegisteredRawEventHandlerFn:
    @_common_function_wrapper
    def _raw_event_internal(request: flask.Request, /) -> flask.typing.ResponseReturnValue:
        return_value = function(request.data)

        if return_value is not None:
            return return_value

        return "", 200

    # Decorators must preserve the wrapped function identity because
    # functions_framework registers metadata against the __name__ of `function`.
    _raw_event_internal.__name__ = function.__name__
    _raw_event_internal = functions_framework.http(_raw_event_internal)

    _raw_event_internal = cast(RegisteredRawEventHandlerFn, _raw_event_internal)
    _raw_event_internal.__wrapped__ = function

    return _raw_event_internal


class CloudEventHandlerFn(Protocol):
    def __call__(self, event_data: Any, /) -> None: ...

    @property
    def __name__(self) -> str: ...


class RegisteredCloudEventHandlerFn(Protocol):
    __wrapped__: CloudEventHandlerFn

    def __call__(self, event: CloudEvent, /) -> None: ...

    @property
    def __name__(self) -> str: ...


def cloud_event(function: CloudEventHandlerFn) -> RegisteredCloudEventHandlerFn:
    @_common_function_wrapper
    def _cloud_event_internal(event: CloudEvent, /) -> None:
        return function(event.data)

    # Decorators must preserve the wrapped function identity because
    # functions_framework registers metadata against the __name__ of `function`.
    _cloud_event_internal.__name__ = function.__name__
    _cloud_event_internal = functions_framework.cloud_event(_cloud_event_internal)

    _cloud_event_internal = cast(RegisteredCloudEventHandlerFn, _cloud_event_internal)
    _cloud_event_internal.__wrapped__ = function

    return _cloud_event_internal


class FaaSGunicornApplication(gunicorn.app.base.Application):  # type: ignore[misc] # gunicorn is not typed # noqa: E501
    def __init__(self, app: WSGIApplication, host: str, port: int | str) -> None:
        self.host = host
        self.port = port
        self.app = app

        self.options = {
            "bind": "%s:%s" % (host, port),
            "workers": os.environ.get("WORKERS", 2),
            "threads": os.environ.get("THREADS", (os.cpu_count() or 1) * 4),
            "timeout": 0,
            "limit_request_line": 0,
            "logconfig_dict": logconfig_dict,
        }

        super().__init__()

    def load_config(self) -> None:
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self) -> WSGIApplication:
        return self.app


def _initialize_ucam_faas_app(target: str, source: str | Path | None, debug: bool) -> flask.Flask:
    app: flask.Flask = functions_framework.create_app(target, source)  # type: ignore[no-untyped-call] # noqa: E501

    app.logger.info("flask_app_created")

    @app.route("/healthy")
    @app.route("/status")
    def get_status() -> str:
        return "ok"

    return app


def run_ucam_faas(
    target: str, source: str | Path | None, host: str, port: int, debug: bool
) -> None:  # pragma: no cover
    app = _initialize_ucam_faas_app(target, source, debug)
    if debug:
        app.run(host, port, debug)
    else:
        server = FaaSGunicornApplication(app, host, port)
        server.run()


@click.command()
@click.option("--target", envvar="FUNCTION_TARGET", type=click.STRING, required=True)
@click.option("--source", envvar="FUNCTION_SOURCE", type=click.Path(), default=None)
@click.option("--host", envvar="HOST", type=click.STRING, default="0.0.0.0")
@click.option("--port", envvar="PORT", type=click.INT, default=8080)
@click.option("--debug", envvar="DEBUG", is_flag=True)
def _cli(target: str, source: str, host: str, port: int, debug: bool) -> None:  # pragma: no cover
    run_ucam_faas(target, source, host, port, debug)
