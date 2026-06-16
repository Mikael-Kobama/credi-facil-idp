import json
import pytest
from unittest.mock import patch
from src.lambdas.result_writer.handler import handler

@patch("src.lambdas.result_writer.handler.db_client")
@patch("src.lambdas.result_writer.handler.s3_client")
def test_deve_salvar_json_no_s3_e_marcar_como_concluido_no_dynamo(mock_s3, mock_db):
    mock_s3.put_object.return_value = {}
    mock_db.update_item.return_value = {}

    evento_input = {
        "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
        "confianca_geral": 0.92,
        "revisao_humana": False,
        "json_estruturado": {
            "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
            "status": "COMPLETED",
            "documentos": {"identidade": {"nome": "Weriton L Petreca"}}
        }
    }

    resposta = handler(evento_input, None)
    corpo_resposta = json.loads(resposta["body"])

    assert resposta["statusCode"] == 200
    assert corpo_resposta["status"] == "COMPLETED"
    
    # Valida o isolamento dos disparos de SDK
    mock_s3.put_object.assert_called_once()
    mock_db.update_item.assert_called_once()