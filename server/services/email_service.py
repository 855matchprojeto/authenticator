from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, FastMail
from pydantic import EmailStr
from typing import List


class EmailService:

    def __init__(self, email_api: FastMail, background_tasks: BackgroundTasks):
        self.email_api = email_api  # FastMail
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
            self.email_api.send_message,
            message
        )

