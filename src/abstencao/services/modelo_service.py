import json
import logging
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from abstencao.core.config import settings
from abstencao.models import Previsao
from abstencao.services.features_service import (
    ALVO,
    FEATURES,
    FEATURES_CATEGORICAS,
    FEATURES_NUMERICAS,
    carregar_dataset,
    criar_features,
    preparar_dataset_modelo,
)

logger = logging.getLogger(__name__)

SEMENTE = 42
PROPORCAO_TESTE = 0.2
FOLDS_VALIDACAO = 5
VERSAO_MODELO = "v1"


@dataclass
class ResultadoTreino:
    metricas: pd.DataFrame
    nome_melhor: str
    modelo: Pipeline
    x_teste: pd.DataFrame
    y_teste: pd.Series
    previsto_teste: np.ndarray


def _pre_processamento() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("numericas", StandardScaler(), FEATURES_NUMERICAS),
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), FEATURES_CATEGORICAS),
        ]
    )


def criar_modelos() -> dict[str, Pipeline]:
    regressores = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=SEMENTE),
        "Gradient Boosting": HistGradientBoostingRegressor(random_state=SEMENTE),
    }
    return {
        nome: Pipeline([("pre_processamento", _pre_processamento()), ("regressor", regressor)])
        for nome, regressor in regressores.items()
    }


def _metricas(y_real: pd.Series, y_previsto: np.ndarray) -> dict[str, float]:
    return {
        "rmse_teste": root_mean_squared_error(y_real, y_previsto),
        "mae_teste": mean_absolute_error(y_real, y_previsto),
        "r2_teste": r2_score(y_real, y_previsto),
    }


def dividir_treino_teste(dados: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        dados[FEATURES], dados[ALVO], test_size=PROPORCAO_TESTE, random_state=SEMENTE
    )


def treinar_e_avaliar(dados: pd.DataFrame) -> ResultadoTreino:
    x_treino, x_teste, y_treino, y_teste = dividir_treino_teste(dados)
    folds = KFold(n_splits=FOLDS_VALIDACAO, shuffle=True, random_state=SEMENTE)

    linhas = [
        {"modelo": "Baseline: média", "rmse_cv": np.nan, **_metricas(y_teste, np.full(len(y_teste), y_treino.mean()))},
        {"modelo": "Baseline: repetir 2022", "rmse_cv": np.nan, **_metricas(y_teste, x_teste["abstencao_anterior"])},
    ]
    treinados: dict[str, Pipeline] = {}
    for nome, modelo in criar_modelos().items():
        rmse_cv = -cross_val_score(
            modelo, x_treino, y_treino, cv=folds, scoring="neg_root_mean_squared_error"
        ).mean()
        modelo.fit(x_treino, y_treino)
        treinados[nome] = modelo
        linhas.append({"modelo": nome, "rmse_cv": rmse_cv, **_metricas(y_teste, modelo.predict(x_teste))})
        logger.info("%s: RMSE CV %.5f", nome, rmse_cv)

    metricas = pd.DataFrame(linhas).set_index("modelo")
    nome_melhor = metricas["rmse_cv"].idxmin()
    melhor = treinados[nome_melhor]
    return ResultadoTreino(metricas, nome_melhor, melhor, x_teste, y_teste, melhor.predict(x_teste))


def caminho_modelo() -> Path:
    return settings.dir_modelos / f"modelo_abstencao_{VERSAO_MODELO}.pkl"


def salvar_modelo(resultado: ResultadoTreino) -> Path:
    settings.dir_modelos.mkdir(parents=True, exist_ok=True)
    pacote = {
        "versao": VERSAO_MODELO,
        "modelo_nome": resultado.nome_melhor,
        "modelo": resultado.modelo,
        "features": FEATURES,
    }
    joblib.dump(pacote, caminho_modelo())

    relatorio = {
        "versao": VERSAO_MODELO,
        "modelo_escolhido": resultado.nome_melhor,
        "criterio": "menor RMSE na validação cruzada (5 folds) do treino",
        "metricas": resultado.metricas.round(5).reset_index().astype(object).where(
            resultado.metricas.reset_index().notna(), None
        ).to_dict("records"),
    }
    caminho_relatorio = settings.dir_modelos / f"metricas_{VERSAO_MODELO}.json"
    caminho_relatorio.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho_modelo()


def carregar_modelo() -> dict:
    return joblib.load(caminho_modelo())


def gravar_previsoes(db: Session, modelo: Pipeline, dados: pd.DataFrame) -> int:
    previsoes = pd.DataFrame(
        {
            "cd_ibge": dados["cd_ibge"],
            "versao_modelo": VERSAO_MODELO,
            "taxa_prevista": modelo.predict(dados[FEATURES]),
        }
    )
    db.execute(delete(Previsao).where(Previsao.versao_modelo == VERSAO_MODELO))
    db.execute(insert(Previsao), previsoes.to_dict("records"))
    db.commit()
    return len(previsoes)


def prever(entrada: dict) -> float:
    pacote = carregar_modelo()
    features = criar_features(pd.DataFrame([entrada]))
    return float(pacote["modelo"].predict(features[pacote["features"]])[0])


def executar_treino(db: Session) -> dict:
    dados = preparar_dataset_modelo(carregar_dataset(db))
    resultado = treinar_e_avaliar(dados)
    salvar_modelo(resultado)
    total_previsoes = gravar_previsoes(db, resultado.modelo, dados)
    linha_melhor = resultado.metricas.loc[resultado.nome_melhor]
    return {
        "modelo": resultado.nome_melhor,
        "rmse_teste": round(float(linha_melhor["rmse_teste"]), 5),
        "r2_teste": round(float(linha_melhor["r2_teste"]), 4),
        "previsoes_gravadas": total_previsoes,
    }
