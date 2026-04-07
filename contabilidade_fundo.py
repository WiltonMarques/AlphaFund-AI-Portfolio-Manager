import pandas as pd
import numpy as np

def calcular_contabilidade_institucional(df_precos, pesos_alocacao, capital_inicial=10000000.0, 
                                        taxa_adm_anual=0.02, taxa_perf_pct=0.20, cdi_anual=0.105):
    """
    Simula a vida do fundo com provisão de taxas e cálculo de performance (Hurdle: CDI).
    """
    print(f"💰 Iniciando processamento contábil com provisão de taxas (PL: R$ {capital_inicial:,.2f})")
    
    # 1. Retornos Brutos
    retornos_diarios = df_precos.pct_change().dropna()
    retorno_bruto_carteira = retornos_diarios.dot(pesos_alocacao)
    
    # 2. Definição das Taxas Diárias (Base 252 dias úteis)
    taxa_adm_diaria = (1 + taxa_adm_anual)**(1/252) - 1
    cdi_diario = (1 + cdi_anual)**(1/252) - 1
    
    # 3. Processamento Dia a Dia (Marcação a Mercado + Provisões)
    pl_bruto = capital_inicial
    benchmark_acumulado = capital_inicial
    pl_lista = [capital_inicial]
    despesas_adm_acum = 0
    despesas_perf_acum = 0
    
    for r_bruto in retorno_bruto_carteira:
        # Valorização do PL antes das taxas
        pl_bruto = pl_bruto * (1 + r_bruto)
        benchmark_acumulado = benchmark_acumulado * (1 + cdi_diario)
        
        # Provisão de Taxa de Administração
        prov_adm = pl_bruto * taxa_adm_diaria
        despesas_adm_acum += prov_adm
        pl_apos_adm = pl_bruto - prov_adm
        
        # Provisão de Taxa de Performance (Calculada sobre o lucro que excede o CDI)
        lucro_excedente = pl_apos_adm - benchmark_acumulado
        prov_perf = 0
        if lucro_excedente > 0:
            prov_perf = lucro_excedente * taxa_perf_pct
            despesas_perf_acum += prov_perf
        
        pl_final_dia = pl_apos_adm - prov_perf
        pl_lista.append(pl_final_dia)
        pl_bruto = pl_final_dia # O PL do dia seguinte parte do valor líquido

    pl_diario = pd.Series(pl_lista, index=df_precos.index)
    
    return pl_diario, despesas_adm_acum, despesas_perf_acum, benchmark_acumulado

def gerar_dre_institucional(pl_diario, despesas_adm, despesas_perf, nomes_ativos, pesos, precos):
    """
    Gera a DRE espelhada no Estudo de Caso de Fundos Multimercado.
    """
    inicio = pl_diario.index[0]
    fim = pl_diario.index[-1]
    pl_inicial = pl_diario.iloc[0]
    pl_final = pl_diario.iloc[-1]
    lucro_bruto_total = (pl_final + despesas_adm + despesas_perf) - pl_inicial
    
    print("\n" + "="*80)
    print("🏛️ DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO (DRE) - AlphaFund")
    print("="*80)
    print(f"Período: {inicio.date()} a {fim.date()}")
    print("-" * 80)
    
    print(f"7.0.0.00.00 RECEITAS COM INVESTIMENTOS (LUCRO BRUTO){' ':<12} R$ {lucro_bruto_total:>15,.2f}")
    
    # Detalhamento por classe de ativos (Marcação a Mercado)
    retornos_totais = precos.iloc[-1] / precos.iloc[0] - 1
    for i, ativo in enumerate(nomes_ativos):
        peso = pesos[i]
        contribuicao = (peso * lucro_bruto_total) 
        if peso > 0:
            print(f"  7.1.{i}.00.00   Resultado com {ativo:<25} R$ {contribuicao:>15,.2f}")
            
    print(f"\n8.0.0.00.00 DESPESAS OPERACIONAIS{' ':<29} (R$ {despesas_adm + despesas_perf:>14,.2f})")
    print(f"  8.1.1.00.00   Taxa de Administração (2% a.a.){' ':<14} (R$ {despesas_adm:>14,.2f})")
    print(f"  8.1.2.00.00   Taxa de Performance (20% s/ CDI){' ':<13} (R$ {despesas_perf:>14,.2f})")
    
    print("-" * 80)
    print(f"RESULTADO LÍQUIDO DO EXERCÍCIO{' ':<32} R$ {pl_final - pl_inicial:>15,.2f}")
    print(f"PATRIMÔNIO LÍQUIDO FINAL{' ':<38} R$ {pl_final:>15,.2f}")
    print(f"RENTABILIDADE LÍQUIDA NO PERÍODO{' ':<34} {((pl_final/pl_inicial)-1)*100:>14.2f}%")
    print("="*80)

if __name__ == "__main__":
    from ingestao_dados import baixar_historico, calcular_retornos_e_covariancia
    from otimizador_markowitz import otimizar_carteira
    
    # Configurações
    CAPITAL = 10000000.0
    CDI_BENCHMARK = 0.105 # Hurdle Rate
    
    # 1. Fluxo de Dados e Inteligência
    precos = baixar_historico("2022-01-01", "2026-04-01")
    _, ret_anuais, cov = calcular_retornos_e_covariancia(precos)
    pesos, _, _, _ = otimizar_carteira(ret_anuais.values, cov.values)
    
    # 2. Processamento Contábil Institucional
    pl_series, adm, perf, _ = calcular_contabilidade_institucional(
        precos, pesos, capital_inicial=CAPITAL, cdi_anual=CDI_BENCHMARK
    )
    
    # 3. Publicação da Peça Contábil
    gerar_dre_institucional(pl_series, adm, perf, ret_anuais.index, pesos, precos)