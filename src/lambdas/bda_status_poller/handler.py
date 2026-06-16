import os
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger(service="bda-status-poller")
bedrock_client = boto3.client("bedrock")

def handler(event, context):
    try:
        job_id = event.get("bda_job_id")
        package_id = event.get("package_id")
        
        if not job_id:
            raise ValueError("O parâmetro bda_job_id não foi fornecido no estado do fluxo.")

        # Consulta o status atual do processamento de IA
        response = bedrock_client.get_data_automation_status(
            automationJobId=job_id
        )
        
        status_atual = response["status"] # COMPLETED, IN_PROGRESS, ou FAILED
        logger.info(f"Verificação de status do Job {job_id}: {status_atual}")

        # Injeta o status de volta no mapa do Step Functions para a tomada de decisão (Choice State)
        event["status_bda"] = status_atual
        return event

    except ClientError as e:
        logger.error(f"Erro do SDK ao consultar status no Bedrock: {str(e)}")
        raise e