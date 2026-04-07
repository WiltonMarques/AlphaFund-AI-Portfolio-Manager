import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from ingestao_dados import baixar_historico, calcular_retornos_e_covariancia
from otimizador_markowitz import otimizar_carteira
from contabilidade_fundo import calcular_contabilidade_institucional
from detector_regimes import identificar_regimes

# Configuração da página
st.set_page_config(page_title="AlphaFund | Institucional", layout="wide")

st.title("🏛️ AlphaFund: AI Portfolio Manager")
st.markdown("Sistema Quantitativo de Alocação e Contabilidade Institucional (COSIF/CVM)")
st.markdown("---")

# ==========================================
# BARRA LATERAL (Parâmetros do Fundo)
# ==========================================
st.sidebar.header("Parâmetros do Fundo")
capital_inicial = st.sidebar.number_input("Capital Inicial (R$)", value=10000000.0, step=1000000.0)
taxa_adm = st.sidebar.slider("Taxa de Administração (% a.a.)", 0.0, 5.0, 2.0) / 100
taxa_perf = st.sidebar.slider("Taxa de Performance (% s/ Alpha)", 0.0, 30.0, 20.0) / 100

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Gestão de Risco")
protocolo_defesa = st.sidebar.checkbox("Ativar Protocolo de Defesa (Forçar Renda Fixa)", value=False)

data_inicio = st.sidebar.date_input("Data de Início", pd.to_datetime("2022-01-01"))
data_fim = st.sidebar.date_input("Data de Fim", pd.to_datetime("2026-03-31"))

# ==========================================
# MOTOR PRINCIPAL
# ==========================================
if st.sidebar.button("Executar Fechamento Contábil"):
    with st.spinner("Conectando à B3 e processando Inteligência Artificial..."):
        
        precos = baixar_historico(data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d"))
        _, ret_anuais, cov = calcular_retornos_e_covariancia(precos)
        
        # IA - Detecção de Regime Macroeconômico
        df_regimes = identificar_regimes(precos)
        regime_atual = df_regimes['Regime'].iloc[-1]
        
        # Otimização Matemática Original
        pesos_originais, _, _, _ = otimizar_carteira(ret_anuais.values, cov.values)
        pesos = pesos_originais.copy()
        
        # 🛡️ LÓGICA DE INTERVENÇÃO E GERAÇÃO DE RELATÓRIO
        if protocolo_defesa:
            lista_ativos = list(ret_anuais.index)
            idx_rf = lista_ativos.index('Renda_Fixa')
            idx_br = lista_ativos.index('Acoes_BR')
            idx_eua = lista_ativos.index('Acoes_EUA')
            
            peso_transferido = pesos[idx_br] + pesos[idx_eua]
            pesos[idx_rf] += peso_transferido
            pesos[idx_br] = 0.0
            pesos[idx_eua] = 0.0
        
        # Contabilidade Institucional
        pl_series, adm, perf, _ = calcular_contabilidade_institucional(
            precos, pesos, 
            capital_inicial=capital_inicial, taxa_adm_anual=taxa_adm, taxa_perf_pct=taxa_perf
        )
        
        # ==========================================
        # RENDERIZAÇÃO DO DASHBOARD
        # ==========================================
        st.header("📑 Resumo do Fechamento (DRE)")
        
        pl_final = pl_series.iloc[-1]
        rentabilidade = ((pl_final / capital_inicial) - 1) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Patrimônio Líquido Inicial", f"R$ {capital_inicial:,.2f}")
        col2.metric("Patrimônio Líquido Final", f"R$ {pl_final:,.2f}")
        col3.metric("Rentabilidade Líquida", f"{rentabilidade:.2f}%")
        col4.metric("Receita da Asset (Taxas)", f"R$ {adm + perf:,.2f}")

        st.markdown("---")
        
        st.subheader("🧠 Leitura de Risco Macroeconômico (IA)")
        
        if protocolo_defesa:
            st.info("🛡️ **OVERLAY DE GESTÃO ATIVO:** Renda Variável zerada. Capital realocado para Renda Fixa para mitigação de crise.")
            
            # NOVO: Relatório de Remanejamento
            st.markdown("#### 🔄 Relatório Sumarizado de Remanejamento (Giro de Risco)")
            
            df_remanejamento = pd.DataFrame({
                'Ativo': ret_anuais.index,
                'Peso Original (Markowitz)': (pesos_originais * 100).round(2),
                'Peso Pós-Intervenção': (pesos * 100).round(2),
                'Variação (Delta %)': ((pesos - pesos_originais) * 100).round(2),
                'Volume Deslocado (R$)': ((pesos - pesos_originais) * capital_inicial).round(2)
            })
            
            # Classificação da Ação Executada
            def classificar_acao(delta):
                if delta > 0.1: return "🟢 Aporte Defensivo"
                elif delta < -0.1: return "🔴 Liquidação de Risco"
                else: return "⚪ Manutenção"
                
            df_remanejamento['Ação Executada'] = df_remanejamento['Variação (Delta %)'].apply(classificar_acao)
            
            # Formatação visual da tabela
            st.dataframe(
                df_remanejamento.style.format({
                    'Peso Original (Markowitz)': '{:.2f}%',
                    'Peso Pós-Intervenção': '{:.2f}%',
                    'Variação (Delta %)': '{:+.2f}%',
                    'Volume Deslocado (R$)': 'R$ {:,.2f}'
                }).applymap(lambda x: 'color: red' if isinstance(x, str) and x.startswith('-') else ('color: green' if isinstance(x, str) and x.startswith('+') else ''), subset=['Variação (Delta %)']),
                use_container_width=True
            )
            
        elif regime_atual == 2:
            st.error(f"🚨 **ALERTA VERMELHO (Cenário de Crise):** O modelo detectou ALTA VOLATILIDADE (Regime {regime_atual}). Risco iminente de perdas. **Ação Recomendada:** Ativar Protocolo de Defesa no menu lateral.")
        elif regime_atual == 1:
            st.warning(f"⚠️ **ALERTA AMARELO (Transição):** Volatilidade moderada (Regime {regime_atual}).")
        else:
            st.success(f"✅ **CENÁRIO ESTÁVEL:** Baixa volatilidade (Regime {regime_atual}). Nenhuma intervenção necessária.")

        st.markdown("---")
        
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            st.subheader("📈 Evolução do Patrimônio Líquido (Cota)")
            fig_pl = go.Figure()
            fig_pl.add_trace(go.Scatter(
                x=pl_series.index, y=pl_series.values, 
                fill='tozeroy', name='PL Fundo', line=dict(color='#0078D7', width=2)
            ))
            fig_pl.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pl, use_container_width=True)
            
        with col_g2:
            st.subheader("🎯 Alocação Aplicada no Fundo")
            ativos_alocados = [ativo for ativo, peso in zip(ret_anuais.index, pesos) if peso > 0.001]
            pesos_alocados = [peso for peso in pesos if peso > 0.001]
            
            fig_pesos = go.Figure(data=[go.Pie(labels=ativos_alocados, values=pesos_alocados, hole=.4)])
            fig_pesos.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pesos, use_container_width=True)