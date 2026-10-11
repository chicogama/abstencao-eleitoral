from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from abstencao.db.base import Base


class PerfilEleitorado(Base):
    __tablename__ = "perfil_eleitorado"

    cd_ibge: Mapped[int] = mapped_column(ForeignKey("municipio.cd_ibge"), primary_key=True)
    ano: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    eleitores: Mapped[int]
    pct_16_17: Mapped[float]
    pct_70_mais: Mapped[float]
    pct_analfabeto: Mapped[float]
    pct_superior: Mapped[float]
    pct_feminino: Mapped[float]
    pct_biometria: Mapped[float]
