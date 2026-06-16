def obter_especificacao_ferramenta_loan() -> dict:
    """
    Retorna a especificação da ferramenta que o Amazon Nova preencherá.
    Este formato segue estritamente o padrão exigido pela API Converse do Bedrock.
    """
    return {
        "toolSpec": {
            "name": "estruturar_dados_solicitacao_credito",
            "description": "Formata e padroniza os dados extraídos de documentos hipotecários em um JSON regulado.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome completo do cliente"},
                        "cpf": {"type": "string", "description": "CPF formatado no padrão XXX.XXX.XXX-XX"},
                        "data_nascimento": {"type": "string", "description": "Data de nascimento no padrão YYYY-MM-DD"}
                    },
                    "required": ["nome", "cpf", "data_nascimento"]
                }
            }
        }
    }