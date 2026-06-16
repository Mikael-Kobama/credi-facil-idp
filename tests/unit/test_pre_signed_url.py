import pytest
from unittest.mock import patch
from src.lambdas.pre_signed_url.handler import gerar_urls_upload

@patch("src.lambdas.pre_signed_url.handler.s3_client")
def test_deve_gerar_urls_pre_assinadas_com_sucesso(mock_s3):
    # Simula o retorno de uma URL falsa pelo cliente do boto3
    mock_s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/fake-presigned-url"
    
    documentos_teste = ["identidade.pdf", "holerite.pdf"]
    package_id = "test-package-123"
    
    resultado = gerar_urls_upload(documentos_teste, package_id)
    
    assert "identidade.pdf" in resultado
    assert "holerite.pdf" in resultado
    assert resultado["identidade.pdf"]["upload_url"] == "https://s3.amazonaws.com/fake-presigned-url"
    # Garante que os arquivos foram roteados para a pasta correta do pacote
    assert resultado["identidade.pdf"]["s3_key"].startswith(f"packages/{package_id}/")

def test_deve_rejeitar_se_houver_documento_que_nao_seja_pdf():
    documentos_invalidos = ["foto_imovel.jpg"]
    package_id = "test-package-123"
    
    with pytest.raises(ValueError) as exc_info:
        gerar_urls_upload(documentos_invalidos, package_id)
        
    assert "Apenas PDFs são permitidos" in str(exc_info.value)

def test_deve_rejeitar_se_lista_ultrapassar_limite_de_oito_arquivos():
    documentos_excessivos = [f"doc_{i}.pdf" for i in range(9)]
    package_id = "test-package-123"
    
    with pytest.raises(ValueError) as exc_info:
        gerar_urls_upload(documentos_excessivos, package_id)
        
    assert "O limite máximo permitido é de 8 documentos" in str(exc_info.value)