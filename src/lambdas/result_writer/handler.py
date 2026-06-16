import json
import os
from datetime import datetime, timezone
import boto3
from aws_lambda_powertools import Logger

logger = Logger(service="result-writer")

# Inicialização dos clientes SDK fora do handler para otimização de performance
s3_client = boto3.client("s3")
db_client = boto3.client("dynamodb")

BUCKET_SAIDA = os.environ.get("BUCKET_SAIDA", "credifacil-docs-saida-dev")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "credifacil-pacotes-dev")

def handler(event, context):
    try:
        package_id = event.get("package_id")
        json_estruturado = event.get("json_estruturado", {})
        confianca_geral = event.get("confianca_geral", 1.0)
        passou_por_revisao = event.get("revisao_humana", False)
        
        if not package_id or not json_estruturado:
            raise ValueError("Os parâmetros package_id e json_estruturado são obrigatórios.")

        timestamp_conclusao = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        s3_key_saida = f"results/{package_id}/output.json"

        # 1. ESCRITA NO AMAZON S3 (Payload completo)
        s3_client.put_object(
            Bucket=BUCKET_SAIDA,
            Key=s3_key_saida,
            Body=json.dumps(json_estruturado, ensure_ascii=False),
            ContentType="application/json"
        )
        logger.info(f"JSON estruturado salvo com sucesso no S3: {s3_key_saida}")

        # 2. ATUALIZAÇÃO NO DYNAMODB (Mapeado ao Single-Table Design do SRS)
        # Usamos o UpdateItem para atualizar cirurgicamente apenas os novos atributos de conclusão
        db_client.update_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": package_id},
                "SK": {"S": "METADATA"}
            },
            UpdateExpression=(
                "SET #st = :status, processedAt = :pAt, resultS3Key = :s3Key, "
                "confidenceScore = :score, humanReview = :hReview"
            ),
            ExpressionAttributeNames={
                "#st": "status" # 'status' é palavra reservada no DynamoDB, mapeamos com alias
            },
            ExpressionAttributeValues={
                ":status": {"S": "COMPLETED"},
                ":pAt": {"S": timestamp_conclusao},
                ":s3Key": {"S": s3_key_saida},
                ":score": {"N": str(confianca_geral)},
                ":hReview": {"BOOL": passou_por_revisao}
            }
        )
        logger.info(f"Registro {package_id} atualizado no DynamoDB para COMPLETED.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "package_id": package_id,
                "status": "COMPLETED",
                "s3_path": f"s3://{BUCKET_SAIDA}/{s3_key_saida}"
            })
        }

    except Exception as e:
        logger.error(f"Erro ao persistir encerramento do pipeline: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"erro": "Falha na persistência final dos dados."})
        }