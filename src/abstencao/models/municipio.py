from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from abstencao.db.base import Base


class Municipio(Base):
    __tablename__ = "municipio"

    cd_ibge: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    cd_tse: Mapped[str] = mapped_column(String(5), unique=True)
    nome: Mapped[str] = mapped_column(String(100))
    sg_uf: Mapped[str] = mapped_column(String(2), index=True)
    regiao: Mapped[str] = mapped_column(String(20))
