import re

def normalize_cnpj(value: str) -> str:
    return re.sub(r"\D", "", value or "")
