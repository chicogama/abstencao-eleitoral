# ETL e treino rodam no worker Arq, e a API só enfileira

O ETL baixa e lê em blocos o perfil do eleitorado de 2026, um ZIP de 408 MB que descompactado tem 4,3 GB. Por isso pode levar vários minutos. O treino também é demorado. Seguindo o `arquitetura.md`, essas tarefas rodam em um worker **Arq** (com Redis), em um processo separado do `uvicorn`. As rotas `POST /pipeline/etl` e `POST /pipeline/treino` apenas publicam na fila e devolvem o id do job.

Um script de linha de comando seria mais simples. A fila foi escolhida para separar a disponibilização (API) do processamento pesado, como no desenho do M4 e do M5. O notebook e o worker usam os mesmos services, de modo que a lógica não fica duplicada.
