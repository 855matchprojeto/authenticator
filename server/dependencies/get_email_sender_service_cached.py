from functools import lru_cache
from fastapi_mail import ConnectionConfig
from server.dependencies.get_environment_cached import get_environment_cached
from server.services.email_service import EmailService
from fastapi import BackgroundTasks


@lru_cache
def get_email_sender_service_cached(background_tasks: BackgroundTasks):
    environment = get_environment_cached()

    email_sender_config = ConnectionConfig(
        MAIL_USERNAME=environment.MAIL_USERNAME,
        MAIL_PASSWORD=environment.MAIL_PASSWORD,
        MAIL_FROM=environment.MAIL_FROM,
        MAIL_PORT=environment.MAIL_PORT,
        MAIL_SERVER=environment.MAIL_SERVER,
        MAIL_TLS=bool(environment.MAIL_TLS),
        MAIL_SSL=bool(environment.MAIL_SSL),
        USE_CREDENTIALS=bool(environment.MAIL_USE_CREDENTIALS)
    )

    return EmailService(
        email_sender_config,
        background_tasks
    )

