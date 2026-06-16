import pytest
from pydantic import ValidationError
from src.shared.models import LoanPackageOutput

def test_deve_validar_payload_da_ia_com_cpf_matematicamente_valido():
    payload_valido = {
        "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
        "status": "COMPLETED",
        "confianca_geral": 0.95,
        "revisao_humana": False,
        "documentos": {
          "identidade": {
            "nome": "Weriton L Petreca",
            "cpf": "529.982.247-25",  # CPF Válido gerado para testes
            "data_nascimento": "1989-12-25",
            "confianca": 0.98
          }
        }
    }
    model = LoanPackageOutput(**payload_valido)
    assert model.documentos.identidade.cpf == "529.982.247-25"

def test_deve_falhar_se_cpf_tiver_formato_correto_mas_for_falso():
    payload_cpf_falso = {
        "package_id": "8f3b9c2e-4a1d-4f7b-9c3e-2a1b4c7d5e6f",
        "status": "COMPLETED",
        "confianca_geral": 0.95,
        "revisao_humana": False,
        "documentos": {
          "identidade": {
            "nome": "João das Couves",
            "cpf": "123.456.789-00",  # Formato OK, mas algoritmo falha!
            "data_nascimento": "1990-01-01",
            "confianca": 0.85
          }
        }
    }
    with pytest.raises(ValidationError) as exc_info:
        LoanPackageOutput(**payload_cpf_falso)
    
    assert "O CPF fornecido é matematicamente inválido" in str(exc_info.value)