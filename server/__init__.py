from fastapi import FastAPI
from server.configuration import exceptions
from server.controllers.usuario_controller import usuario_router
from starlette_context.middleware import RawContextMiddleware
from starlette_context import plugins
from server.configuration.custom_logging import MICROSERVICE_LOGGER_KWARGS, Logger
from server.middleware.plugins import custom_request_plugin
from server.configuration import db


routers = [
    usuario_router
]


def _init_app():
    app = FastAPI()
    app = configura_exception_handlers(app)
    app = configura_middlewares(app)
    configura_logger()
    configura_routers(app)
    configura_async_engine()
    return app


def configura_async_engine():
    db.create_async_engine_cached()


def configura_logger():
    Logger(**MICROSERVICE_LOGGER_KWARGS).get_logger()


def configura_middlewares(app):
    app.add_middleware(
        RawContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            custom_request_plugin.RequestPlugin()
        )
    )
    return app


def configura_exception_handlers(app):
    app.add_exception_handler(
        exceptions.ApiBaseException,
        exceptions.api_base_exception_handler
    )
    app.add_exception_handler(
        exceptions.InvalidEmailException,
        exceptions.api_base_exception_handler
    )
    app.add_exception_handler(
        Exception,
        exceptions.generic_exception_handler
    )
    return app


def configura_routers(app):
    for router in routers:
        app.include_router(**router),

