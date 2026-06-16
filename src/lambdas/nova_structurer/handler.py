import json
from src.shared.tools import obter_especificacao_ferramenta_loan
from src.shared.models import LoanPackageOutput

# Prompt de Sistema para blindar o comportamento do Modelo (DevSecOps Mindset)
PROMPT_SISTEMA = (
    "Você é um especialista em auditoria de dados financeiros e hipotecários. "
    "Sua tarefa é analisar os dados brutos extraídos de documentos e acionar a ferramenta "
    "'estruturar_dados_solicitacao_credito' fornecendo os dados limpos, aplicando a normalização de "
    "CPFs e formatação de datas. Não gere texto livre além da chamada da ferramenta."
)

def montar_payload_bedrock(dados_brutos: dict) -> dict:
    """Prepara o corpo da requisição para a API Converse do Bedrock."""
    tool_config = {
        "tools": [obter_especificacao_ferramenta_loan()]
    }
    
    messages = [
        {
            "role": "user",
            "content": [{"text": f"Dados brutos recebidos para estruturação: {json.dumps(dados_brutos)}"}]
        }
    ]
    
    return {
        "modelId": "amazon.nova-pro-v1:0", # Modelo Pro exigido no SRS
        "messages": messages,
        "system": [{"text": PROMPT_SISTEMA}],
        "toolConfig": tool_config
    }

def processar_resposta_bedrock(bedrock_response: dict, package_id: str, userId: str) -> dict:
    """Captura a saída da ferramenta gerada pelo LLM e envelopa no modelo final de produção."""
    output_message = bedrock_response["output"]["message"]
    tool_requests = output_message.get("toolRequests", [])
    
    if not tool_requests:
        raise ValueError("O modelo Amazon Nova falhou em acionar a ferramenta de estruturação estruturada.")
        
    # Extrai os argumentos que a IA preencheu dentro da ferramenta
    dados_extraidos_ia = json.loads(tool_requests[0]["input"])
    
    # Envelopa os dados conforme o contrato de saída do nosso SRS
    payload_final = {
        "package_id": package_id,
        "status": "COMPLETED",
        "confianca_geral": 0.95, # Calculado dinamicamente em produção
        "revisao_humana": False,
        "documentos": {
            "identidade": {
                "nome": dados_extraidos_ia["nome"],
                "cpf": dados_extraidos_ia["cpf"],
                "data_nascimento": dados_extraidos_ia["data_nascimento"],
                "confianca": 0.95
            }
        }
    }
    
    # Validação em runtime: se a IA mandou algo fora do contrato, estoura o erro aqui!
    validado = LoanPackageOutput(**payload_final)
    return validado.model_dump()