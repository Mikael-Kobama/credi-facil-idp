import json
import pytest
from unittest.mock import patch, MagicMock
from src.lambdas.query_handler.handler import handler

@patch("src.lambdas.query_handler.handler.db_client")
def test_query_handler_deve_retornar_apenas_status_se_estiver_em_processamento(mock_db):
    # Simula resposta do DynamoDB para um pacote que ainda está rodando a IA
    mock_db.get_item.return_value = {
        "Item": {
            "PK": {"S": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f"},
            "SK": {"S": "METADATA"},
            "status": {"S": "PROCESSING"},
            "uploadedBy": {"S": "analista-weriton"},
            "uploadedAt": {"S": "2026-06-16T14:30:00Z"}
        }
    }

    event_api = {
        "pathParameters": {"packageId": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f"}
    }

    resposta = handler(event_api, None)
    corpo_json = json.loads(resposta["body"])

    assert resposta["statusCode"] == 200
    assert corpo_json["status"] == "PROCESSING"
    assert "dados_extraidos" not in corpo_json  # Não deve buscar no S3 se não concluiu

@patch("src.lambdas.query_handler.handler.s3_client")
@patch("src.lambdas.query_handler.handler.db_client")
def test_query_handler_deve_trazer_json_do_s3_se_status_for_completed(mock_db, mock_s3):
    # Simula o ponteiro no banco apontando para o S3
    mock_db.get_item.return_value = {
        "Item": {
            "PK": {"S": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f"},
            "SK": {"S": "METADATA"},
            "status": {"S": "COMPLETED"},
            "uploadedBy": {"S": "analista-weriton"},
            "uploadedAt": {"S": "2026-06-16T14:30:00Z"},
            "resultS3Key": {"S": "results/8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f/output.json"}
        }
    }

    # Simula o payload de negócio guardado no arquivo do S3
    mock_s3_object = MagicMock()
    mock_s3_object.read.return_value = b'{"cpf": "529.982.247-25", "nome": "Weriton L Petreca"}'
    mock_s3.get_object.return_value = {"Body": mock_s3_object}

    event_api = {
        "pathParameters": {"packageId": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f"}
    }

    resposta = handler(event_api, None)
    corpo_json = json.loads(resposta["body"])

    assert resposta["statusCode"] == 200
    assert corpo_json["status"] == "COMPLETED"
    assert corpo_json["dados_extraidos"]["nome"] == "Weriton L Petreca"