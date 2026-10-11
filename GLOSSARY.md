# Abstenção Eleitoral

Estudo da abstenção nas eleições gerais brasileiras, município a município, para entender e prever quantos eleitores aptos deixam de votar.

## Eleição

**Eleição**:
Um pleito identificado pelo ano e pelo turno. O alvo do estudo é o 1º turno da eleição geral de 04/10/2026, e a eleição de 2022 serve de histórico.
_Evite_: pleito, votação (quando o sentido for o evento)

**Turno**:
Cada rodada de votação de uma eleição. Apenas o 1º turno é usado, porque o 2º turno não acontece em todos os municípios.

**Zona eleitoral**:
Unidade administrativa da Justiça Eleitoral que reúne seções. Um município pode ter várias zonas, e uma zona pode abranger mais de um município.
_Evite_: zona (sozinho), seção

## Município

**Município**:
Unidade de análise do estudo: cada linha do conjunto final é um município brasileiro. O exterior não é município e fica fora do estudo.
_Evite_: cidade, localidade

**Código TSE**:
Identificador de cinco dígitos que a Justiça Eleitoral dá ao município. É diferente do código IBGE.

**Código IBGE**:
Identificador de sete dígitos que o IBGE dá ao município. É o elo com os dados socioeconômicos.

## Comparecimento

**Eleitor apto**:
Pessoa registrada e habilitada a votar em um município em uma eleição.
_Evite_: eleitor (sozinho), eleitorado, votante

**Comparecimento**:
Número de eleitores aptos que votaram.
_Evite_: participação, votantes

**Abstenção**:
Número de eleitores aptos que não votaram. É o complemento do comparecimento.
_Evite_: falta, ausência, não comparecimento

**Taxa de abstenção**:
Abstenção dividida pelo número de eleitores aptos do município, entre 0 e 1. É o que o modelo prevê.
_Evite_: percentual de abstenção, índice de abstenção

**Abstenção anterior**:
Taxa de abstenção do mesmo município no 1º turno da eleição geral anterior (2022).
_Evite_: histórico, abstenção passada

## Perfil do eleitorado

**Perfil do eleitorado**:
Composição dos eleitores aptos de um município por faixa etária, grau de instrução e gênero, como registrada pela Justiça Eleitoral para a eleição.
_Evite_: perfil do eleitor, demografia

**Eleitor facultativo**:
Eleitor apto que não é obrigado a votar: quem tem 16 ou 17 anos, quem tem mais de 70 anos e quem é analfabeto.
_Evite_: eleitor opcional, voto facultativo (quando o sentido for a pessoa)

## Contexto socioeconômico

**Indicador socioeconômico**:
Medida do IBGE sobre o município, como população residente, PIB e participação de setores na economia, usada para explicar a abstenção.
_Evite_: dado do IBGE, variável econômica
