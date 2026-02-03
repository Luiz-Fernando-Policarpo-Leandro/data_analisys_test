from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
import re

from app.core.database import get_connection
from app.utils.cnpj import normalize_cnpj
from app.models.schemas import Operadora, Despesa, PaginatedOperadoras

router = APIRouter(prefix="/api/operadoras", tags=["Operadoras"])

@router.get("", response_model=PaginatedOperadoras)
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    q: Optional[str] = None,
    include_sem_despesas: bool = Query(False), # Novo parâmetro
    conn=Depends(get_connection)
):
    offset = (page - 1) * limit
    cur = conn.cursor()

    # 1. Construção dinâmica das condições (WHERE)
    conditions = []
    params = []

    # Filtro de busca (Nome ou CNPJ)
    if q:
        q_norm = re.sub(r"\D", "", q)
        if q_norm:
            conditions.append("cnpj LIKE %s")
            params.append(f"%{q_norm}%")
        else:
            conditions.append("razao_social ILIKE %s")
            params.append(f"%{q}%")

    # Filtro de despesas: Se include_sem_despesas for False (padrão), 
    # filtramos apenas as que possuem registros na tabela despesa.
    if not include_sem_despesas:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM despesa d 
                WHERE d.id_operadora = operadora.id_operadora
            )
        """)

    # Une as condições com AND
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # 2. Busca o total para a paginação
    cur.execute(f"SELECT COUNT(*) FROM operadora {where_clause}", params)
    total = cur.fetchone()[0]

    # 3. Busca os dados paginados
    # Nota: data_registro_ans convertido para str para evitar erro de validação
    cur.execute(f"""
        SELECT id_operadora, registro_ans, cnpj, razao_social,
               nome_fantasia, modalidade, uf, data_registro_ans
        FROM operadora
        {where_clause}
        ORDER BY razao_social
        OFFSET %s LIMIT %s
    """, params + [offset, limit])

    rows = cur.fetchall()
    cur.close()

    return {
        "data": [
            Operadora(
                id_operadora=r[0],
                registro_ans=r[1],
                cnpj=r[2],
                razao_social=r[3],
                nome_fantasia=r[4],
                modalidade=r[5],
                uf=r[6],
                data_registro_ans=str(r[7]) if r[7] else ""
            ) for r in rows
        ],
        "total": total,
        "page": page,
        "limit": limit
    }

# ... (os outros métodos obter_operadora e despesas_operadora permanecem iguais)
@router.get("/{cnpj}", response_model=Operadora)
def obter_operadora(cnpj: str, conn=Depends(get_connection)):
    cnpj = normalize_cnpj(cnpj)
    cur = conn.cursor()

    cur.execute("""
        SELECT id_operadora, registro_ans, cnpj, razao_social,
               nome_fantasia, modalidade, uf, data_registro_ans
        FROM operadora WHERE cnpj = %s
    """, (cnpj,))

    row = cur.fetchone()
    cur.close()

    if not row:
        raise HTTPException(404, "Operadora não encontrada")

    return Operadora(
        id_operadora=row[0],
        registro_ans=row[1],
        cnpj=row[2],
        razao_social=row[3],
        nome_fantasia=row[4],
        modalidade=row[5],
        uf=row[6],
        data_registro_ans=str(row[7])
    )

@router.get("/{cnpj}/despesas", response_model=List[Despesa])
def despesas_operadora(cnpj: str, conn=Depends(get_connection)):
    cnpj = normalize_cnpj(cnpj)
    cur = conn.cursor()

    cur.execute("""
        SELECT d.ano, d.trimestre, d.valor
        FROM despesa d
        JOIN operadora o ON o.id_operadora = d.id_operadora
        WHERE o.cnpj = %s
        ORDER BY d.ano, d.trimestre
    """, (cnpj,))

    rows = cur.fetchall()
    cur.close()

    return [Despesa(ano=r[0], trimestre=r[1], valor=float(r[2])) for r in rows]
