from scripts.run_integration import run as run_integrate
from scripts.run_aggregate import run as run_aggregate


def main():
    try:
        print("[STEP 1] Executando integração...")
        run_integrate()

        print("[STEP 2] Executando agregação...")
        run_aggregate()

        print("[OK] Pipeline completo executado com sucesso.")

    except Exception as e:
        print("[ERRO] Falha na execução do pipeline.")
        raise 


if __name__ == "__main__":
    main()
