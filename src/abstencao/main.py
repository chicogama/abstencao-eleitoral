from fastapi import FastAPI

from abstencao.api.routes import municipios, pipeline, previsao

app = FastAPI(
    title="Abstenção Eleitoral 2026",
    description="Pipeline de dados do TSE e do IBGE e modelo de regressão da taxa de abstenção por município.",
)
app.include_router(pipeline.router)
app.include_router(municipios.router)
app.include_router(previsao.router)
