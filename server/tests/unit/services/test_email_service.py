import pytest
from server.services.email_service import EmailService
from mock import Mock, AsyncMock
from server.configuration import exceptions
from pydantic import EmailStr
from typing import List


class TestEmailService:

    """
        Testes dos serviços chamados por outros serviços
    """

    @staticmethod
    @pytest.mark.parametrize("recipients, subject, rendered_html", [
        (["a@dac.unicamp.br", "b@dac.unicamp.br"], "", ""),
        (["a@dac.unicamp.br"], "Subject", "HTML")
    ])
    def test_send_email(recipients: List[EmailStr], subject, rendered_html):

        """
            Teste da função principal do serviço de envio de email
        """

        email_api_mock = Mock()
        email_api_mock.send_message = Mock(
            return_value=None
        )

        background_tasks_mock = Mock()
        background_tasks_mock.add_task = Mock(
            return_value=None
        )

        email_service = EmailService(
            email_api=email_api_mock,
            background_tasks=background_tasks_mock
        )

        email_service.send_email_background(
            recipients,
            subject,
            rendered_html
        )

        background_tasks_mock.add_task.assert_called()

