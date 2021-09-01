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
                              template_body: dict, template_name: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipient_email_list,
            template_body=template_body
        )
        self.background_tasks.add_task(
            self.fast_mail.send_message,
            message=message,
            template_name=template_name
        )

