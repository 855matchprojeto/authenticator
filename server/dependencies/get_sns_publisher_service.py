import boto3
from fastapi import Depends
from server.configuration.custom_logging import get_main_logger
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.environment import Environment
from server.services.aws_publisher_service import AWSPublisherService


MAIN_LOGGER = get_main_logger()


async def get_sns_publisher_service(
    environment: Environment = Depends(get_environment_cached)
) -> AWSPublisherService:

    """
        Retorna um client boto3 para as mensagens SNS para a AWS
    """

    boto3_client = boto3.client(
        'sns',
        aws_access_key_id=environment.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=environment.AWS_SECRET_KEY,
        region_name=environment.AWS_REGION_NAME
    )

    return AWSPublisherService(boto3_client)

