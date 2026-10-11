# Projeto Integrador: abstenção eleitoral por município (2026)

**Banco de Dados para Engenharia de Dados**, Especialização UNIFAP (Departamento de Educação a Distância), turma 2026.1
**Autor:** Josemar Ferreira Gama

Pipeline *end-to-end* de Engenharia de Dados e Machine Learning. O pipeline coleta dados abertos do **TSE** e do **IBGE**, armazena tudo em um modelo relacional no **PostgreSQL** com um ETL em Python e treina um modelo de **regressão** que prevê a **taxa de abstenção** de cada município brasileiro no 1º turno da eleição geral de **04/10/2026**.

## Resultado

| Modelo | RMSE (CV 5 folds) | RMSE (teste) | MAE (teste) | R² (teste) |
|---|---|---|---|---|
| Baseline: prever a média | – | 0,0395 | 0,0312 | 0,000 |
| Baseline: repetir a abstenção de 2022 | – | 0,0281 | 0,0211 | 0,493 |
| Linear Regression | 0,0195 | 0,0186 | 0,0147 | 0,777 |
| Random Forest | 0,0187 | 0,0179 | 0,0137 | 0,795 |
| **Gradient Boosting (escolhido)** | **0,0180** | **0,0171** | **0,0132** | **0,812** |

O modelo erra em média **1,3 ponto percentual** (MAE). Isso é **39% menos erro (RMSE)** do que simplesmente repetir a abstenção de 2022. Depois do histórico, os fatores que mais pesam são a UF, o percentual de eleitores com **biometria** (mais biometria, menos abstenção) e o peso dos **eleitores facultativos** (16–17 anos, 70+ e analfabetos). A análise completa está no notebook [`notebooks/projeto_integrador.ipynb`](notebooks/projeto_integrador.ipynb), e as métricas ficam salvas em [`models/metricas_v1.json`](models/metricas_v1.json).

## Arquitetura

```
                ┌──────────── worker Arq (processo separado) ─────────────┐
TSE (CSV/ZIP) ──┤                                                         │
                ├─► ETL Python ─► PostgreSQL ─► vw_dataset_modelo ─► Features ─► 3 modelos + 2 baselines
IBGE (API) ─────┤   (log em carga_etl)                                      │
                └───────────────────────────────────────── modelo .pkl ◄────┘ ─► previsao (PostgreSQL)
                                     ▲                          │
                             fila Redis                         ▼
                                     │                 API FastAPI: /municipios, /prever
                       API FastAPI: POST /pipeline/etl | /pipeline/treino (só enfileiram)
```

A organização em camadas segue o guia de arquitetura do projeto: `routes` → `services` → `models`/`db`.
- As rotas nunca acessam o banco diretamente.
- As rotas de pipeline só **enfileiram** no Arq, e quem processa é o worker ([ADR 0003](docs/adr/0003-etl-e-treino-no-worker-arq.md)).
- O notebook, o worker, o CLI e a API usam as **mesmas funções** de `services/`.

## Fontes de dados

