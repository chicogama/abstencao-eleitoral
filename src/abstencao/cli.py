import argparse
import logging

from abstencao.db.session import SessionLocal
from abstencao.services.etl_service import executar_etl
from abstencao.services.modelo_service import executar_treino


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa etapas do pipeline sem passar pela fila.")
    parser.add_argument("etapa", choices=["etl", "treino", "tudo"])
    etapa = parser.parse_args().etapa

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    with SessionLocal() as db:
        if etapa in ("etl", "tudo"):
            for carga in executar_etl(db):
                print(f"{carga.fonte}: {carga.status} ({carga.linhas} linhas)")
        if etapa in ("treino", "tudo"):
            print(executar_treino(db))


if __name__ == "__main__":
    main()
