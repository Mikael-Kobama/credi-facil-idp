import json
import os
import uuid
import boto3
from botocore.exceptions import ClientError

# Inicialização do cliente fora do handler para otimizar o cold start
s3_client = boto3.client("s3")

# Nome do bucket injetado dinamicamente pelo AWS SAM
BUCKET_ENTRADA = os.environ.get("BUCKET_ENTRADA", "credifacil-docs-entrada-dev")

def gerar_urls_upload(lista_documentos: list[str], package_id: str) -> dict:
    """
    Gera URLs pré-assinadas para uma lista de documentos dentro de um package_id.
    Aplica validações de segurança severas antes da emissão.
    """
    # RNF-02 / Restrições do Case: Limite estrito de no máximo 8 documentos por pacote
    if len(lista_documentos) > 8:
        raise ValueError("O limite máximo permitido é de 8 documentos por pacote.")
        
    urls_geradas = {}
    
    for doc_name in lista_documentos:
        # Validação Sintática de Segurança: Aceitar estritamente arquivos .pdf
        if not doc_name.lower().endswith('.pdf'):
            raise ValueError(f"Extensão inválida para o arquivo {doc_name}. Apenas PDFs são permitidos.")
            
        # Define o caminho imutável do arquivo dentro do S3 protegido
        s3_key = f"packages/{package_id}/{uuid.uuid4()}-{doc_name}"
        
        try:
            # Emite a URL com expiração de 15 minutos (900 segundos) conforme RF-02
            url = s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": BUCKET_ENTRADA,
                    "Key": s3_key,
                    "ContentType": "application/pdf" # Força o Content-Type correto no upload
                },
                ExpiresIn=900
            )
            urls_geradas[doc_name] = {
                "s3_key": s3_key,
                "upload_url": url
            }
        except ClientError as e:
            print(f"Erro ao gerar URL para {doc_name}: {str(e)}")
            raise e
            
    return urls_geradas

def handler(event, context):
    """Ponto de entrada que o API Gateway invoca (padrão de produção AWS)"""
    try:
        # Recupera o corpo da requisição enviado pelo Frontend via API Gateway
        body = json.loads(event.get("body", "{}"))
        documentos = body.get("documentos", [])
        
        if not documentos:
            return {
                "statusCode": 400,
                "body": json.dumps({"erro": "A lista de documentos não pode estar vazia."})
            }
            
        # Gera o identificador único do pacote hipotecário[cite: 3]
        package_id = str(uuid.uuid4())
        
        # Processa a geração dos links seguros
        links = gerar_urls_upload(documentos, package_id)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "package_id": package_id,
                "uploads": links
            })
        }
        
    except ValueError as val_err:
        return {
            "statusCode": 400,
            "body": json.dumps({"erro": str(val_err)})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"erro": "Erro interno ao processar a solicitação."})}