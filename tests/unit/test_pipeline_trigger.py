import json
import pytest
from unittest.mock import patch, MagicMock
from src.lambdas.pipeline_trigger.handler import handler

@patch("src.lambdas.pipeline_trigger.handler.sf_client")
@patch("src.lambdas.pipeline_trigger.handler.db_client")
def test_deve_registrar_no_dynamo_e_disparar_step_functions_com_sucesso(mock_db, mock_sf):
    # Simula as respostas de sucesso das APIs da AWS
    mock_db.put_item.return_value = {}
    mock_sf.start_execution.return_value = {"executionArn": "arn:aws:states:execution-123"}
    
    # Evento simulado chegando do API Gateway
    event_api = {
        "body": json.dumps({
            "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
            "user_id": "analista-weriton",
            "document_count": 5
        })
    }
    
    resposta = handler(event_api, None)
    corpo_json = json.loads(resposta["body"])
    
    assert resposta["statusCode"] == 202
    assert corpo_json["execution_arn"] == "arn:aws:states:execution-123"
    # Garante que as funções do SDK foram chamadas exatamente uma vez
    mock_db.put_item.assert_called_once()
    mock_sf.start_execution.assert_called_once()