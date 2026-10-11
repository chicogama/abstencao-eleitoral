import pandas as pd
import requests

from abstencao.core.config import settings

TABELA_PIB = 5938
PERIODO_PIB = 2023
VARIAVEIS_PIB = {37: "pib_mil_reais"}
PERIODO_VAB_SETORIAL = 2021
VARIAVEIS_VAB = {498: "vab_total", 513: "vab_agro", 525: "vab_adm_publica"}

TABELA_POPULACAO = 4709
PERIODO_POPULACAO = 2022
VARIAVEL_POPULACAO = {93: "populacao"}


def _consultar_agregado(tabela: int, periodo: int, variaveis: dict[int, str]) -> pd.DataFrame:
    ids = "|".join(str(v) for v in variaveis)
    url = f"{settings.url_ibge}/{tabela}/periodos/{periodo}/variaveis/{ids}"
    resposta = requests.get(url, params={"localidades": "N6[all]"}, timeout=120)
    resposta.raise_for_status()

    colunas = {}
    for variavel in resposta.json():
        nome = variaveis[int(variavel["id"])]
        serie = variavel["resultados"][0]["series"]
        colunas[nome] = {
            int(item["localidade"]["id"]): item["serie"][str(periodo)] for item in serie
        }
    tabela_df = pd.DataFrame(colunas)
    tabela_df.index.name = "cd_ibge"
    return tabela_df.apply(pd.to_numeric, errors="coerce")


def extrair_indicadores() -> pd.DataFrame:
    pib = _consultar_agregado(TABELA_PIB, PERIODO_PIB, VARIAVEIS_PIB)
    vab = _consultar_agregado(TABELA_PIB, PERIODO_VAB_SETORIAL, VARIAVEIS_VAB)
    populacao = _consultar_agregado(TABELA_POPULACAO, PERIODO_POPULACAO, VARIAVEL_POPULACAO)
    indicadores = pib.join([vab, populacao], how="outer")
    indicadores["pib_per_capita"] = indicadores["pib_mil_reais"] * 1000 / indicadores["populacao"]
    indicadores["pct_vab_agro"] = indicadores["vab_agro"] / indicadores["vab_total"]
    indicadores["pct_vab_adm_publica"] = indicadores["vab_adm_publica"] / indicadores["vab_total"]
    indicadores = indicadores.drop(columns=["vab_total", "vab_agro", "vab_adm_publica"])
    indicadores["populacao"] = indicadores["populacao"].astype("Int64")
    return indicadores.reset_index()
