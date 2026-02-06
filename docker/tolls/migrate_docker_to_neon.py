#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def run(cmd: list[str], env=None, title: str | None = None):
    if title:
        print(f"\n=== {title} ===")

    print("CMD:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.stdout.strip():
        print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Falhou ao executar: {' '.join(cmd)}")

    return result


def require_tool(name: str):
    from shutil import which
    if which(name) is None:
        raise RuntimeError(
            f"Ferramenta '{name}' não encontrada no PATH.\n"
            f"Instale com: sudo apt install postgresql-client"
        )


def test_connection_pg_isready(host: str, port: str, user: str, db: str, password: str):
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    run(
        ["pg_isready", "-h", host, "-p", port, "-U", user, "-d", db],
        env=env,
        title=f"Testando conexão: {user}@{host}:{port}/{db}"
    )


def backup_custom_dump(host: str, port: str, user: str, db: str, password: str, output_file: Path):
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    run(
        [
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", db,
            "-Fc",
            "--no-owner",
            "--no-privileges",
            "-f", str(output_file)
        ],
        env=env,
        title="Gerando backup custom (.dump) com pg_dump"
    )


def restore_custom_dump(neon_url: str, dump_file: Path):
    run(
        [
            "pg_restore",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "-d", neon_url,
            str(dump_file)
        ],
        title="Restaurando no Neon com pg_restore"
    )


def main():
    require_tool("pg_isready")
    require_tool("pg_dump")
    require_tool("pg_restore")
    require_tool("psql")

    # ORIGEM (Docker local)
    SRC_HOST = os.getenv("LOCAL_PG_HOST", "localhost")
    SRC_PORT = os.getenv("LOCAL_PG_PORT", "5432")
    SRC_DB = os.getenv("LOCAL_PG_DB", "ans_db")
    SRC_USER = os.getenv("LOCAL_PG_USER", "ans_user")
    SRC_PASSWORD = os.getenv("LOCAL_PG_PASSWORD", "ans_pass")

    # DESTINO (Neon)
    NEON_URL = os.getenv("NEON_DATABASE_URL", "").strip()

    if not NEON_URL:
        print("\nERRO: defina a variável de ambiente NEON_DATABASE_URL no .env")
        print("Exemplo:")
        print('NEON_DATABASE_URL="postgresql://user:pass@host/neondb?sslmode=require"')
        sys.exit(1)

    # OUTPUT
    dump_override = os.getenv("DUMP_FILE", "").strip()

    if dump_override:
        dump_file = Path(dump_override)
        dump_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = Path("backups")
        out_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_file = out_dir / f"{SRC_DB}_{timestamp}.dump"

    try:
        # 1) Testa conexão no docker
        test_connection_pg_isready(SRC_HOST, SRC_PORT, SRC_USER, SRC_DB, SRC_PASSWORD)

        # 2) Faz backup
        backup_custom_dump(SRC_HOST, SRC_PORT, SRC_USER, SRC_DB, SRC_PASSWORD, dump_file)

        # 3) Testa conexão no Neon
        run(["psql", NEON_URL, "-c", "SELECT 1;"], title="Testando conexão no Neon (psql)")

        # 4) Restaura no Neon
        restore_custom_dump(NEON_URL, dump_file)

        # 5) Confirma
        run(["psql", NEON_URL, "-c", "SELECT COUNT(*) FROM operadora;"], title="Validação: COUNT operadora")
        run(["psql", NEON_URL, "-c", "SELECT COUNT(*) FROM despesa;"], title="Validação: COUNT despesa")

        print("\nOK: Migração concluída com sucesso.")
        print(f"Backup gerado em: {dump_file}")

    except Exception as e:
        print("\nFALHA:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
