from scripts.run_integration import run as run_integrate
from scripts.run_aggregate import run as run_aggregate
from scripts.run_format_csv import run as run_format_csv


def main():
    try:
        print("[STEP 1] Executando integração...")
        run_integrate()

        print("[STEP 2] Executando agregação...")
        run_aggregate()

        print("[STEP 3] Formatando CSVs...")
        # run_format_csv()

        print("[OK] Pipeline completo executado com sucesso.")

    except Exception as e:
        print("[ERRO] Falha na execução do pipeline.")
        raise 


if __name__ == "__main__":
    main()
