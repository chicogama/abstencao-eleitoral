from sqlalchemy import text
from sqlalchemy.orm import Session

from abstencao.services.modelo_service import VERSAO_MODELO

CONSULTA_MUNICIPIO = text(
    """
    SELECT d.cd_ibge, d.nome, d.sg_uf, d.regiao, d.aptos, d.taxa_abstencao,
           d.abstencao_anterior, p.taxa_prevista
    FROM vw_dataset_modelo d
    LEFT JOIN previsao p ON p.cd_ibge = d.cd_ibge AND p.versao_modelo = :versao
    WHERE d.cd_ibge = :cd_ibge
    """
)


def obter_municipio(db: Session, cd_ibge: int) -> dict | None:
    linha = db.execute(CONSULTA_MUNICIPIO, {"cd_ibge": cd_ibge, "versao": VERSAO_MODELO}).mappings().first()
    return dict(linha) if linha else None
