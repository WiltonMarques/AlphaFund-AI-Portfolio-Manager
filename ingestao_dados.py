import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# CONFIGURAÇÃO DO UNIVERSO DE INVESTIMENTO
# ==========================================
# Representação do fundo em 5 grandes classes macroeconômicas
ATIVOS = {
    "Acoes_BR": "BOVA11.SA",       # Risco Brasil (Ibovespa)
    "Acoes_EUA": "IVVB11.SA",      # Risco Global (S&P 500 em Reais)
    "Renda_Fixa": "B5P211.SA",     # Títulos Públicos (Inflação IPCA)
    "Ouro": "GOLD11.SA",           # Proteção / Reserva de Valor
    "Moeda": "USDBRL=X"            # Hedge Cambial Direto
}

def baixar_historico(data_inicio, data_fim):
    """
    Baixa os preços de fechamento e trata valores nulos.
    """
    print("⏳ Baixando dados do mercado...")
    tickers = list(ATIVOS.values())
    
    # Download em lote via Yahoo Finance (Usando 'Close' para versões recentes da API)
    df_precos = yf.download(tickers, start=data_inicio, end=data_fim)['Close']
    
    # Renomeando as colunas para os nomes das classes (mais elegante para o painel)
    mapa_inverso = {v: k for k, v in ATIVOS.items()}
    df_precos.rename(columns=mapa_inverso, inplace=True)
    
    # Preenchendo buracos de feriados locais/internacionais com o preço do dia anterior (método atualizado)
    df_precos.ffill(inplace=True)
    df_precos.dropna(inplace=True) # Remove linhas iniciais se algum ativo for muito novo
    
    print(f"✅ Dados carregados! {len(df_precos)} dias úteis processados.")
    return df_precos

def calcular_retornos_e_covariancia(df_precos):
    """
    Transforma preços absolutos em retornos percentuais e calcula a matriz de risco.
    """
    # Retorno diário logarítmico (padrão institucional) ou percentual simples
    df_retornos = df_precos.pct_change().dropna()
    
    # Anualizando os retornos esperados (média diária * 252 dias úteis)
    retornos_anualizados = df_retornos.mean() * 252
    
    # Matriz de covariância anualizada (mede como os ativos se movem juntos)
    matriz_cov = df_retornos.cov() * 252
    
    return df_retornos, retornos_anualizados, matriz_cov

# Teste rápido do módulo
if __name__ == "__main__":
    precos = baixar_historico("2021-01-01", "2026-04-01")
    retornos, ret_anuais, cov = calcular_retornos_e_covariancia(precos)
    print("\n📈 Retornos Esperados (Anualizados):")
    print(ret_anuais)