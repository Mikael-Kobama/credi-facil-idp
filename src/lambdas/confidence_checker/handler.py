import json

# Limiar de confiança estipulado no SRS
THRESHOLD = 0.80

def avaliar_confianca(bda_output: dict) -> dict:
    """
    Analisa os campos extraídos pelo BDA e decide se o pacote 
    precisa de revisão humana (A2I) ou pode seguir direto para o LLM.
    """
    extracted_fields = bda_output.get("extractedFields", {})
    needs_review = False
    campos_com_falha = []

    # Iteramos sobre os campos para checar o score de cada um
    for campo, dados in extracted_fields.items():
        score = dados.get("confidence", 0.0)
        if score < THRESHOLD:
            needs_review = True
            campos_com_falha.append(campo)

    return {
        "needs_human_review": needs_review,
        "low_confidence_fields": campos_com_falha,
        "status": "NEEDS_REVIEW" if needs_review else "PROCESSING"
    }