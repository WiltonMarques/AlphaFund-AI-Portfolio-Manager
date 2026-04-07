import numpy as np
from scipy.optimize import minimize
import pandas as pd

def calcular_performance_portfolio(pesos, retornos_esperados, matriz_cov):
    """ Calcula o retorno esperado e a volatilidade (risco) de uma dada alocação """
    retorno_portfolio = np.sum(retornos_esperados * pesos)
    risco_portfolio = np.sqrt(np.dot(pesos.T, np.dot(matriz_cov, pesos)))
    return retorno_portfolio, risco_portfolio

def objetivo_sharpe(pesos, retornos_esperados, matriz_cov, taxa_livre_risco):
    """ Função matemática que o algoritmo vai tentar MINIMIZAR (Sharpe negativo) """
    retorno, risco = calcular_performance_portfolio(pesos, retornos_esperados, matriz_cov)
    sharpe = (retorno - taxa_livre_risco) / risco
    # Como a função 'minimize' do SciPy busca o menor valor, retornamos o Sharpe negativo
    return -sharpe

def otimizar_carteira(retornos_esperados, matriz_cov, taxa_livre_risco=0.105):
    """
    Motor matemático que testa milhares de combinações até achar o peso ideal de cada ativo.
    taxa_livre_risco = 10.5% (Aproximação da Selic atual)
    """
    num_ativos = len(retornos_esperados)
    
    # Ponto de partida: dividir o dinheiro igualmente (pesos iguais)
    pesos_iniciais = np.array(num_ativos * [1. / num_ativos])
    
    # Restrições:
    # 1. A soma de todos os pesos deve ser exatamente 1 (100% do capital)
    restricoes = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # 2. Nenhum ativo pode ter peso negativo (Proibido operar vendido / short neste fundo)
    # e nenhum ativo pode passar de 100% (alavancagem)
    limites = tuple((0.0, 1.0) for _ in range(num_ativos))
    
    # Executando o solver matemático (SLSQP é ideal para limites contínuos)
    resultado = minimize(
        objetivo_sharpe, 
        pesos_iniciais, 
        args=(retornos_esperados, matriz_cov, taxa_livre_risco),
        method='SLSQP', 
        bounds=limites, 
        constraints=restricoes
    )
    
    pesos_otimos = resultado.x
    ret_otimo, risco_otimo = calcular_performance_portfolio(pesos_otimos, retornos_esperados, matriz_cov)
    sharpe_otimo = (ret_otimo - taxa_livre_risco) / risco_otimo
    
    return pesos_otimos, ret_otimo, risco_otimo, sharpe_otimo

# Teste integrando os dois módulos
if __name__ == "__main__":
    from ingestao_dados import baixar_historico, calcular_retornos_e_covariancia
    
    print("Iniciando Otimização Institucional...")
    precos = baixar_historico("2022-01-01", "2026-04-01")
    _, retornos_anuais, cov = calcular_retornos_e_covariancia(precos)
    
    pesos, ret, risco, sharpe = otimizar_carteira(retornos_anuais.values, cov.values)
    
    print("\n🎯 ALOCAÇÃO IDEAL (Máximo Índice Sharpe):")
    for ativo, peso in zip(retornos_anuais.index, pesos):
        print(f" - {ativo}: {peso*100:.2f}%")
        
    print(f"\n📊 Expectativa do Fundo:")
    print(f"Retorno Anual: {ret*100:.2f}%")
    print(f"Risco (Volatilidade): {risco*100:.2f}%")
    print(f"Índice Sharpe: {sharpe:.2f}")