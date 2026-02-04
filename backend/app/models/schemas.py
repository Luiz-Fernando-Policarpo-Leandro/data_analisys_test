from pydantic import BaseModel
from typing import List, Optional

class Operadora(BaseModel):
    id_operadora: int
    registro_ans: int
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str]
    modalidade: str
    uf: str
    data_registro_ans: str


class Despesa(BaseModel):
    ano: int
    trimestre: int
    valor: float


class PaginatedOperadoras(BaseModel):
    data: List[Operadora]
    total: int
    page: int
    limit: int


class TopOperadora(BaseModel):
    id_operadora: int
    cnpj: str
    razao_social: str
    total_despesas: float


class EstatisticasGlobais(BaseModel):
    total_despesas: float
    media_despesas: float
    top_5_operadoras: List[TopOperadora]


class EstatisticaOperadora(BaseModel):
    id_operadora: int
    cnpj: str
    razao_social: str
    total_despesas: float
    media_despesas: float
    desvio_padrao: float

# app/models/schemas.py

class DespesaPorUF(BaseModel):
    uf: str
    total: float

class EstatisticasGlobais(BaseModel):
    total_despesas: float
    media_despesas: float
    top_5_operadoras: List[TopOperadora]
    despesas_por_uf: List[DespesaPorUF]