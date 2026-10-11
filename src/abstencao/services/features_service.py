import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

ALVO = "taxa_abstencao"

FEATURES_NUMERICAS = [
    "abstencao_anterior",
    "pct_16_17",
    "pct_70_mais",
    "pct_analfabeto",
    "pct_superior",
    "pct_feminino",
    "pct_biometria",
    "log_aptos",
    "log_populacao",
    "log_pib_per_capita",
    "pct_vab_agro",
    "pct_vab_adm_publica",
    "razao_aptos_populacao",
]
FEATURES_CATEGORICAS = ["sg_uf"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

COLUNAS_ENTRADA = [
    "abstencao_anterior",
    "pct_16_17",
    "pct_70_mais",
    "pct_analfabeto",
    "pct_superior",
    "pct_feminino",
    "pct_biometria",
    "aptos",
    "populacao",
    "pib_per_capita",
    "pct_vab_agro",
    "pct_vab_adm_publica",
    "sg_uf",
]


def carregar_dataset(db: Session) -> pd.DataFrame:
    return pd.read_sql(text("SELECT * FROM vw_dataset_modelo ORDER BY cd_ibge"), db.connection())


def criar_features(dados: pd.DataFrame) -> pd.DataFrame:
    features = dados.copy()
    features["log_aptos"] = np.log(features["aptos"])
    features["log_populacao"] = np.log(features["populacao"])
    features["log_pib_per_capita"] = np.log(features["pib_per_capita"])
    features["razao_aptos_populacao"] = features["aptos"] / features["populacao"]
    return features


def preparar_dataset_modelo(dados: pd.DataFrame) -> pd.DataFrame:
    completos = dados.dropna(subset=COLUNAS_ENTRADA + [ALVO])
    return criar_features(completos).reset_index(drop=True)
