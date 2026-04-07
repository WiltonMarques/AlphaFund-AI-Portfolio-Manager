# 🏛️ AlphaFund: AI Portfolio Manager & Institutional Backoffice

Um sistema quantitativo completo de gestão de portfólios que simula a infraestrutura de uma *Asset Management* institucional. O AlphaFund integra Inteligência Artificial para leitura de risco macroeconômico, otimização matemática de ativos e um motor de *Backoffice* contábil alinhado às normas do COSIF/CVM.

O objetivo do projeto é demonstrar a fusão entre **Engenharia Financeira**, **Machine Learning** e **Compliance Contábil**, indo muito além da simples previsão de preços para entregar uma governança de dados ponta a ponta.

## 🚀 Arquitetura e Funcionalidade dos Scripts

O ecossistema é dividido em 5 módulos complementares:

* **`ingestao_dados.py` (Data Engineering):**
  Responsável pela extração automatizada de dados históricos da B3 e mercados globais via API (`yfinance`). Realiza o tratamento de dados faltantes (feriados), o cálculo de retornos logarítmicos diários e a geração da Matriz de Covariância anualizada.

* **`otimizador_markowitz.py` (Quantitative Finance):**
  O motor matemático da carteira. Utiliza o solver `SLSQP` do `scipy.optimize` para aplicar a Teoria Moderna do Portfólio (Harry Markowitz), testando milhares de combinações para encontrar a Fronteira Eficiente e sugerir a alocação de ativos que maximiza o Índice Sharpe (Maior Retorno por Unidade de Risco).

* **`detector_regimes.py` (Machine Learning):**
  A camada de Inteligência Artificial não-supervisionada. Utiliza o algoritmo **K-Means** (com `scikit-learn`) para agrupar o comportamento do mercado em "Regimes" baseados em retorno móvel e volatilidade. Ele detecta silenciosamente se o mercado está em um *Bull Market* (Crescimento) ou *Bear Market* (Crise de Liquidez).

* **`contabilidade_fundo.py` (Institutional Backoffice):**
  O diferencial corporativo do sistema. Simula a vida de um fundo de investimento multimercado:
  * Realiza a Marcação a Mercado (MTM) diária do portfólio.
  * Calcula a evolução do Patrimônio Líquido (PL) e o Valor da Cota.
  * Realiza o provisionamento matemático contínuo (base 252 dias) da Taxa de Administração e Taxa de Performance (utilizando o CDI como *Hurdle Rate*).
  * Gera o Balancete Patrimonial e a DRE sintética espelhados no plano de contas regulatório do Banco Central (COSIF).

* **`dashboard_alphafund.py` (Governança e Interface):**
  O painel executivo construído em `Streamlit` e `Plotly`. Integra todos os módulos anteriores em uma interface de tempo real. Possui um sistema de alertas de risco baseado na leitura da IA e o **Protocolo de Defesa (Management Overlay)** — um botão de intervenção humana que zera a exposição em Renda Variável durante crises, transferindo o capital para Renda Fixa e gerando automaticamente a *Boleta de Remanejamento* (Relatório de Giro de Risco) para auditoria.

## 🛠️ Stack Tecnológico
* **Linguagem:** Python
* **Data Science & ML:** Pandas, NumPy, Scikit-Learn
* **Otimização Matemática:** SciPy
* **Dataviz & Interface:** Streamlit, Plotly
  
https://github.com/WiltonMarques/AlphaFund-AI-Portfolio-Manager
  
![dashboard_alphafund_v1](https://github.com/user-attachments/assets/1f2555c9-54ad-48b0-852f-8137ba46976e)
![dashboard_alphafund_v2](https://github.com/user-attachments/assets/d2cbe547-a3bd-49ac-b0d3-3f45365a4f72)
