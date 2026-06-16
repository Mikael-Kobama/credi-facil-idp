import pytest
from unittest.mock import patch, MagicMock
from src.lambdas.bda_invoker.handler import handler as invoker_handler
from src.lambdas.bda_status_poller.handler import handler as poller_handler

@patch("src.lambdas.bda_invoker.handler.boto3.client")
@patch("src.lambdas.bda_invoker.handler.bedrock_client")
def test_bda_invoker_deve_submeter_job_com_sucesso(mock_bedrock, mock_boto_sts):
    # Mock para a conta AWS fictícia e para o retorno do Bedrock Job
    mock_boto_sts("sts").get_caller_identity.return_value = {"Account": "123456789012"}
    mock_bedrock.invoke_data_automation_async.return_value = {"automationJobId": "job-ia-abc-123"}
    
    evento_sf = {
        "package_id": "pacote-uuid-teste",
        "user_id": "user-123",
        "bda_output_bucket": "meu-bucket-saida"
    }
    
    resposta = invoker_handler(evento_sf, None)
    
    assert resposta["bda_job_id"] == "job-ia-abc-123"
    assert "result.json" in resposta["bda_output_key"]
    mock_bedrock.invoke_data_automation_async.assert_called_once()

@patch("src.lambdas.bda_status_poller.handler.bedrock_client")
def test_bda_status_poller_deve_retornar_status_atual_da_ia(mock_bedrock):
    mock_bedrock.get_data_automation_status.return_value = {"status": "IN_PROGRESS"}
    
    evento_polling = {
        "package_id": "pacote-uuid-teste",
        "bda_job_id": "job-ia-abc-123"
    }
    
    resposta = poller_handler(evento_polling, None)
    
    assert resposta["status_bda"] == "IN_PROGRESS"
    mock_bedrock.get_data_automation_status.assert_called_once()