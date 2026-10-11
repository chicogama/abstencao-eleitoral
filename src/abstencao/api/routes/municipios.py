from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from abstencao.db.session import get_db
from abstencao.schemas.municipio import MunicipioOut
from abstencao.services import municipio_service

router = APIRouter(prefix="/municipios", tags=["municípios"])


@router.get("/{cd_ibge}", response_model=MunicipioOut)
def obter_municipio(cd_ibge: int, db: Session = Depends(get_db)) -> dict:
    municipio = municipio_service.obter_municipio(db, cd_ibge)
    if municipio is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return municipio
