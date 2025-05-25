import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob
from datetime import datetime, timedelta
import numpy as np
import re
from pathlib import Path
import uuid

# Configuração da página
st.set_page_config(
    page_title="💰 Dashboard Financeiro Avançado",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Tema principal */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric > label {
        color: #2c3e50 !important;
        font-weight: bold !important;
    }
    
    .warning-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def detect_column_mappings(df):
    """Detecta automaticamente as colunas do CSV baseado em padrões comuns"""
    column_mapping = {}
    
    # Detectar coluna de data
    date_patterns = ['data', 'date', 'dt', 'timestamp', 'time']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in date_patterns):
            column_mapping['Data'] = col
            break
    
    # Detectar coluna de valor
    value_patterns = ['valor', 'value', 'amount', 'montante', 'quantia']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in value_patterns):
            column_mapping['Valor'] = col
            break
    
    # Detectar coluna de descrição
    desc_patterns = ['descricao', 'descrição', 'description', 'memo', 'observacao', 'observação', 'historic']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in desc_patterns):
            column_mapping['Descrição'] = col
            break
    
    # Detectar coluna de categoria
    cat_patterns = ['categoria', 'category', 'tipo', 'class']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in cat_patterns):
            column_mapping['Categoria'] = col
            break
    
    # Detectar coluna de ID
    id_patterns = ['id', 'codigo', 'código', 'reference', 'ref']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in id_patterns):
            column_mapping['ID'] = col
            break
    
    return column_mapping

@st.cache_data
def load_csv_files():
    """Carrega todos os CSVs da pasta especificada"""
    csv_patterns = [
        "*.csv",
        "data/*.csv", 
        "data/raw/*.csv",
        "extratos/*.csv",
        "uploads/*.csv"
    ]
    
    all_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
    
    if not all_files:
        return pd.DataFrame(), []
    
    dfs = []
    loaded_files = []
    
    for file in all_files:
        try:
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            separators = [',', ';', '\t']
            df = None
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(file, encoding=encoding, sep=sep)
                        if len(df.columns) > 1:
                            break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError):
                        continue
                if df is not None and len(df.columns) > 1:
                    break
            
            if df is not None and len(df.columns) > 1:
                df['arquivo_origem'] = os.path.basename(file)
                dfs.append(df)
                loaded_files.append(file)
                
        except Exception as e:
            st.sidebar.error(f"❌ {os.path.basename(file)}: {str(e)}")
    
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df, loaded_files
    return pd.DataFrame(), []

