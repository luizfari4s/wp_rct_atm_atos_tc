from prefect import flow
import importlib
import main


@flow(log_prints=True)
def atm_tc():

    # Recarrega o módulo a cada execução
    # para pegar alterações sem reiniciar o flow.py
    importlib.reload(main)

    # Executa a função principal
    main.main()

if __name__ == "__main__":

    atm_tc.serve(
        name="atm-producao-tc",
        cron="0 12 * * 1-5"
    )