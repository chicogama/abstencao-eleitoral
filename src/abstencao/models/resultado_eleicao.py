from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from abstencao.db.base import Base


class ResultadoEleicao(Base):
    __tablename__ = "resultado_eleicao"

    cd_ibge: Mapped[int] = mapped_column(ForeignKey("municipio.cd_ibge"), primary_key=True)
    ano: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    turno: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    aptos: Mapped[int]
    comparecimento: Mapped[int]
    abstencoes: Mapped[int]
