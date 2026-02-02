import re
import pandas as pd

def valida_cnpj(cnpj: str) -> bool:
    if pd.isna(cnpj):
        return False

    cnpj = re.sub(r"\D", "", str(cnpj))

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calc_digito(cnpj_, pesos):
        soma = sum(int(n) * p for n, p in zip(cnpj_, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    d1 = calc_digito(cnpj[:12], [5,4,3,2,9,8,7,6,5,4,3,2])
    d2 = calc_digito(cnpj[:12] + d1, [6,5,4,3,2,9,8,7,6,5,4,3,2])

    return cnpj[-2:] == d1 + d2


def normalizar_cnpj(cnpj: str) -> str | None:
    if pd.isna(cnpj):
        return None
    return re.sub(r"\D", "", str(cnpj)).zfill(14)
