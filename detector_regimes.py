import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from ingestao_dados import baixar_historico

def identificar_regimes(df_precos, n_regimes=3):
    print("🧠 Analisando padrões de comportamento do mercado...")
    
    # 1. Feature Engineering: Criando os indicadores que a IA vai ler
    # Usamos o Ibovespa (Acoes_BR) como termômetro do regime
    retornos = df_precos['Acoes_BR'].pct_change().dropna()
    
    # Calculando média e volatilidade móvel de 20 dias (1 mês comercial)
    features = pd.DataFrame(index=retornos.index)
    features['retorno_movel'] = retornos.rolling(window=20).mean()
    features['volatilidade_movel'] = retornos.rolling(window=20).std()
    features.dropna(inplace=True)
    
    # 2. Normalização: Essencial para algoritmos de clusterização
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # 3. Treinamento do K-Means
    kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
    regimes = kmeans.fit_predict(features_scaled)
    
    features['Regime'] = regimes
    
    # Organizando os regimes por nível de risco (volatilidade) para facilitar a leitura
    # Regime 0 será sempre o de menor volatilidade
    ordem_vol = features.groupby('Regime')['volatilidade_movel'].mean().sort_values().index
    mapeamento = {old: new for new, old in enumerate(ordem_vol)}
    features['Regime'] = features['Regime'].map(mapeamento)
    
    return features

if __name__ == "__main__":
    precos = baixar_historico("2021-01-01", "2026-04-01")
    df_regimes = identificar_regimes(precos)
    
    print("\n📊 Resumo dos Regimes Identificados:")
    resumo = df_regimes.groupby('Regime').agg({
        'retorno_movel': 'mean',
        'volatilidade_movel': 'mean'
    })
    resumo.columns = ['Retorno Médio', 'Volatilidade Média']
    print(resumo)
    
    # Mostrando os últimos dias
    print("\n📅 Regimes dos últimos 5 dias:")
    print(df_regimes['Regime'].tail())