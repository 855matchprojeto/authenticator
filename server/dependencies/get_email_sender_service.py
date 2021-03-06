from fastapi_mail import ConnectionConfig, FastMail
from server.services.email_service import EmailService
from fastapi import BackgroundTasks, Depends
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.environment import Environment


def get_email_sender_service(
    background_tasks: BackgroundTasks,
    environment: Environment = Depends(get_environment_cached)
):

    email_api = FastMail(
        ConnectionConfig(
            MAIL_USERNAME=environment.MAIL_USERNAME,
            MAIL_PASSWORD=environment.MAIL_PASSWORD,
            MAIL_FROM=environment.MAIL_FROM,
            MAIL_PORT=environment.MAIL_PORT,
            MAIL_SERVER=environment.MAIL_SERVER,
            MAIL_TLS=bool(environment.MAIL_TLS),
            MAIL_SSL=bool(environment.MAIL_SSL),
            USE_CREDENTIALS=bool(environment.MAIL_USE_CREDENTIALS)
        )
    )

    return EmailService(
        email_api,
        background_tasks
    )

