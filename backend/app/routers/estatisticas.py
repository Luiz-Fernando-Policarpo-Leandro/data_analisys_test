from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_connection
from app.utils.cnpj import normalize_cnpj
from app.models.schemas import EstatisticasGlobais, EstatisticaOperadora, TopOperadora

router = APIRouter(prefix="/api/estatisticas", tags=["Estatísticas"])

@router.get("", response_model=EstatisticasGlobais)
def estatisticas_globais(conn=Depends(get_connection)):
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(total_despesas),0),
               COALESCE(AVG(media_trimestral),0)
        FROM despesa_agregada
    """)
    total, media = cur.fetchone()

    cur.execute("""
        SELECT o.id_operadora, o.cnpj, o.razao_social,
               SUM(da.total_despesas)
        FROM despesa_agregada da
        JOIN operadora o ON o.id_operadora = da.id_operadora
        GROUP BY o.id_operadora, o.cnpj, o.razao_social
        ORDER BY SUM(da.total_despesas) DESC
        LIMIT 5
    """)

    top_5 = [
        TopOperadora(
            id_operadora=r[0],
            cnpj=r[1],
            razao_social=r[2],
            total_despesas=float(r[3])
        ) for r in cur.fetchall()
    ]

    cur.close()

    return EstatisticasGlobais(
        total_despesas=float(total),
        media_despesas=float(media),
        top_5_operadoras=top_5
    )

@router.get("/{cnpj}", response_model=EstatisticaOperadora)
def estatisticas_operadora(cnpj: str, conn=Depends(get_connection)):
    cnpj = normalize_cnpj(cnpj)
    cur = conn.cursor()

    cur.execute("""
        SELECT o.id_operadora, o.cnpj, o.razao_social,
               COALESCE(SUM(da.total_despesas),0),
               COALESCE(AVG(da.media_trimestral),0),
               COALESCE(AVG(da.desvio_padrao),0)
        FROM operadora o
        LEFT JOIN despesa_agregada da ON da.id_operadora = o.id_operadora
        WHERE o.cnpj = %s
        GROUP BY o.id_operadora, o.cnpj, o.razao_social
    """, (cnpj,))

    row = cur.fetchone()
    cur.close()

    if not row:
        raise HTTPException(404, "Operadora não encontrada")

    return EstatisticaOperadora(
        id_operadora=row[0],
        cnpj=row[1],
        razao_social=row[2],
        total_despesas=float(row[3]),
        media_despesas=float(row[4]),
        desvio_padrao=float(row[5])
    )