| # | Fonte | Formato | Uso |
|---|---|---|---|
| 1 | [TSE: códigos de municípios TSE × IBGE](https://dadosabertos.tse.jus.br/dataset/codigos-oficiais-de-uf-e-municipios-segundo-o-tse-e-o-ibge) | CSV em ZIP | dimensão `municipio` e ligação entre as bases |
| 2 | [TSE: Resultados 2022](https://dadosabertos.tse.jus.br/dataset/resultados-2022) e [2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026), detalhe da apuração por município e zona | CSV em ZIP | alvo (2026) e abstenção anterior (2022) |
| 3 | [TSE: Eleitorado, perfil do eleitorado 2026](https://dadosabertos.tse.jus.br/dataset/?groups=eleitorado) | CSV em ZIP (408 MB, 4,3 GB descompactado) | idade, instrução, gênero e biometria por município |
| 4 | [IBGE: API de agregados](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3), tabelas 5938 (PIB dos municípios) e 4709 (Censo 2022) | JSON | população, PIB per capita e estrutura do PIB |

## Modelo de dados (PostgreSQL)

| Tabela | Grão | Conteúdo |
|---|---|---|
| `municipio` | 1 por município | `cd_ibge` (PK), `cd_tse`, nome, UF, região |
| `resultado_eleicao` | município × ano × turno | aptos, comparecimento, abstenções |
| `perfil_eleitorado` | município × ano | total de eleitores e % de 16–17 anos, 70+, analfabetos, superior completo, mulheres, biometria |
| `indicador_municipio` | 1 por município | população, PIB, PIB per capita, % VAB agropecuária, % VAB administração pública |
| `carga_etl` | 1 por execução de fonte | fonte, início, fim, linhas, status, mensagem de erro |
| `previsao` | município × versão do modelo | taxa prevista |
| `vw_dataset_modelo` (view) | 1 por município | junção de tudo, entrada do modelo |

O esquema é criado e versionado pelas migrations do **Alembic** (`alembic/versions/`).

## Estrutura do repositório

```
projeto-integrador/
├── README.md
├── GLOSSARY.md                     # vocabulário do domínio (abstenção, eleitor apto, ...)
├── docs/adr/                       # decisões técnicas registradas
├── compose.yml                     # PostgreSQL 16 + Redis 7
├── .env.example
├── pyproject.toml / uv.lock        # dependências (uv)
├── alembic.ini / alembic/          # migrations do banco
├── notebooks/
│   └── projeto_integrador.ipynb    # notebook final: ETL, qualidade, EDA, features, modelos, métricas
├── models/
│   └── metricas_v1.json            # métricas do último treino (o .pkl é gerado, não versionado)
├── data/raw/                       # downloads do TSE (gerado, não versionado)
└── src/abstencao/
    ├── main.py                     # app FastAPI
    ├── cli.py                      # pipeline por linha de comando
    ├── core/config.py              # configurações (pydantic-settings)
    ├── db/                         # Base declarativa, engine e sessão
    ├── models/                     # tabelas SQLAlchemy
    ├── schemas/                    # entrada e saída da API (Pydantic)
    ├── services/
    │   ├── download_service.py     # download com cache em data/raw
    │   ├── etl_tse.py              # extração e transformação dos arquivos do TSE
    │   ├── etl_ibge.py             # extração e transformação da API do IBGE
    │   ├── etl_service.py          # orquestra o ETL e registra o log em carga_etl
    │   ├── features_service.py     # dataset do modelo e Feature Engineering
    │   ├── modelo_service.py       # treino, avaliação, baselines, .pkl e previsões
    │   ├── municipio_service.py    # consulta usada pela API
    │   └── processing_service.py   # enfileira e consulta jobs no Arq
    ├── worker/
    │   ├── tasks.py                # tarefas executadas pelo worker
    │   └── worker_settings.py      # configuração do Arq
    └── api/routes/                 # pipeline.py, municipios.py, previsao.py
```

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) (ele instala o Python 3.13 sozinho, se for preciso)
- Podman com `podman-compose` (ou Docker com `docker compose`)
- Cerca de 1 GB livre em disco para os downloads do TSE

## Como executar do zero

```bash
# 1. Dependências e configuração
uv sync
cp .env.example .env

# 2. PostgreSQL e Redis
podman-compose up -d

# 3. Esquema do banco
uv run alembic upgrade head
```

A partir daqui há dois caminhos que chegam ao mesmo resultado.

**A) Pela API e pelo worker**, que é a arquitetura completa. Use dois terminais:

```bash
uv run arq abstencao.worker.worker_settings.WorkerSettings   # terminal 1: worker
uv run uvicorn abstencao.main:app --port 8000                # terminal 2: API
```

```bash
curl -X POST localhost:8000/pipeline/etl          # devolve {"job_id": ...}
curl localhost:8000/pipeline/jobs/<job_id>        # acompanha até "complete"
curl -X POST localhost:8000/pipeline/treino
curl localhost:8000/municipios/1600303            # Macapá: taxa real e prevista
```

A documentação interativa fica em <http://localhost:8000/docs>.

**B) Pelo notebook ou pelo CLI:**

```bash
uv run jupyter lab notebooks/projeto_integrador.ipynb   # roda ETL, EDA e treino
# ou
uv run python -m abstencao.cli tudo
```

O primeiro ETL baixa cerca de 420 MB do TSE. As execuções seguintes reaproveitam os arquivos de `data/raw/`, e o ETL completo leva cerca de 20 segundos.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/pipeline/etl` | enfileira o ETL e devolve `job_id` (202) |
| POST | `/pipeline/treino` | enfileira o treino e devolve `job_id` (202) |
| GET | `/pipeline/jobs/{job_id}` | status e resultado do job |
| GET | `/municipios/{cd_ibge}` | dados do município, taxa real de 2026 e taxa prevista |
| POST | `/prever` | recebe as features de um município e devolve a taxa prevista |

## Decisões técnicas

- [ADR 0001](docs/adr/0001-cargo-presidente-como-base-da-abstencao.md): aptos e abstenções vêm do cargo **Presidente**, 1º turno, o único que abrange todos os eleitores (por causa do voto em trânsito).
- [ADR 0002](docs/adr/0002-abstencao-anterior-como-feature-e-baseline.md): a **abstenção de 2022** é feature e também baseline. O modelo só vale se ganhar de "repetir 2022".
- [ADR 0003](docs/adr/0003-etl-e-treino-no-worker-arq.md): ETL e treino rodam no **worker Arq**, e a API só enfileira.
- O perfil do eleitorado é lido em blocos de 500 mil linhas, só dos CSVs por UF. O arquivo `BRASIL` repete as UFs e o `ZZ` é o exterior.
- O IBGE publica o VAB por setor só até **2021** e o PIB total até 2023. O PIB per capita usa PIB 2023 e Censo 2022.
- Para evitar vazamento: nenhuma feature usa votos ou comparecimento de 2026, e o `StandardScaler` e o `OneHotEncoder` ficam dentro do `Pipeline` do scikit-learn.

## Limitações

- **Boa Esperança do Norte (MT)** foi criado depois de 2022 e não tem histórico. **Cachoeira Dourada (GO)** teve VAB total negativo em 2021. Os dois ficam fora da modelagem: são 5.569 de 5.571 municípios.
- O split treino/teste é aleatório entre municípios da mesma eleição. Uma validação temporal (treinar em 2018 → 2022 e testar em 2022 → 2026) seria mais exigente.
- Fatores locais, como disputa acirrada, distância até a seção e clima no dia, não estão nas fontes usadas.
