# Cargo Presidente como base dos eleitores aptos e da abstenção

O arquivo de apuração do TSE (`detalhe_votacao_munzona`) repete aptos e abstenções em cada cargo, e os números variam um pouco entre eles. Isso acontece por causa do voto em trânsito: quem vota fora do domicílio eleitoral só vota para Presidente. Usamos apenas as linhas do cargo **Presidente**, 1º turno, porque é o único cargo que abrange todos os eleitores aptos do país. Assim a taxa de abstenção de um município é sempre calculada sobre o mesmo universo, em 2022 e em 2026. O exterior (UF `ZZ`) fica de fora.