def process_financial_data(df):
    """Processa e limpa os dados financeiros"""
    if df.empty:
        return df
    
    # Detectar mapeamento de colunas
    column_mapping = detect_column_mappings(df)
    
    # Aplicar mapeamento se necessário
    df_processed = df.copy()
    for standard_name, actual_name in column_mapping.items():
        if actual_name != standard_name and actual_name in df.columns:
            df_processed[standard_name] = df_processed[actual_name]
    
    # Verificar se temos as colunas essenciais
    essential_columns = ['Data', 'Valor']
    missing_columns = [col for col in essential_columns if col not in df_processed.columns]
    
    if missing_columns:
        st.error(f"⚠️ **Colunas essenciais não encontradas:** {', '.join(missing_columns)}")
        st.write("**Colunas disponíveis no seu CSV:**")
        st.write(list(df.columns))
        st.stop()
    
    # Processar coluna de data
    try:
        df_processed['Data'] = pd.to_datetime(df_processed['Data'], errors='coerce', dayfirst=True)
        df_processed = df_processed.dropna(subset=['Data'])
        
        # Criar colunas de tempo
        df_processed['Mes'] = df_processed['Data'].dt.to_period('M')
        df_processed['Mes_Str'] = df_processed['Data'].dt.strftime('%Y-%m')
        df_processed['Ano'] = df_processed['Data'].dt.year
        df_processed['Mes_Nome'] = df_processed['Data'].dt.strftime('%B')
        df_processed['Dia_Semana'] = df_processed['Data'].dt.strftime('%A')
        
    except Exception as e:
        st.error(f"❌ Erro ao processar datas: {e}")
        st.stop()
    
    # Processar valores
    try:
        if df_processed['Valor'].dtype == 'object':
            df_processed['Valor'] = df_processed['Valor'].astype(str)
            df_processed['Valor'] = df_processed['Valor'].str.replace(r'[R$\s]', '', regex=True)
            df_processed['Valor'] = df_processed['Valor'].str.replace(',', '.', regex=False)
        
        df_processed['Valor'] = pd.to_numeric(df_processed['Valor'], errors='coerce')
        df_processed = df_processed.dropna(subset=['Valor'])
        
        # Classificar receitas e despesas
        df_processed['Tipo'] = df_processed['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
        df_processed['Valor_Absoluto'] = df_processed['Valor'].abs()
        
    except Exception as e:
        st.error(f"❌ Erro ao processar valores: {e}")
        st.stop()
    
    # Limpar descrições
    if 'Descrição' not in df_processed.columns:
        if any(col for col in df.columns if 'desc' in col.lower()):
            desc_col = next(col for col in df.columns if 'desc' in col.lower())
            df_processed['Descrição'] = df_processed[desc_col]
        else:
            df_processed['Descrição'] = 'Sem descrição'
    
    df_processed['Descrição'] = df_processed['Descrição'].fillna('Sem descrição')
    df_processed['Descrição'] = df_processed['Descrição'].astype(str).str.strip()
    
    # Preencher categorias faltantes
    if 'Categoria' not in df_processed.columns:
        df_processed['Categoria'] = 'Outros'
    else:
        df_processed['Categoria'] = df_processed['Categoria'].fillna('Outros')
    
    # Identificar custos fixos automaticamente
    df_processed = identify_fixed_costs(df_processed)
    
    # Remover duplicatas se existir coluna ID
    if 'ID' in df_processed.columns:
        df_processed = df_processed.drop_duplicates(subset=['ID'], keep='first')
    
    return df_processed

def reprocess_as_nubank_data(df):
    """Reprocessa dados especificamente para extratos do Nubank (só despesas)"""
    if df.empty:
        return df
    
    df_nubank = df.copy()
    
    # No Nubank, tudo são despesas - converter valores para absoluto e marcar como despesa
    df_nubank['Valor_Absoluto'] = df_nubank['Valor'].abs()
    df_nubank['Tipo'] = 'Despesa'
    df_nubank['Valor'] = -df_nubank['Valor_Absoluto']  # Manter valores negativos para despesas
    
    # Melhorar a categorização automática baseada em descrições do Nubank
    df_nubank = improve_nubank_categorization(df_nubank)
    
    return df_nubank

def improve_nubank_categorization(df):
    """Melhora a categorização específica para dados do Nubank"""
    
    # Padrões mais específicos do Nubank
    nubank_patterns = {
        'Alimentação': [
            'RESTAURANTE', 'LANCHONETE', 'PADARIA', 'PIZZARIA', 'HAMBURGUER', 'SUBWAY',
            'MCDONALDS', 'BURGER KING', 'KFC', 'PIZZA', 'IFOOD', 'UBER EATS', 'RAPPI',
            'BAR ', 'CAFE', 'CAFETERIA', 'AÇOUGUE', 'SORVETERIA', 'PARRILLA'
        ],
        'Mercado': [
            'SUPERMERCADO', 'MERCADO', 'ATACADAO', 'CARREFOUR', 'EXTRA', 'WALMART',
            'BISTEK', 'ZAFFARI', 'COMERCIAL', 'MERCEARIA', 'HIPERMERCADO', 'BIG',
            'NACIONAL', 'ANGELONI', 'CONDOR'
        ],
        'Transporte': [
            'POSTO', 'COMBUSTIVEL', 'SHELL', 'PETROBRAS', 'IPIRANGA', 'BR DISTRIBUIDORA',
            'UBER', 'TAXI', '99', 'ONIBUS', 'METRO', 'ESTACIONAMENTO', 'PEDÁGIO',
            'AUTOPASS', 'SEM PARAR', 'OFICINA', 'MECANICA'
        ],
        'Saúde': [
            'FARMACIA', 'DROGARIA', 'PANVEL', 'DROGASIL', 'PACHECO', 'UNIMED',
            'MEDICO', 'HOSPITAL', 'CLINICA', 'LABORATORIO', 'DENTISTA', 'FISIOTERAPEUTA',
            'PAGUE MENOS', 'ULTRAFARMA'
        ],
        'Moradia': [
            'FERREIRA IMOVEIS', 'ALUGUEL', 'CONDOMINIO', 'IPTU', 'COPEL', 'CEMIG',
            'LIGHT', 'ELETROPAULO', 'SABESP', 'SANEPAR', 'COMGAS', 'CEG',
            'LUZ', 'ENERGIA', 'ÁGUA', 'AGUA', 'GAS', 'ESGOTO'
        ],
        'Telefone': [
            'CLARO', 'TIM', 'VIVO', 'OI', 'NET', 'SKY', 'TELEFONICA', 'NEXTEL',
            'TELEFONE', 'CELULAR', 'INTERNET', 'BANDA LARGA'
        ],
        'Educação': [
            'ESCOLA', 'UNIVERSIDADE', 'FACULDADE', 'COLEGIO', 'CURSO', 'MENSALIDADE',
            'LIVROS', 'MATERIAL ESCOLAR', 'PAPELARIA', 'XEROX'
        ],
        'Entretenimento': [
            'NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'DISNEY', 'GLOBOPLAY', 'YOUTUBE',
            'CINEMA', 'TEATRO', 'SHOW', 'INGRESSO', 'BALADA', 'CLUBE'
        ],
        'Compras': [
            'MAGAZINE', 'SHOPPING', 'LOJA', 'AMERICANAS', 'SUBMARINO', 'MERCADOLIVRE',
            'AMAZON', 'ALIEXPRESS', 'SHOPEE', 'RENNER', 'C&A', 'ZARA', 'H&M'
        ],
        'Serviços': [
            'BANCO', 'CAIXA', 'BRADESCO', 'ITAU', 'SANTANDER', 'NUBANK',
            'CARTORIO', 'DESPACHANTE', 'ADVOCACIA', 'CONTABILIDADE'
        ]
    }
    
    # Aplicar padrões específicos do Nubank
    for category, patterns in nubank_patterns.items():
        for pattern in patterns:
            mask = df['Descrição'].str.contains(pattern, case=False, na=False)
            df.loc[mask, 'Categoria'] = category
    
    return df

def identify_fixed_costs(df):
    """Identifica custos fixos vs variáveis"""
    df['Custo_Tipo'] = 'Variável'
    
    # Padrões conhecidos de custos fixos
    fixed_patterns = {
        'Moradia': ['FERREIRA IMOVEIS', 'ALUGUEL', 'CONDOMINIO', 'IPTU', 'LUZ', 'ENERGIA', 'ÁGUA', 'AGUA', 'GAS'],
        'Educação': ['ESCOLA', 'GREMIO NAUTICO', 'MENSALIDADE', 'UNIVERSIDADE', 'FACULDADE', 'CURSO'],
        'Telefone': ['CLARO', 'TIM SA', 'VIVO', 'OI', 'TELEFONE', 'CELULAR', 'INTERNET'],
        'Transferências para terceiros': ['COPE SERVICOS', 'CONTABIL', 'PIX PROGRAMADO'],
        'Saúde': ['PLANO DE SAUDE', 'UNIMED', 'BRADESCO SAUDE', 'PLANO SAUDE', 'CONVENIO'],
        'Transporte': ['SEGURO AUTO', 'IPVA', 'LICENCIAMENTO'],
        'Entretenimento': ['NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'DISNEY', 'GLOBOPLAY']
    }
    
    for categoria, patterns in fixed_patterns.items():
        for pattern in patterns:
            if 'Descrição' in df.columns:
                mask = df['Descrição'].str.contains(pattern, case=False, na=False)
                df.loc[mask, 'Custo_Tipo'] = 'Fixo'
                df.loc[mask & (df['Categoria'] == 'Outros'), 'Categoria'] = categoria
    
    # Identificar gastos recorrentes (aparecem em pelo menos 3 meses)
    if len(df) > 0 and 'Mes' in df.columns:
        despesas = df[df['Tipo'] == 'Despesa'].copy()
        if not despesas.empty and 'Descrição' in despesas.columns:
            freq_descriptions = despesas.groupby('Descrição')['Mes'].nunique()
            recurring_descriptions = freq_descriptions[freq_descriptions >= 3].index
            
            mask = df['Descrição'].isin(recurring_descriptions) & (df['Tipo'] == 'Despesa')
            df.loc[mask, 'Custo_Tipo'] = 'Fixo'
    
    return df

def create_monthly_analysis(df):
    """Cria análise mensal"""
    if df.empty:
        return pd.DataFrame()
    
    monthly_data = df.groupby(['Mes_Str', 'Tipo']).agg({
        'Valor_Absoluto': 'sum',
        'Data': 'count'
    }).reset_index()
    
    monthly_data.rename(columns={'Data': 'Quantidade'}, inplace=True)
    
    monthly_pivot = monthly_data.pivot(
        index='Mes_Str',
        columns='Tipo',
        values='Valor_Absoluto'
    ).fillna(0)
    
    monthly_pivot['Saldo'] = monthly_pivot.get('Receita', 0) - monthly_pivot.get('Despesa', 0)
    monthly_pivot['Taxa_Poupanca'] = (
        monthly_pivot['Saldo'] / monthly_pivot.get('Receita', 1) * 100
    ).replace([np.inf, -np.inf], 0)
    
    return monthly_pivot.reset_index()

def create_visualizations_nubank(df, monthly_analysis):
    """Cria visualizações específicas para dados do Nubank (só despesas)"""
    
    if monthly_analysis.empty or df.empty:
        return None, None, None, None, None
    
    # 1. Gráfico de despesas mensais (sem receitas)
    fig_monthly = go.Figure()
    
    if 'Despesa' in monthly_analysis.columns and monthly_analysis['Despesa'].sum() > 0:
        fig_monthly.add_trace(go.Bar(
            name='Despesas no Cartão',
            x=monthly_analysis['Mes_Str'],
            y=monthly_analysis['Despesa'],
            marker_color='#e74c3c',
            hovertemplate='<b>Despesas</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Adicionar linha de tendência
        if len(monthly_analysis) > 1:
            fig_monthly.add_trace(go.Scatter(
                name='Tendência',
                x=monthly_analysis['Mes_Str'],
                y=monthly_analysis['Despesa'].rolling(window=2).mean(),
                mode='lines',
                line=dict(color='#3498db', width=2, dash='dash'),
                hovertemplate='<b>Média Móvel</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ))
    
    fig_monthly.update_layout(
        title='💸 Evolução dos Gastos Mensais - Cartão Nubank',
        xaxis_title='Mês',
        yaxis_title='Valor (R$)',
        height=500,
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # 2. Gráfico de pizza por categoria
    despesas_df = df[df['Tipo'] == 'Despesa']
    fig_category = None
    
    if not despesas_df.empty:
        category_data = despesas_df.groupby('Categoria')['Valor_Absoluto'].sum().reset_index()
        category_data = category_data.sort_values('Valor_Absoluto', ascending=False)
        
        if len(category_data) > 0 and category_data['Valor_Absoluto'].sum() > 0:
            fig_category = px.pie(
                category_data, 
                values='Valor_Absoluto', 
                names='Categoria',
                title='🏷️ Distribuição de Gastos por Categoria - Cartão Nubank',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_category.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
            )
            fig_category.update_layout(
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
    
    # 3. Custos fixos vs variáveis
    fig_fixed_var = None
    if 'Custo_Tipo' in df.columns:
        fixed_var_data = df[df['Tipo'] == 'Despesa'].groupby(['Mes_Str', 'Custo_Tipo'])['Valor_Absoluto'].sum().reset_index()
        
        if not fixed_var_data.empty and len(fixed_var_data) > 0:
            fig_fixed_var = px.bar(
                fixed_var_data,
                x='Mes_Str',
                y='Valor_Absoluto',
                color='Custo_Tipo',
                title='💡 Custos Fixos vs Variáveis por Mês - Cartão Nubank',
                color_discrete_map={'Fixo': '#e74c3c', 'Variável': '#3498db'},
                labels={'Mes_Str': 'Mês', 'Valor_Absoluto': 'Valor (R$)'}
            )
            fig_fixed_var.update_layout(
                height=400,
                hovermode='x unified',
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
    
    # 4. Tendências por categoria (top 6)
    fig_trends = None
    if not despesas_df.empty:
        category_totals = despesas_df.groupby('Categoria')['Valor_Absoluto'].sum()
        top_categories = category_totals.nlargest(6).index
        
        trend_data = despesas_df[
            despesas_df['Categoria'].isin(top_categories)
        ].groupby(['Mes_Str', 'Categoria'])['Valor_Absoluto'].sum().reset_index()
        
        if not trend_data.empty and len(trend_data) > 0:
            fig_trends = px.line(
                trend_data,
                x='Mes_Str',
                y='Valor_Absoluto',
                color='Categoria',
                title='📈 Tendência dos Gastos por Categoria (Top 6) - Cartão Nubank',
                markers=True,
                labels={'Mes_Str': 'Mês', 'Valor_Absoluto': 'Valor (R$)'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_trends.update_layout(
                height=400,
                hovermode='x unified',
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
    
    # 5. Gauge de economia (baseado na diferença mês a mês)
    fig_gauge = None
    if len(monthly_analysis) >= 2:
        current_expense = monthly_analysis['Despesa'].iloc[-1] if 'Despesa' in monthly_analysis.columns else 0
        previous_expense = monthly_analysis['Despesa'].iloc[-2] if 'Despesa' in monthly_analysis.columns else 0
        
        if previous_expense > 0:
            economy_rate = ((previous_expense - current_expense) / previous_expense) * 100
        else:
            economy_rate = 0
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=economy_rate,
            delta={'reference': 0, 'valueformat': '.1f'},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Economia vs Mês Anterior (%)", 'font': {'size': 20}},
            number={'font': {'size': 40}},
            gauge={
                'axis': {'range': [-50, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#2ecc71" if economy_rate >= 0 else "#e74c3c"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-50, -10], 'color': "#ffebee"},
                    {'range': [-10, 10], 'color': "#fff3e0"},
                    {'range': [10, 50], 'color': "#e8f5e8"}
                ],
                'threshold': {
                    'line': {'color': "blue", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ))
        
        fig_gauge.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "darkblue", 'family': "Arial"}
        )
    
    return fig_monthly, fig_category, fig_fixed_var, fig_trends, fig_gauge

def create_financial_summary_cards_nubank(df, monthly_analysis):
    """Cria cards de resumo financeiro específico para Nubank (só despesas)"""
    if df.empty or monthly_analysis.empty:
        return
    
    # Calcular métricas do último mês (só despesas)
    latest_month = df['Mes_Str'].max()
    current_month_data = df[df['Mes_Str'] == latest_month]
    
    total_despesas = current_month_data['Valor_Absoluto'].sum()
    num_transacoes = len(current_month_data)
    gasto_medio_transacao = total_despesas / num_transacoes if num_transacoes > 0 else 0
    
    # Custos fixos do mês
    if 'Custo_Tipo' in current_month_data.columns:
        custos_fixos = current_month_data[current_month_data['Custo_Tipo'] == 'Fixo']['Valor_Absoluto'].sum()
        custos_variaveis = current_month_data[current_month_data['Custo_Tipo'] == 'Variável']['Valor_Absoluto'].sum()
    else:
        custos_fixos = 0
        custos_variaveis = total_despesas
    
    # Categoria que mais gastou
    if not current_month_data.empty:
        categoria_top = current_month_data.groupby('Categoria')['Valor_Absoluto'].sum().idxmax()
        valor_categoria_top = current_month_data.groupby('Categoria')['Valor_Absoluto'].sum().max()
    else:
        categoria_top = "N/A"
        valor_categoria_top = 0
    
    # Comparação com mês anterior
    months = sorted(df['Mes_Str'].unique())
    if len(months) >= 2:
        previous_month = months[-2]
        prev_month_data = df[df['Mes_Str'] == previous_month]
        prev_despesas = prev_month_data['Valor_Absoluto'].sum()
        delta_despesas = total_despesas - prev_despesas
        delta_despesas_pct = (delta_despesas / prev_despesas * 100) if prev_despesas > 0 else 0
    else:
        delta_despesas_pct = 0
    
    # Exibir métricas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💳 Total no Cartão",
            f"R$ {total_despesas:,.2f}",
            delta=f"{delta_despesas_pct:+.1f}%" if abs(delta_despesas_pct) > 0.1 else None,
            help=f"Total gasto no cartão Nubank em {latest_month}"
        )
    
    with col2:
        st.metric(
            "🔢 Transações",
            f"{num_transacoes}",
            help="Número total de compras no cartão"
        )
    
    with col3:
        st.metric(
            "📊 Gasto Médio",
            f"R$ {gasto_medio_transacao:.2f}",
            help="Valor médio por compra no cartão"
        )
    
    with col4:
        st.metric(
            "🔒 Custos Fixos",
            f"R$ {custos_fixos:,.2f}",
            delta=f"{(custos_fixos/total_despesas*100):.1f}%" if total_despesas > 0 else None,
            help="Gastos fixos pagos no cartão"
        )
    
    with col5:
        st.metric(
            f"🏆 {categoria_top}",
            f"R$ {valor_categoria_top:,.2f}",
            delta=f"{(valor_categoria_top/total_despesas*100):.1f}%" if total_despesas > 0 else None,
            help="Categoria com maior gasto no cartão"
        )

def show_expense_titles_analysis(df):
    """Mostra análise detalhada dos títulos/descrições das despesas"""
    st.subheader("🏪 Análise Detalhada dos Estabelecimentos - Cartão Nubank")
    
    if df.empty:
        st.info("Nenhum dado disponível para análise.")
        return
    
    # Estatísticas gerais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unique_descriptions = df['Descrição'].nunique()
        st.metric("🏪 Estabelecimentos Únicos", unique_descriptions)
    
    with col2:
        most_frequent = df['Descrição'].mode().iloc[0] if not df['Descrição'].mode().empty else "N/A"
        frequency = df['Descrição'].value_counts().iloc[0] if len(df) > 0 else 0
        st.metric("🔄 Mais Usado", f"{frequency}x", delta=most_frequent[:20] + "..." if len(most_frequent) > 20 else most_frequent)
    
    with col3:
        avg_per_establishment = df.groupby('Descrição')['Valor_Absoluto'].mean().mean()
        st.metric("💰 Gasto Médio por Local", f"R$ {avg_per_establishment:.2f}")
    
    # Análise por frequência
    st.markdown("#### 🔄 Estabelecimentos por Frequência de Uso do Cartão")
    
    frequency_analysis = df.groupby('Descrição').agg({
        'Valor_Absoluto': ['sum', 'mean', 'count'],
        'Data': ['min', 'max']
    }).round(2)
    
    frequency_analysis.columns = ['Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Compra', 'Ultima_Compra']
    frequency_analysis = frequency_analysis.sort_values('Frequencia', ascending=False)
    
    # Top 20 mais frequentes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🏆 Top 10 - Mais Usados no Cartão")
        top_frequent = frequency_analysis.head(10)
        
        for idx, (desc, row) in enumerate(top_frequent.iterrows(), 1):
            with st.expander(f"{idx}. {desc} ({int(row['Frequencia'])}x)"):
                st.write(f"💳 **Total no cartão:** R$ {row['Total_Gasto']:,.2f}")
                st.write(f"📊 **Gasto médio:** R$ {row['Gasto_Medio']:,.2f}")
                st.write(f"📅 **Primeira compra:** {row['Primeira_Compra'].strftime('%d/%m/%Y')}")
                st.write(f"📅 **Última compra:** {row['Ultima_Compra'].strftime('%d/%m/%Y')}")
                
                # Calcular frequência mensal
                dias_periodo = (row['Ultima_Compra'] - row['Primeira_Compra']).days
                if dias_periodo > 0:
                    freq_mensal = (row['Frequencia'] / dias_periodo) * 30
                    st.write(f"📈 **Frequência estimada:** {freq_mensal:.1f}x por mês")
    
    with col2:
        st.markdown("##### 💸 Top 10 - Maiores Gastos no Cartão")
        top_expensive = frequency_analysis.sort_values('Total_Gasto', ascending=False).head(10)
        
        for idx, (desc, row) in enumerate(top_expensive.iterrows(), 1):
            with st.expander(f"{idx}. {desc} (R$ {row['Total_Gasto']:,.2f})"):
                st.write(f"🔄 **Usado:** {int(row['Frequencia'])}x no cartão")
                st.write(f"📊 **Gasto médio:** R$ {row['Gasto_Medio']:,.2f}")
                st.write(f"📅 **Primeira compra:** {row['Primeira_Compra'].strftime('%d/%m/%Y')}")
                st.write(f"📅 **Última compra:** {row['Ultima_Compra'].strftime('%d/%m/%Y')}")
                
                # Percentual do total
                total_geral = df['Valor_Absoluto'].sum()
                percentual = (row['Total_Gasto'] / total_geral) * 100
                st.write(f"📊 **Representa:** {percentual:.1f}% do total gasto no cartão")
    
    # Busca por estabelecimento
    st.markdown("#### 🔍 Buscar Estabelecimento Específico")
    search_term = st.text_input("Digite o nome do estabelecimento:", placeholder="Ex: SUPERMERCADO, POSTO, RESTAURANTE")
    
    if search_term:
        filtered_descriptions = df[df['Descrição'].str.contains(search_term, case=False, na=False)]
        
        if not filtered_descriptions.empty:
            search_results = filtered_descriptions.groupby('Descrição').agg({
                'Valor_Absoluto': ['sum', 'mean', 'count'],
                'Data': ['min', 'max']
            }).round(2)
            
            search_results.columns = ['Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Compra', 'Ultima_Compra']
            search_results = search_results.sort_values('Total_Gasto', ascending=False)
            
            st.write(f"🎯 **Encontrados {len(search_results)} estabelecimentos com '{search_term}'**")
            
            for desc, row in search_results.iterrows():
                st.write(f"**{desc}**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💳 Total", f"R$ {row['Total_Gasto']:,.2f}")
                with col2:
                    st.metric("📊 Média", f"R$ {row['Gasto_Medio']:,.2f}")
                with col3:
                    st.metric("🔄 Vezes", f"{int(row['Frequencia'])}")
                with col4:
                    st.metric("📅 Período", f"{row['Primeira_Compra'].strftime('%m/%Y')} - {row['Ultima_Compra'].strftime('%m/%Y')}")
                st.markdown("---")
        else:
            st.info(f"Nenhum estabelecimento encontrado com '{search_term}' nos seus gastos do cartão")
    
    # Lista completa com filtros
    st.markdown("#### 📋 Lista Completa de Estabelecimentos")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_option = st.selectbox("Ordenar por:", 
            ['Frequência (maior)', 'Frequência (menor)', 'Total gasto (maior)', 'Total gasto (menor)', 'Alfabética'])
    with col2:
        min_frequency = st.number_input("Frequência mínima:", min_value=1, value=1)
    with col3:
        show_count = st.selectbox("Mostrar:", [20, 50, 100, "Todos"])
    
    # Aplicar filtros e ordenação
    filtered_data = frequency_analysis[frequency_analysis['Frequencia'] >= min_frequency]
    
    if sort_option == 'Frequência (maior)':
        filtered_data = filtered_data.sort_values('Frequencia', ascending=False)
    elif sort_option == 'Frequência (menor)':
        filtered_data = filtered_data.sort_values('Frequencia', ascending=True)
    elif sort_option == 'Total gasto (maior)':
        filtered_data = filtered_data.sort_values('Total_Gasto', ascending=False)
    elif sort_option == 'Total gasto (menor)':
        filtered_data = filtered_data.sort_values('Total_Gasto', ascending=True)
    elif sort_option == 'Alfabética':
        filtered_data = filtered_data.sort_index()
    
    if show_count != "Todos":
        filtered_data = filtered_data.head(show_count)
    
    # Exibir tabela formatada
    st.dataframe(
        filtered_data.style.format({
            'Total_Gasto': 'R$ {:.2f}',
            'Gasto_Medio': 'R$ {:.2f}',
            'Frequencia': '{:.0f}',
            'Primeira_Compra': lambda x: x.strftime('%d/%m/%Y'),
            'Ultima_Compra': lambda x: x.strftime('%d/%m/%Y')
        }),
        use_container_width=True,
        height=400
    )

def main():
    """Função principal do dashboard"""
    
    # DEFINIR PROCESSING_MODE LOGO NO INÍCIO
    processing_mode = st.sidebar.selectbox(
        "📱 Tipo de Extrato",
        options=["Nubank (Só Despesas)", "Banco Tradicional (Receitas + Despesas)"],
        help="Nubank: trata tudo como despesa\nBanco Tradicional: usa sinais +/- para classificar"
    )
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>💰 Dashboard Financeiro Avançado</h1>
        <p>Análise Completa e Inteligente dos seus Gastos Pessoais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Alerta sobre o modo ativo
    if processing_mode == "Nubank (Só Despesas)":
        st.markdown("""
        <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
        <h4>💳 Modo Cartão Nubank Ativo</h4>
        <p><strong>Todas as transações estão sendo tratadas como DESPESAS do cartão</strong>, pois no extrato do cartão Nubank só aparecem os <strong>gastos/compras</strong> que você fez, nunca receitas.</p>
        <ul>
            <li>🏪 <strong>Análise de estabelecimentos</strong> - Onde você mais usa o cartão</li>
            <li>🔄 <strong>Frequência de compras</strong> - Quantas vezes comprou em cada lugar</li>
            <li>💡 <strong>Categorização inteligente</strong> - Baseada em padrões do Nubank</li>
            <li>📊 <strong>Gauge de economia</strong> - Comparação com mês anterior</li>
        </ul>
        <p><em>Para analisar conta corrente completa (receitas + despesas), mude para 'Banco Tradicional'.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar para configurações
    st.sidebar.title("⚙️ Configurações")
    st.sidebar.markdown("### 📁 Status dos Arquivos")
    
    # Carregar dados
    with st.spinner("🔄 Carregando dados..."):
        df, loaded_files = load_csv_files()
    
    if df.empty:
        st.error("⚠️ **Nenhum dado encontrado!**")
        
        st.markdown("""
        <div class="warning-box">
        <h4>📋 Como adicionar dados do seu cartão Nubank:</h4>
        <ol>
        <li><strong>Baixe o extrato do cartão no app/site do Nubank</strong></li>
        <li><strong>Salve o arquivo CSV em uma das pastas:</strong></li>
        <ul>
            <li>Pasta atual (raiz do projeto)</li>
            <li><code>data/raw/</code></li>
            <li><code>extratos/</code></li>
            <li><code>uploads/</code></li>
        </ul>
        <li><strong>Atualize a página (F5)</strong></li>
        </ol>
        
        <h4>📄 Formato do extrato Nubank:</h4>
        <ul>
            <li><strong>Todas as linhas são gastos</strong> (compras no cartão)</li>
            <li><strong>Colunas esperadas:</strong> Data, Valor, Descrição</li>
            <li><strong>Não há receitas</strong> no extrato do cartão</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload de arquivo
        st.markdown("### 📤 Upload de Extrato do Cartão")
        uploaded_file = st.file_uploader("Escolha o arquivo CSV do Nubank", type="csv")
        
        if uploaded_file is not None:
            try:
                upload_dir = "uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                st.success(f"✅ Extrato {uploaded_file.name} carregado com sucesso!")
                st.info("🔄 Atualize a página para processar o arquivo.")
                
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivo: {e}")
        
        return
    
    # Processar dados
    with st.spinner("🔧 Processando dados do cartão..."):
        try:
            df = process_financial_data(df)
            
            # Aplicar modo específico se for Nubank
            if processing_mode == "Nubank (Só Despesas)":
                df = reprocess_as_nubank_data(df)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar dados: {e}")
            st.write("**Detalhes do erro:**")
            st.exception(e)
            return
    
    if df.empty:
        st.error("❌ Erro ao processar os dados ou dados inválidos!")
        return
    
    # Informações na sidebar
    st.sidebar.success(f"✅ **{len(df):,}** transações carregadas")
    st.sidebar.info(f"📅 **Período:** {df['Data'].min().date()} até {df['Data'].max().date()}")
    st.sidebar.info(f"📁 **Arquivos:** {len(loaded_files)}")
    
    # Informações sobre o modo selecionado
    if processing_mode == "Nubank (Só Despesas)":
        st.sidebar.markdown("""
        <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
        <h4>💳 Modo Cartão Nubank</h4>
        <p><strong>Características:</strong></p>
        <ul>
            <li>✅ Todas as transações = despesas do cartão</li>
            <li>✅ Análise de estabelecimentos</li>
            <li>✅ Frequência de uso por local</li>
            <li>✅ Gauge de economia mensal</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Análise mensal
    monthly_analysis = create_monthly_analysis(df)
    
    # Filtros na sidebar
    st.sidebar.markdown("### 🔍 Filtros")
    
    # Filtro de período
    min_date = df['Data'].min().date()
    max_date = df['Data'].max().date()
    
    date_range = st.sidebar.date_input(
        "📅 Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de categorias
    categories = ['Todas'] + sorted(df['Categoria'].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "🏷️ Categorias",
        options=categories,
        default=['Todas']
    )
    
    # Filtro de valor mínimo
    min_value = st.sidebar.number_input(
        "💰 Valor mínimo (R$)",
        min_value=0.0,
        value=0.0,
        step=10.0
    )
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    # Filtro de data
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Data'].dt.date >= start_date) &
            (filtered_df['Data'].dt.date <= end_date)
        ]
    
    # Filtro de categoria
    if 'Todas' not in selected_categories and selected_categories:
        filtered_df = filtered_df[filtered_df['Categoria'].isin(selected_categories)]
    
    # Filtro de valor mínimo
    if min_value > 0:
        filtered_df = filtered_df[filtered_df['Valor_Absoluto'] >= min_value]
    
    # Recalcular análise mensal com dados filtrados
    monthly_analysis_filtered = create_monthly_analysis(filtered_df)
    
    # Cards de resumo financeiro
    if not filtered_df.empty and not monthly_analysis_filtered.empty:
        create_financial_summary_cards_nubank(filtered_df, monthly_analysis_filtered)
    
    st.markdown("---")
    
    # Criar visualizações
    if not monthly_analysis_filtered.empty:
        try:
            fig_monthly, fig_category, fig_fixed_var, fig_trends, fig_gauge = create_visualizations_nubank(filtered_df, monthly_analysis_filtered)
        except Exception as e:
            st.error(f"❌ Erro ao criar visualizações: {e}")
            fig_monthly = fig_category = fig_fixed_var = fig_trends = fig_gauge = None
        
        # Tabs específicas para Nubank
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Visão Geral", 
            "💡 Custos Fixos vs Variáveis", 
            "📈 Tendências", 
            "🏪 Estabelecimentos",  # Aba específica para análise de onde gasta
            "📋 Dados Brutos",
            "📊 Relatórios"
        ])
        
        # Tab 1 - Visão Geral
        with tab1:
            if fig_monthly is not None and fig_gauge is not None:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_chart")
                
                with col2:
                    st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_chart")
            elif fig_monthly is not None:
                st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_chart_only")
            
            # Gráfico de pizza
            if fig_category is not None:
                st.plotly_chart(fig_category, use_container_width=True, key="category_pie_chart")
        
        # Tab 2 - Custos Fixos vs Variáveis
        with tab2:
            if fig_fixed_var is not None:
                st.plotly_chart(fig_fixed_var, use_container_width=True, key="fixed_var_chart")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔒 Custos Fixos Pagos no Cartão")
                    if 'Custo_Tipo' in filtered_df.columns:
                        fixed_expenses = filtered_df[
                            filtered_df['Custo_Tipo'] == 'Fixo'
                        ].groupby('Descrição')['Valor_Absoluto'].mean().sort_values(ascending=False).head(10)
                        
                        if not fixed_expenses.empty:
                            st.dataframe(
                                fixed_expenses.to_frame('Valor Médio').style.format({'Valor Médio': 'R$ {:.2f}'}),
                                use_container_width=True
                            )
                        else:
                            st.info("Nenhum custo fixo identificado no cartão")
                
                with col2:
                    st.subheader("📊 Distribuição dos Gastos")
                    if 'Custo_Tipo' in filtered_df.columns:
                        summary = filtered_df.groupby('Custo_Tipo')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
                        summary.columns = ['Total', 'Média', 'Quantidade']
                        st.dataframe(
                            summary.style.format({
                                'Total': 'R$ {:.2f}',
                                'Média': 'R$ {:.2f}',
                                'Quantidade': '{:.0f}'
                            }),
                            use_container_width=True
                        )
            else:
                st.info("💡 Análise de custos fixos vs variáveis não disponível para este período")
        
        # Tab 3 - Tendências
        with tab3:
            if fig_trends is not None:
                st.plotly_chart(fig_trends, use_container_width=True, key="trends_chart")
            
            # Top gastos no cartão
            st.subheader("🔝 Maiores Gastos no Cartão do Período")
            top_expenses = filtered_df.nlargest(15, 'Valor_Absoluto')
            
            if not top_expenses.empty:
                display_cols = ['Data', 'Descrição', 'Categoria', 'Valor_Absoluto']
                if 'Custo_Tipo' in top_expenses.columns:
                    display_cols.append('Custo_Tipo')
                
                st.dataframe(
                    top_expenses[display_cols].style.format({
                        'Data': lambda x: x.strftime('%d/%m/%Y'),
                        'Valor_Absoluto': 'R$ {:.2f}'
                    }),
                    use_container_width=True
                )
        
        # Tab 4 - Estabelecimentos (específica do Nubank)
        with tab4:
            show_expense_titles_analysis(filtered_df)
        
        # Tab 5 - Dados Brutos
        with tab5:
            st.subheader("📋 Dados Completos do Cartão Nubank")
            
            # Opções de visualização
            col1, col2, col3 = st.columns(3)
            with col1:
                show_all = st.checkbox("Mostrar todos os dados", value=False)
            with col2:
                rows_to_show = st.selectbox("Linhas para mostrar", [50, 100, 200, 500], index=0)
            with col3:
                sort_by = st.selectbox("Ordenar por", ['Data', 'Valor_Absoluto', 'Categoria'])
            
            # Preparar dados para exibição
            display_df = filtered_df.copy()
            
            if not show_all:
                display_df = display_df.head(rows_to_show)
            
            # Ordenar
            if sort_by == 'Data':
                display_df = display_df.sort_values('Data', ascending=False)
            elif sort_by == 'Valor_Absoluto':
                display_df = display_df.sort_values('Valor_Absoluto', ascending=False)
            else:
                display_df = display_df.sort_values(sort_by)
            
            # Exibir
            cols_to_show = ['Data', 'Descrição', 'Categoria', 'Valor_Absoluto']
            if 'Custo_Tipo' in display_df.columns:
                cols_to_show.append('Custo_Tipo')
            
            st.dataframe(
                display_df[cols_to_show].style.format({
                    'Data': lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '',
                    'Valor_Absoluto': 'R$ {:.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Botão de download
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados do cartão (CSV)",
                data=csv,
                file_name=f"gastos_cartao_nubank_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Tab 6 - Relatórios
        with tab6:
            st.subheader("📊 Relatórios do Cartão Nubank")
            
            report_type = st.selectbox(
                "Tipo de Relatório",
                ["Mensal Detalhado", "Por Categoria", "Estabelecimentos Frequentes", "Custos Fixos"]
            )
            
            if st.button("📄 Gerar Relatório"):
                if report_type == "Mensal Detalhado":
                    st.write("### 📊 Relatório Mensal - Cartão Nubank")
                    
                    for _, row in monthly_analysis_filtered.iterrows():
                        st.write(f"**Mês: {row['Mes_Str']}**")
                        st.write(f"- Total gasto no cartão: R$ {row.get('Despesa', 0):,.2f}")
                        
                        # Calcular número de transações no mês
                        month_transactions = filtered_df[filtered_df['Mes_Str'] == row['Mes_Str']]
                        st.write(f"- Compras realizadas: {len(month_transactions)}")
                        if len(month_transactions) > 0:
                            st.write(f"- Gasto médio por compra: R$ {row.get('Despesa', 0)/len(month_transactions):,.2f}")
                        st.write("---")
                
                elif report_type == "Estabelecimentos Frequentes":
                    st.write("### 🏪 Relatório de Estabelecimentos - Cartão Nubank")
                    
                    establishment_report = filtered_df.groupby('Descrição').agg({
                        'Valor_Absoluto': ['sum', 'mean', 'count'],
                        'Data': ['min', 'max']
                    }).round(2)
                    
                    establishment_report.columns = ['Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Compra', 'Ultima_Compra']
                    establishment_report = establishment_report.sort_values('Frequencia', ascending=False).head(20)
                    
                    for desc, row in establishment_report.iterrows():
                        st.write(f"**{desc}**")
                        st.write(f"- Compras no cartão: {int(row['Frequencia'])} vezes")
                        st.write(f"- Total gasto: R$ {row['Total_Gasto']:,.2f}")
                        st.write(f"- Gasto médio por compra: R$ {row['Gasto_Medio']:,.2f}")
                        st.write(f"- Primeira compra: {row['Primeira_Compra'].strftime('%d/%m/%Y')}")
                        st.write(f"- Última compra: {row['Ultima_Compra'].strftime('%d/%m/%Y')}")
                        st.write("---")
                
                elif report_type == "Por Categoria":
                    st.write("### 🏷️ Relatório por Categoria - Cartão Nubank")
                    
                    category_report = filtered_df.groupby('Categoria').agg({
                        'Valor_Absoluto': ['sum', 'mean', 'count'],
                        'Data': ['min', 'max']
                    }).round(2)
                    
                    for categoria in category_report.index:
                        st.write(f"**{categoria}**")
                        st.write(f"- Total no cartão: R$ {category_report.loc[categoria, ('Valor_Absoluto', 'sum')]:,.2f}")
                        st.write(f"- Gasto médio: R$ {category_report.loc[categoria, ('Valor_Absoluto', 'mean')]:,.2f}")
                        st.write(f"- Número de compras: {category_report.loc[categoria, ('Valor_Absoluto', 'count')]:.0f}")
                        st.write("---")
                
                # Botão para exportar relatório
                st.download_button(
                    label="📥 Baixar Relatório (TXT)",
                    data=f"Relatório {report_type} - Cartão Nubank\nGerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    file_name=f"relatorio_cartao_nubank_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
    
    else:
        st.warning("⚠️ Não foi possível gerar as visualizações. Verifique se há dados suficientes.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <h3>💳 Dashboard Cartão Nubank</h3>
        <p>Análise especializada para extratos do cartão Nubank | 🔒 Dados processados localmente</p>
        <p>Versão 3.0 - Otimizada para cartão de crédito/débito</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()