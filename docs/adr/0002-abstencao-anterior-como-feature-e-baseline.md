# Abstenção anterior como feature e como baseline

A taxa de abstenção de 2022 de cada município entra como feature do modelo de 2026. Só ela já explica boa parte do alvo: a correlação é 0,81, e usá-la sozinha como previsão dá RMSE 0,0286, contra 0,040 do desvio padrão do alvo. Por isso o modelo é sempre comparado com dois baselines, "prever a média" e "repetir 2022". O modelo só tem valor se ganhar do segundo. Sem essa comparação, um RMSE baixo pareceria mérito do modelo, quando na verdade viria da persistência da abstenção.

Boa Esperança do Norte (MT) não existia em 2022. O município fica fora do conjunto de modelagem e aparece como limitação no README. Pelo mesmo critério, que é não imputar valores para casos isolados, Cachoeira Dourada (GO) também fica de fora: o VAB total do município foi negativo em 2021, e a participação setorial não tem sentido nesse caso.
