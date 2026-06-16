import json
import pytest
from unittest.mock import patch
from src.lambdas.notification.handler import handler

@patch("src.lambdas.notification.handler.sns_client")
def test_deve_enviar_notificacao_para_o_topico_de_conclusao_em_caso_de_sucesso(mock_sns):
    mock_sns.publish.return_value = {"MessageId": "msg-12345"}

    evento_sucesso = {
        "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
        "execution_status": "SUCCESS"
    }

    resposta = handler(evento_sucesso, None)
    corpo_json = json.loads(resposta["body"])

    assert resposta["statusCode"] == 200
    assert "SUCCESS" in corpo_json["mensagem"]
    
    # Garante que o SNS foi acionado passando o assunto correto de sucesso
    args_chamada = mock_sns.publish.call_args[1]
    assert "Processamento Concluído" in args_chamada["Subject"]

@patch("src.lambdas.notification.handler.sns_client")
def test_deve_enviar_alerta_para_o_topico_de_erros_em_caso_de_falha(mock_sns):
    mock_sns.publish.return_value = {"MessageId": "msg-67890"}

    evento_falha = {
        "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
        "execution_status": "ERROR",
        "error_message": "Timeout ao invocar o modelo Amazon Nova Pro."
    }

    resposta = handler(evento_falha, None)
    corpo_json = json.loads(resposta["body"])

    assert resposta["statusCode"] == 200
    
    # Garante que o SNS foi acionado direcionando o alerta para a equipe de administração
    args_chamada = mock_sns.publish.call_args[1]
    assert "ALERTA ADMIN" in args_chamada["Subject"]
    assert "Timeout" in args_chamada["Message"]