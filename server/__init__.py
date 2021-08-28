from fastapi import FastAPI
from server.configuration import exceptions
from server.controllers.usuario_controller import usuario_router
from server.configuration import environment


routers = [
    usuario_router
]


def _init_app():
    app = FastAPI()
    app = configura_exception_handlers(app)
    configura_routers(app)
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

