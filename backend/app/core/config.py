import os
from dotenv import load_dotenv

load_dotenv()

print("Carregando variáveis de ambiente do .env para configuração do banco de dados...")

DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "ans_db")
DB_USER = os.environ.get("POSTGRES_USER", "ans_user")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "ans_pass")
