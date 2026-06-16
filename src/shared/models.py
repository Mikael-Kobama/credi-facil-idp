from pydantic import BaseModel, Field, field_validator, UUID4
from typing import Optional
from datetime import date
import re

def calcular_digito(digitos: list[int], peso_inicial: int) -> int:
    soma = sum(d * p for d, p in zip(digitos, range(peso_inicial, 1, -1)))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto

def eh_cpf_valido(cpf: str) -> bool:
    # Remove pontos e hífen para trabalhar apenas com os números
    numeros = [int(d) for d in cpf if d.isdigit()]
    
    # CPFs com todos os números iguais são matematicamente inválidos, mas passam no teste do dígito
    if len(set(numeros)) == 1:
        return False
        
    # Calcula o primeiro e o segundo dígito verificador
    digito_1 = calcular_digito(numeros[:9], 10)
    digito_2 = calcular_digito(numeros[:10], 11)
    
    return numeros[9] == digito_1 and numeros[10] == digito_2

class IdentidadeModel(BaseModel):
    nome: str = Field(..., description="Nome completo extraído do documento")
    cpf: str = Field(..., description="CPF formatado com pontos e hífen")
    data_nascimento: date = Field(..., description="Data de nascimento no padrão ISO YYYY-MM-DD")
    confianca: float = Field(..., ge=0.0, le=1.0)

    @field_validator('cpf')
    @classmethod
    def validar_cpf_completo(cls, valor: str) -> str:
        # 1. Validação Sintática (Formato)
        padrao = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
        if not re.match(padrao, valor):
            raise ValueError("O CPF extraído pela IA deve seguir o formato XXX.XXX.XXX-XX")
        
        # 2. Validação Semântica (Cálculo Matemático Real)
        if not eh_cpf_valido(valor):
            raise ValueError("O CPF fornecido é matematicamente inválido")
            
        return valor

class DocumentosPacote(BaseModel):
    identidade: IdentidadeModel

class LoanPackageOutput(BaseModel):
    package_id: UUID4
    status: str
    confianca_geral: float = Field(..., ge=0.0, le=1.0)
    revisao_humana: bool
    documentos: DocumentosPacote