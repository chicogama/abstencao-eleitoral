import logging
from pathlib import Path

import requests

from abstencao.core.config import settings

logger = logging.getLogger(__name__)


def baixar_arquivo(url: str) -> Path:
    destino = settings.dir_raw / url.rsplit("/", 1)[-1]
    if destino.exists() and destino.stat().st_size > 0:
        logger.info("Usando arquivo já baixado: %s", destino.name)
        return destino

    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(destino.suffix + ".parcial")
    logger.info("Baixando %s", url)
    with requests.get(url, stream=True, timeout=60) as resposta:
        resposta.raise_for_status()
        with temporario.open("wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                arquivo.write(bloco)
    temporario.rename(destino)
    return destino


def url_tse(caminho: str) -> str:
    return f"{settings.url_tse}/{caminho}"
