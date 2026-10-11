from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_PROJETO = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=RAIZ_PROJETO / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://abstencao:abstencao@localhost:5432/abstencao"
    redis_url: str = "redis://localhost:6379"

    dir_raw: Path = RAIZ_PROJETO / "data" / "raw"
    dir_modelos: Path = RAIZ_PROJETO / "models"

    url_tse: str = "https://cdn.tse.jus.br/estatistica/sead/odsele"
    url_ibge: str = "https://servicodados.ibge.gov.br/api/v3/agregados"

    ano_alvo: int = 2026
    ano_anterior: int = 2022


settings = Settings()
