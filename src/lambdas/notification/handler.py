import json
import os
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger(service="notification")

# Inicialização do cliente SNS fora do handler para reaproveitamento de conexões
sns_client = boto3.client("sns")

# ARNs dos tópicos injetados dinamicamente pelo AWS SAM via Parameter Store
TOPIC_CONCLUSAO = os.environ.get("SNS_COMPLETION_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:credifacil-conclusao-dev")
TOPIC_ERROS = os.environ.get("SNS_ERROR_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:credifacil-erros-dev")

def handler(event, context):
    try:
        package_id = event.get("package_id")
        tipo_evento = event.get("execution_status") # SUCCESS ou ERROR
        
        if not package_id or not tipo_evento:
            raise ValueError("Os campos package_id e execution_status são obrigatórios no evento.")

        if tipo_evento == "SUCCESS":
            mensagem = {
                "default": f"Solicitação de crédito {package_id} processada com sucesso pela IA. Dados estruturados disponíveis para análise.",
                "package_id": package_id,
                "status": "COMPLETED"
            }
            topic_arn = TOPIC_CONCLUSAO
            assunto = f"✨ [CrediFácil IDP] Processamento Concluído - {package_id}"
            
        else:
            detalhe_erro = event.get("error_message", "Erro interno não mapeado no workflow.")
            mensagem = {
                "default": f"ALERTA CRÍTICO: O pipeline serverless falhou ao processar o pacote {package_id}.",
                "package_id": package_id,
                "status": "FAILED",
                "motivo": detalhe_erro
            }
            topic_arn = TOPIC_ERROS
            assunto = f"🚨 [ALERTA ADMIN] Falha no Pipeline IDP - {package_id}"

        logger.info(f"Publicando notificação de {tipo_evento} para o pacote {package_id} no SNS.")

        # Publicação oficial no Amazon SNS aplicando formatação JSON estruturada
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(mensagem, ensure_ascii=False),
            Subject=assunto
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({"mensagem": f"Notificação de {tipo_evento} enviada com sucesso."})
        }

    except ClientError as e:
        logger.error(f"Erro do SDK ao publicar mensagem no Amazon SNS: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"erro": "Falha ao disparar o serviço de mensageria."})}
    except Exception as e:
        logger.error(f"Erro inesperado na Lambda de notificação: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"erro": "Erro interno de processamento."})}