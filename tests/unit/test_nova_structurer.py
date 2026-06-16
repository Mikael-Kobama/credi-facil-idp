import pytest
from src.lambdas.nova_structurer.handler import montar_payload_bedrock, processar_resposta_bedrock

def test_deve_montar_payload_do_bedrock_com_a_ferramenta_correta():
    dados_teste = {"nome_cru": "WERITON L PETRECA", "cpf_cru": "52998224725"}
    payload = montar_payload_bedrock(dados_teste)
    
    assert payload["modelId"] == "amazon.nova-pro-v1:0"
    assert len(payload["toolConfig"]["tools"]) == 1
    assert payload["toolConfig"]["tools"][0]["toolSpec"]["name"] == "estruturar_dados_solicitacao_credito"

def test_deve_processar_resposta_de_tool_calling_do_bedrock_com_sucesso():
    # Resposta simulada exatamente no padrão de retorno do SDK Boto3 da AWS para o Amazon Nova
    mock_response_boto3 = {
        "output": {
            "message": {
                "role": "assistant",
                "toolRequests": [
                    {
                        "toolId": "toolrequest-123",
                        "name": "estruturar_dados_solicitacao_credito",
                        "input": '{"nome": "Weriton L Petreca", "cpf": "529.982.247-25", "data_nascimento": "1989-12-25"}'
                    }
                ]
            }
        }
    }
    
    package_id = "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f"
    resultado_final = processar_resposta_bedrock(mock_response_boto3, package_id, "user-test-123")
    
    assert resultado_final["status"] == "COMPLETED"
    assert resultado_final["documentos"]["identidade"]["cpf"] == "529.982.247-25"
    assert resultado_final["documentos"]["identidade"]["nome"] == "Weriton L Petreca"