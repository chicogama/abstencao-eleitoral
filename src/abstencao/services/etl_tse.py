import zipfile
from pathlib import Path

import pandas as pd

from abstencao.services.download_service import baixar_arquivo, url_tse

ENCODING_TSE = "latin1"
REGIOES = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}

FAIXAS_16_17 = {1600, 1700}
INICIO_FAIXA_70_MAIS = 7074
ESCOLARIDADE_ANALFABETO = 1
ESCOLARIDADE_SUPERIOR_COMPLETO = 8
GENERO_FEMININO = 4


def _ler_csv_do_zip(caminho_zip: Path, nome_csv: str, **kwargs) -> pd.DataFrame:
    with zipfile.ZipFile(caminho_zip) as arquivo_zip:
        with arquivo_zip.open(nome_csv) as csv:
            return pd.read_csv(csv, sep=";", encoding=ENCODING_TSE, **kwargs)


def extrair_municipios() -> pd.DataFrame:
    caminho = baixar_arquivo(url_tse("municipio_tse_ibge/municipio_tse_ibge.zip"))
    bruto = _ler_csv_do_zip(caminho, "municipio_tse_ibge.csv", dtype={"CD_MUNICIPIO_TSE": str})
    municipios = pd.DataFrame(
        {
            "cd_ibge": bruto["CD_MUNICIPIO_IBGE"].astype(int),
            "cd_tse": bruto["CD_MUNICIPIO_TSE"].str.zfill(5),
            "nome": bruto["NM_MUNICIPIO_IBGE"].str.strip(),
            "sg_uf": bruto["SG_UF"],
        }
    )
    municipios["regiao"] = municipios["cd_ibge"].astype(str).str[0].map(REGIOES)
    return municipios.drop_duplicates("cd_ibge")


def extrair_resultados(ano: int, turno: int = 1) -> pd.DataFrame:
    caminho = baixar_arquivo(url_tse(f"detalhe_votacao_munzona/detalhe_votacao_munzona_{ano}.zip"))
    colunas = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "DS_CARGO", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES"]
    bruto = _ler_csv_do_zip(
        caminho,
        f"detalhe_votacao_munzona_{ano}_BRASIL.csv",
        usecols=colunas,
        dtype={"CD_MUNICIPIO": str},
    )
    filtro = (
        (bruto["NR_TURNO"] == turno)
        & (bruto["DS_CARGO"].str.upper() == "PRESIDENTE")
        & (bruto["SG_UF"] != "ZZ")
    )
    resultados = (
        bruto[filtro]
        .groupby("CD_MUNICIPIO", as_index=False)[["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES"]]
        .sum()
        .rename(
            columns={
                "CD_MUNICIPIO": "cd_tse",
                "QT_APTOS": "aptos",
                "QT_COMPARECIMENTO": "comparecimento",
                "QT_ABSTENCOES": "abstencoes",
            }
        )
    )
    resultados["cd_tse"] = resultados["cd_tse"].str.zfill(5)
    resultados["ano"] = ano
    resultados["turno"] = turno
    return resultados


def _agregar_bloco_perfil(bloco: pd.DataFrame) -> pd.DataFrame:
    qtd = bloco["QT_ELEITORES"]
    marcadores = pd.DataFrame(
        {
            "cd_tse": bloco["CD_MUNICIPIO"],
            "eleitores": qtd,
            "qt_16_17": qtd.where(bloco["CD_FAIXA_ETARIA"].isin(FAIXAS_16_17), 0),
            "qt_70_mais": qtd.where(bloco["CD_FAIXA_ETARIA"] >= INICIO_FAIXA_70_MAIS, 0),
            "qt_analfabeto": qtd.where(bloco["CD_GRAU_ESCOLARIDADE"] == ESCOLARIDADE_ANALFABETO, 0),
            "qt_superior": qtd.where(bloco["CD_GRAU_ESCOLARIDADE"] == ESCOLARIDADE_SUPERIOR_COMPLETO, 0),
            "qt_feminino": qtd.where(bloco["CD_GENERO"] == GENERO_FEMININO, 0),
            "qt_biometria": bloco["QT_ELEITORES_BIOMETRIA"],
        }
    )
    return marcadores.groupby("cd_tse").sum()


def extrair_perfil_eleitorado(ano: int) -> pd.DataFrame:
    caminho = baixar_arquivo(url_tse(f"perfil_eleitorado/perfil_eleitorado_{ano}.zip"))
    colunas = [
        "CD_MUNICIPIO",
        "CD_GENERO",
        "CD_FAIXA_ETARIA",
        "CD_GRAU_ESCOLARIDADE",
        "QT_ELEITORES",
        "QT_ELEITORES_BIOMETRIA",
    ]
    with zipfile.ZipFile(caminho) as arquivo_zip:
        csvs_por_uf = [
            nome
            for nome in arquivo_zip.namelist()
            if nome.endswith(".csv") and not nome.endswith(("_BRASIL.csv", "_ZZ.csv"))
        ]
    parciais = []
    for nome_csv in csvs_por_uf:
        with zipfile.ZipFile(caminho) as arquivo_zip, arquivo_zip.open(nome_csv) as csv:
            blocos = pd.read_csv(
                csv,
                sep=";",
                encoding=ENCODING_TSE,
                usecols=colunas,
                dtype={"CD_MUNICIPIO": str},
                chunksize=500_000,
            )
            parciais.extend(_agregar_bloco_perfil(bloco) for bloco in blocos)

    totais = pd.concat(parciais).groupby(level=0).sum()
    perfil = pd.DataFrame(index=totais.index)
    perfil["eleitores"] = totais["eleitores"]
    for coluna in ["16_17", "70_mais", "analfabeto", "superior", "feminino", "biometria"]:
        perfil[f"pct_{coluna}"] = totais[f"qt_{coluna}"] / totais["eleitores"]
    perfil = perfil.reset_index()
    perfil["cd_tse"] = perfil["cd_tse"].str.zfill(5)
    perfil["ano"] = ano
    return perfil
