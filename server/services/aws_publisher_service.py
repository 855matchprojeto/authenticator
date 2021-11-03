class AWSPublisherService:

    def __init__(self, boto3_client):
        self.boto3_client = boto3_client

    def publish(self, msg: str, target_arn: str) -> dict:
        """
        Função responsável por publicar uma mensagem para a AWS
        utilizando o client definido no objeto de classe.

        :param msg: Mensagem enviada para o SNS ou SQS
        :param target_arn: ARN do SQS ou SNS
        :return: response
        """
        response = self.boto3_client.publish(
            TargetArn=target_arn,
            Message=msg
        )
        return response
