from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from abstencao.db.base import Base


class IndicadorMunicipio(Base):
    __tablename__ = "indicador_municipio"

    cd_ibge: Mapped[int] = mapped_column(ForeignKey("municipio.cd_ibge"), primary_key=True)
    populacao: Mapped[int | None]
    pib_mil_reais: Mapped[float | None]
    pib_per_capita: Mapped[float | None]
    pct_vab_agro: Mapped[float | None]
    pct_vab_adm_publica: Mapped[float | None]
