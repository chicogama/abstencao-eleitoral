"""view do dataset do modelo

Revision ID: 3f2079ecceec
Revises: 86e33f1feb0f
Create Date: 2026-10-10 22:19:21.138772

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3f2079ecceec'
down_revision: Union[str, Sequence[str], None] = '86e33f1feb0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VIEW_DATASET_MODELO = """
CREATE VIEW vw_dataset_modelo AS
SELECT
    m.cd_ibge,
    m.nome,
    m.sg_uf,
    m.regiao,
    r.aptos,
    r.abstencoes::float8 / r.aptos AS taxa_abstencao,
    ra.abstencoes::float8 / ra.aptos AS abstencao_anterior,
    p.pct_16_17,
    p.pct_70_mais,
    p.pct_analfabeto,
    p.pct_superior,
    p.pct_feminino,
    p.pct_biometria,
    i.populacao,
    i.pib_per_capita,
    i.pct_vab_agro,
    i.pct_vab_adm_publica
FROM municipio m
JOIN resultado_eleicao r
    ON r.cd_ibge = m.cd_ibge AND r.ano = 2026 AND r.turno = 1
LEFT JOIN resultado_eleicao ra
    ON ra.cd_ibge = m.cd_ibge AND ra.ano = 2022 AND ra.turno = 1
LEFT JOIN perfil_eleitorado p
    ON p.cd_ibge = m.cd_ibge AND p.ano = 2026
LEFT JOIN indicador_municipio i
    ON i.cd_ibge = m.cd_ibge
"""


def upgrade() -> None:
    op.execute(VIEW_DATASET_MODELO)


def downgrade() -> None:
    op.execute("DROP VIEW vw_dataset_modelo")
