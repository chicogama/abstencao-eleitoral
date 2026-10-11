import logging
from collections.abc import Callable

import pandas as pd
from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from abstencao.core.config import settings
from abstencao.models import (
    CargaEtl,
    IndicadorMunicipio,
    Municipio,
    PerfilEleitorado,
    Previsao,
    ResultadoEleicao,
)
from abstencao.services import etl_ibge, etl_tse

logger = logging.getLogger(__name__)


def _registrar_carga(db: Session, fonte: str, carregar: Callable[[], int]) -> CargaEtl:
    carga = CargaEtl(fonte=fonte)
    db.add(carga)
    db.commit()
    logger.info("Início da carga: %s", fonte)
    try:
        carga.linhas = carregar()
        carga.status = "sucesso"
    except Exception as erro:
        db.rollback()
        carga.status = "erro"
        carga.mensagem = str(erro)[:500]
        raise
    finally:
        carga.fim = func.now()
        db.add(carga)
        db.commit()
        logger.info("Fim da carga: %s (%s, %s linhas)", fonte, carga.status, carga.linhas)
    return carga


def _mapa_tse_para_ibge(db: Session) -> dict[str, int]:
    return dict(db.execute(select(Municipio.cd_tse, Municipio.cd_ibge)).all())


def _com_cd_ibge(db: Session, dados: pd.DataFrame) -> pd.DataFrame:
    dados = dados.assign(cd_ibge=dados["cd_tse"].map(_mapa_tse_para_ibge(db)))
    sem_correspondencia = dados["cd_ibge"].isna().sum()
    if sem_correspondencia:
        logger.warning("%s linhas sem código IBGE foram descartadas", sem_correspondencia)
    return dados.dropna(subset=["cd_ibge"]).astype({"cd_ibge": int}).drop(columns="cd_tse")


def _gravar(db: Session, modelo: type, dados: pd.DataFrame) -> int:
    registros = dados.astype(object).where(dados.notna(), None).to_dict("records")
    db.execute(insert(modelo), registros)
    db.commit()
    return len(registros)


def carregar_municipios(db: Session) -> int:
    municipios = etl_tse.extrair_municipios()
    for modelo in (Previsao, ResultadoEleicao, PerfilEleitorado, IndicadorMunicipio):
        db.execute(delete(modelo))
    db.execute(delete(Municipio))
    return _gravar(db, Municipio, municipios)


def carregar_resultados(db: Session, ano: int) -> int:
    resultados = _com_cd_ibge(db, etl_tse.extrair_resultados(ano))
    db.execute(delete(ResultadoEleicao).where(ResultadoEleicao.ano == ano))
    return _gravar(db, ResultadoEleicao, resultados)


def carregar_perfil_eleitorado(db: Session, ano: int) -> int:
    perfil = _com_cd_ibge(db, etl_tse.extrair_perfil_eleitorado(ano))
    db.execute(delete(PerfilEleitorado).where(PerfilEleitorado.ano == ano))
    return _gravar(db, PerfilEleitorado, perfil)


def carregar_indicadores(db: Session) -> int:
    indicadores = etl_ibge.extrair_indicadores()
    municipios_conhecidos = set(db.scalars(select(Municipio.cd_ibge)))
    indicadores = indicadores[indicadores["cd_ibge"].isin(municipios_conhecidos)]
    db.execute(delete(IndicadorMunicipio))
    return _gravar(db, IndicadorMunicipio, indicadores)


def executar_etl(db: Session) -> list[CargaEtl]:
    etapas: list[tuple[str, Callable[[], int]]] = [
        ("tse_municipios", lambda: carregar_municipios(db)),
        (f"tse_resultados_{settings.ano_anterior}", lambda: carregar_resultados(db, settings.ano_anterior)),
        (f"tse_resultados_{settings.ano_alvo}", lambda: carregar_resultados(db, settings.ano_alvo)),
        (f"tse_perfil_eleitorado_{settings.ano_alvo}", lambda: carregar_perfil_eleitorado(db, settings.ano_alvo)),
        ("ibge_indicadores", lambda: carregar_indicadores(db)),
    ]
    return [_registrar_carga(db, fonte, carregar) for fonte, carregar in etapas]
