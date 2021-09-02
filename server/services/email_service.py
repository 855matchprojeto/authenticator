from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List


class EmailService:

    def __init__(self, conf: ConnectionConfig, background_tasks: BackgroundTasks):
        self.conf = conf
        self.fast_mail = FastMail(conf)
        self.background_tasks = background_tasks

    def send_email_background(self, recipient_email_list: List[EmailStr], subject: str,
                              rendered_html: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipient_email_list,
            html=rendered_html,
            subtype="html"
        )
        self.background_tasks.add_task(
            self.fast_mail.send_message,
            message
        )

