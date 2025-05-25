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

# Carregar CSS personalizado
try:
    with open('css/dashboard_styles.css', 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    # CSS básico inline se arquivo não existir
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .nubank-mode-indicator {
        background: #f8f9fa;
        border: 2px solid #8b2fff;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    
    @media (prefers-color-scheme: dark) {
        .nubank-mode-indicator {
            background: #1c2128;
            color: #f0f6fc;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def detect_nubank_format(df):
    """Detecta se o CSV é do formato Nubank (date, title, amount)"""
    nubank_columns = ['date', 'title', 'amount']
    return all(col in df.columns for col in nubank_columns)

def detect_column_mappings(df):
    """Detecta automaticamente as colunas do CSV baseado em padrões comuns"""
    column_mapping = {}
    
    # Se é formato Nubank, mapear diretamente
    if detect_nubank_format(df):
        return {
            'Data': 'date',
            'Descrição': 'title', 
            'Valor': 'amount'
        }
    
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
    desc_patterns = ['descricao', 'descrição', 'description', 'memo', 'observacao', 'observação', 'historic', 'title']
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
    """Carrega todos os CSVs da pasta especificada, com prioridade para arquivos Nubank"""
    csv_patterns = [
        "Nubank_*.csv",  # Prioritário: arquivos Nubank
        "*.csv",
        "data/*.csv", 
        "data/raw/*.csv",
        "extratos/*.csv",
        "uploads/*.csv"
    ]
    
    all_files = []
    nubank_files = []
    
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
        # Identificar arquivos Nubank
        if "Nubank_" in pattern:
            nubank_files.extend(files)
    
    # Remover duplicatas mantendo ordem
    all_files = list(dict.fromkeys(all_files))
    
    if not all_files:
        return pd.DataFrame(), [], False
    
    dfs = []
    loaded_files = []
    is_nubank_data = len(nubank_files) > 0
    
    # Priorizar arquivos Nubank se existirem
    files_to_process = nubank_files if nubank_files else all_files
    
    for file in files_to_process:
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
        return combined_df, loaded_files, is_nubank_data
    return pd.DataFrame(), [], False

def process_financial_data(df, is_nubank_data=False):
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
        
        # Mostrar primeiras linhas para debug
        st.write("**Primeiras linhas do arquivo:**")
        st.dataframe(df.head(3))
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
        
        # Para dados Nubank, tratar diferentemente
        if is_nubank_data:
            # No Nubank, valores negativos são despesas, positivos são receitas/estornos
            df_processed['Tipo'] = df_processed['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
            df_processed['Valor_Absoluto'] = df_processed['Valor'].abs()
        else:
            # Dados bancários tradicionais
            df_processed['Tipo'] = df_processed['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
            df_processed['Valor_Absoluto'] = df_processed['Valor'].abs()
        
    except Exception as e:
        st.error(f"❌ Erro ao processar valores: {e}")
        st.stop()
    
    # Limpar descrições
    if 'Descrição' not in df_processed.columns:
        if any(col for col in df.columns if 'desc' in col.lower() or 'title' in col.lower()):
            desc_col = next(col for col in df.columns if 'desc' in col.lower() or 'title' in col.lower())
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
    
    # Melhorar categorização para dados Nubank
    if is_nubank_data:
        df_processed = improve_nubank_categorization(df_processed)
    
    # Remover duplicatas se existir coluna ID
    if 'ID' in df_processed.columns:
        df_processed = df_processed.drop_duplicates(subset=['ID'], keep='first')
    
    return df_processed

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
            'PAGUE MENOS', 'ULTRAFARMA', 'Drogaria', 'DROGARIA SAO PAULO'
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
            'LIVROS', 'MATERIAL ESCOLAR', 'PAPELARIA', 'XEROX', 'ALDEIAS INFAN', 'Aldeias'
        ],
        'Entretenimento': [
            'NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'DISNEY', 'GLOBOPLAY', 'YOUTUBE',
            'CINEMA', 'TEATRO', 'SHOW', 'INGRESSO', 'BALADA', 'CLUBE', 'Google'
        ],
        'Compras': [
            'MAGAZINE', 'SHOPPING', 'LOJA', 'AMERICANAS', 'SUBMARINO', 'MERCADOLIVRE',
            'AMAZON', 'ALIEXPRESS', 'SHOPEE', 'RENNER', 'C&A', 'ZARA', 'H&M'
        ],
        'Investimento': [
            'Tesouro Nacional', 'TESOURO', 'INVESTIMENTO', 'APLICACAO', 'RENDA FIXA'
        ],
        'Transferências para terceiros': [
            'PIX', 'TRANSFERENCIA', 'TED', 'DOC', 'Fatima Cristina', 'Sirlei da Silva'
        ],
        'Receitas': [
            'CHESSFLIX', 'TREINAMENTOS', 'SALARIO', 'FREELANCE', 'RENDA', 'RECEITA'
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
        'Educação': ['ESCOLA', 'GREMIO NAUTICO', 'MENSALIDADE', 'UNIVERSIDADE', 'FACULDADE', 'CURSO', 'ALDEIAS'],
        'Telefone': ['CLARO', 'TIM SA', 'VIVO', 'OI', 'TELEFONE', 'CELULAR', 'INTERNET'],
        'Transferências para terceiros': ['COPE SERVICOS', 'CONTABIL', 'PIX PROGRAMADO'],
        'Saúde': ['PLANO DE SAUDE', 'UNIMED', 'BRADESCO SAUDE', 'PLANO SAUDE', 'CONVENIO'],
        'Transporte': ['SEGURO AUTO', 'IPVA', 'LICENCIAMENTO'],
        'Entretenimento': ['NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'DISNEY', 'GLOBOPLAY', 'Google']
    }
    
    for categoria, patterns in fixed_patterns.items():
        for pattern in patterns:
            if 'Descrição' in df.columns:
                mask = df['Descrição'].str.contains(pattern, case=False, na=False)
                df.loc[mask, 'Custo_Tipo'] = 'Fixo'
                df.loc[mask & (df['Categoria'] == 'Outros'), 'Categoria'] = categoria
    
    # Identificar gastos recorrentes (aparecem em pelo menos 3 períodos)
    if len(df) > 0 and 'Mes' in df.columns:
        despesas = df[df['Tipo'] == 'Despesa'].copy()
        if not despesas.empty and 'Descrição' in despesas.columns:
            freq_descriptions = despesas.groupby('Descrição')['Mes'].nunique()
            recurring_descriptions = freq_descriptions[freq_descriptions >= 2].index
            
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

def create_visualizations_nubank(df, monthly_analysis, is_nubank_data=False):
    """Cria visualizações específicas para dados do Nubank ou bancários tradicionais"""
    
    if monthly_analysis.empty or df.empty:
        return None, None, None, None, None
    
    # 1. Gráfico de evolução mensal
    fig_monthly = go.Figure()
    
    if is_nubank_data:
        # Para Nubank, focar em despesas com receitas ocasionais
        if 'Despesa' in monthly_analysis.columns:
            fig_monthly.add_trace(go.Bar(
                name='Despesas no Cartão',
                x=monthly_analysis['Mes_Str'],
                y=monthly_analysis['Despesa'],
                marker_color='#e74c3c',
                hovertemplate='<b>Despesas</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ))
        
        if 'Receita' in monthly_analysis.columns and monthly_analysis['Receita'].sum() > 0:
            fig_monthly.add_trace(go.Bar(
                name='Receitas/Estornos',
                x=monthly_analysis['Mes_Str'],
                y=monthly_analysis['Receita'],
                marker_color='#27ae60',
                hovertemplate='<b>Receitas</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ))
        
        title = '💸 Evolução Financeira - Dados Nubank'
    else:
        # Para dados bancários tradicionais
        if 'Receita' in monthly_analysis.columns:
            fig_monthly.add_trace(go.Bar(
                name='Receitas',
                x=monthly_analysis['Mes_Str'],
                y=monthly_analysis['Receita'],
                marker_color='#27ae60',
                hovertemplate='<b>Receitas</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ))
        
        if 'Despesa' in monthly_analysis.columns:
            fig_monthly.add_trace(go.Bar(
                name='Despesas',
                x=monthly_analysis['Mes_Str'],
                y=monthly_analysis['Despesa'],
                marker_color='#e74c3c',
                hovertemplate='<b>Despesas</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ))
        
        title = '💰 Evolução de Receitas vs Despesas'
    
    # Adicionar linha de tendência
    if len(monthly_analysis) > 1 and 'Despesa' in monthly_analysis.columns:
        fig_monthly.add_trace(go.Scatter(
            name='Tendência',
            x=monthly_analysis['Mes_Str'],
            y=monthly_analysis['Despesa'].rolling(window=2).mean(),
            mode='lines',
            line=dict(color='#3498db', width=2, dash='dash'),
            hovertemplate='<b>Média Móvel</b><br>Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
        ))
    
    fig_monthly.update_layout(
        title=title,
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
            title_cat = '🏷️ Distribuição de Gastos por Categoria - Nubank' if is_nubank_data else '🏷️ Distribuição de Despesas por Categoria'
            
            fig_category = px.pie(
                category_data, 
                values='Valor_Absoluto', 
                names='Categoria',
                title=title_cat,
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
            title_fixed = '💡 Custos Fixos vs Variáveis - Nubank' if is_nubank_data else '💡 Custos Fixos vs Variáveis'
            
            fig_fixed_var = px.bar(
                fixed_var_data,
                x='Mes_Str',
                y='Valor_Absoluto',
                color='Custo_Tipo',
                title=title_fixed,
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
            title_trends = '📈 Tendência dos Gastos por Categoria (Top 6) - Nubank' if is_nubank_data else '📈 Tendência das Despesas por Categoria (Top 6)'
            
            fig_trends = px.line(
                trend_data,
                x='Mes_Str',
                y='Valor_Absoluto',
                color='Categoria',
                title=title_trends,
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
    
    # 5. Gauge de economia/controle
    fig_gauge = None
    if len(monthly_analysis) >= 2:
        current_expense = monthly_analysis['Despesa'].iloc[-1] if 'Despesa' in monthly_analysis.columns else 0
        previous_expense = monthly_analysis['Despesa'].iloc[-2] if 'Despesa' in monthly_analysis.columns else 0
        
        if previous_expense > 0:
            economy_rate = ((previous_expense - current_expense) / previous_expense) * 100
        else:
            economy_rate = 0
        
        gauge_title = "Controle vs Mês Anterior (%)" if is_nubank_data else "Economia vs Mês Anterior (%)"
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=economy_rate,
            delta={'reference': 0, 'valueformat': '.1f'},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': gauge_title, 'font': {'size': 20}},
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

def create_financial_summary_cards(df, monthly_analysis, is_nubank_data=False):
    """Cria cards de resumo financeiro"""
    if df.empty or monthly_analysis.empty:
        return
    
    # Calcular métricas do último mês
    latest_month = df['Mes_Str'].max()
    current_month_data = df[df['Mes_Str'] == latest_month]
    
    total_despesas = current_month_data[current_month_data['Tipo'] == 'Despesa']['Valor_Absoluto'].sum()
    total_receitas = current_month_data[current_month_data['Tipo'] == 'Receita']['Valor_Absoluto'].sum()
    num_transacoes = len(current_month_data)
    gasto_medio_transacao = total_despesas / len(current_month_data[current_month_data['Tipo'] == 'Despesa']) if len(current_month_data[current_month_data['Tipo'] == 'Despesa']) > 0 else 0
    
    # Custos fixos do mês
    if 'Custo_Tipo' in current_month_data.columns:
        custos_fixos = current_month_data[
            (current_month_data['Custo_Tipo'] == 'Fixo') & 
            (current_month_data['Tipo'] == 'Despesa')
        ]['Valor_Absoluto'].sum()
        custos_variaveis = current_month_data[
            (current_month_data['Custo_Tipo'] == 'Variável') & 
            (current_month_data['Tipo'] == 'Despesa')
        ]['Valor_Absoluto'].sum()
    else:
        custos_fixos = 0
        custos_variaveis = total_despesas
    
    # Categoria que mais gastou
    despesas_mes = current_month_data[current_month_data['Tipo'] == 'Despesa']
    if not despesas_mes.empty:
        categoria_top = despesas_mes.groupby('Categoria')['Valor_Absoluto'].sum().idxmax()
        valor_categoria_top = despesas_mes.groupby('Categoria')['Valor_Absoluto'].sum().max()
    else:
        categoria_top = "N/A"
        valor_categoria_top = 0
    
    # Comparação com mês anterior
    months = sorted(df['Mes_Str'].unique())
    delta_despesas_pct = 0
    if len(months) >= 2:
        previous_month = months[-2]
        prev_month_data = df[df['Mes_Str'] == previous_month]
        prev_despesas = prev_month_data[prev_month_data['Tipo'] == 'Despesa']['Valor_Absoluto'].sum()
        if prev_despesas > 0:
            delta_despesas = total_despesas - prev_despesas
            delta_despesas_pct = (delta_despesas / prev_despesas * 100)
    
    # Exibir métricas
    if is_nubank_data:
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
                help="Número total de transações no período"
            )
        
        with col3:
            st.metric(
                "📊 Gasto Médio",
                f"R$ {gasto_medio_transacao:.2f}",
                help="Valor médio por transação no cartão"
            )
        
        with col4:
            st.metric(
                "🔒 Custos Fixos",
                f"R$ {custos_fixos:,.2f}",
                delta=f"{(custos_fixos/total_despesas*100):.1f}%" if total_despesas > 0 else None,
                help="Gastos fixos identificados no cartão"
            )
        
        with col5:
            st.metric(
                f"🏆 {categoria_top}",
                f"R$ {valor_categoria_top:,.2f}",
                delta=f"{(valor_categoria_top/total_despesas*100):.1f}%" if total_despesas > 0 else None,
                help="Categoria com maior gasto no cartão"
            )
        
        # Mostrar receitas/estornos se existirem
        if total_receitas > 0:
            st.info(f"💰 **Receitas/Estornos no período:** R$ {total_receitas:,.2f}")
    
    else:
        # Layout tradicional para dados bancários
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 Receitas",
                f"R$ {total_receitas:,.2f}",
                help=f"Total de receitas em {latest_month}"
            )
        
        with col2:
            st.metric(
                "💸 Despesas",
                f"R$ {total_despesas:,.2f}",
                delta=f"{delta_despesas_pct:+.1f}%" if abs(delta_despesas_pct) > 0.1 else None,
                help=f"Total de despesas em {latest_month}"
            )
        
        with col3:
            saldo = total_receitas - total_despesas
            st.metric(
                "💵 Saldo",
                f"R$ {saldo:,.2f}",
                delta="Positivo" if saldo > 0 else "Negativo",
                help="Saldo líquido do mês"
            )
        
        with col4:
            taxa_poupanca = (saldo / total_receitas * 100) if total_receitas > 0 else 0
            st.metric(
                "📊 Taxa Poupança",
                f"{taxa_poupanca:.1f}%",
                help="Percentual poupado do total de receitas"
            )
        
        with col5:
            st.metric(
                f"🏆 {categoria_top}",
                f"R$ {valor_categoria_top:,.2f}",
                delta=f"{(valor_categoria_top/total_despesas*100):.1f}%" if total_despesas > 0 else None,
                help="Categoria com maior despesa"
            )

def show_expense_titles_analysis(df, is_nubank_data=False):
    """Mostra análise detalhada dos títulos/descrições das transações"""
    title = "🏪 Análise Detalhada dos Estabelecimentos - Nubank" if is_nubank_data else "🏪 Análise Detalhada das Transações"
    st.subheader(title)
    
    if df.empty:
        st.info("Nenhum dado disponível para análise.")
        return
    
    # Estatísticas gerais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unique_descriptions = df['Descrição'].nunique()
        label = "🏪 Estabelecimentos Únicos" if is_nubank_data else "📝 Descrições Únicas"
        st.metric(label, unique_descriptions)
    
    with col2:
        most_frequent = df['Descrição'].mode().iloc[0] if not df['Descrição'].mode().empty else "N/A"
        frequency = df['Descrição'].value_counts().iloc[0] if len(df) > 0 else 0
        st.metric("🔄 Mais Frequente", f"{frequency}x", delta=most_frequent[:20] + "..." if len(most_frequent) > 20 else most_frequent)
    
    with col3:
        avg_per_establishment = df.groupby('Descrição')['Valor_Absoluto'].mean().mean()
        label = "💰 Gasto Médio por Local" if is_nubank_data else "💰 Valor Médio por Descrição"
        st.metric(label, f"R$ {avg_per_establishment:.2f}")
    
    # Análise por frequência
    freq_title = "🔄 Estabelecimentos por Frequência" if is_nubank_data else "🔄 Transações por Frequência"
    st.markdown(f"#### {freq_title}")
    
    frequency_analysis = df.groupby('Descrição').agg({
        'Valor_Absoluto': ['sum', 'mean', 'count'],
        'Data': ['min', 'max']
    }).round(2)
    
    frequency_analysis.columns = ['Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Transacao', 'Ultima_Transacao']
    frequency_analysis = frequency_analysis.sort_values('Frequencia', ascending=False)
    
    # Top 20 mais frequentes
    col1, col2 = st.columns(2)
    
    with col1:
        freq_label = "🏆 Top 10 - Mais Frequentes" if is_nubank_data else "🏆 Top 10 - Mais Usados"
        st.markdown(f"##### {freq_label}")
        top_frequent = frequency_analysis.head(10)
        
        for idx, (desc, row) in enumerate(top_frequent.iterrows(), 1):
            with st.expander(f"{idx}. {desc} ({int(row['Frequencia'])}x)"):
                st.write(f"💳 **Total:** R$ {row['Total_Gasto']:,.2f}")
                st.write(f"📊 **Gasto médio:** R$ {row['Gasto_Medio']:,.2f}")
                st.write(f"📅 **Primeira:** {row['Primeira_Transacao'].strftime('%d/%m/%Y')}")
                st.write(f"📅 **Última:** {row['Ultima_Transacao'].strftime('%d/%m/%Y')}")
                
                # Calcular frequência mensal
                dias_periodo = (row['Ultima_Transacao'] - row['Primeira_Transacao']).days
                if dias_periodo > 0:
                    freq_mensal = (row['Frequencia'] / dias_periodo) * 30
                    st.write(f"📈 **Frequência estimada:** {freq_mensal:.1f}x por mês")
    
    with col2:
        expense_label = "💸 Top 10 - Maiores Gastos" if is_nubank_data else "💸 Top 10 - Maiores Valores"
        st.markdown(f"##### {expense_label}")
        top_expensive = frequency_analysis.sort_values('Total_Gasto', ascending=False).head(10)
        
        for idx, (desc, row) in enumerate(top_expensive.iterrows(), 1):
            with st.expander(f"{idx}. {desc} (R$ {row['Total_Gasto']:,.2f})"):
                st.write(f"🔄 **Frequência:** {int(row['Frequencia'])}x")
                st.write(f"📊 **Gasto médio:** R$ {row['Gasto_Medio']:,.2f}")
                st.write(f"📅 **Primeira:** {row['Primeira_Transacao'].strftime('%d/%m/%Y')}")
                st.write(f"📅 **Última:** {row['Ultima_Transacao'].strftime('%d/%m/%Y')}")
                
                # Percentual do total
                total_geral = df['Valor_Absoluto'].sum()
                percentual = (row['Total_Gasto'] / total_geral) * 100
                st.write(f"📊 **Representa:** {percentual:.1f}% do total")
    
    # Busca por estabelecimento
    search_label = "🔍 Buscar Estabelecimento" if is_nubank_data else "🔍 Buscar Transação"
    st.markdown(f"#### {search_label}")
    search_placeholder = "Ex: SUPERMERCADO, POSTO, RESTAURANTE" if is_nubank_data else "Ex: MERCADO, FARMACIA, TRANSFERENCIA"
    search_term = st.text_input("Digite o termo para buscar:", placeholder=search_placeholder)
    
    if search_term:
        filtered_descriptions = df[df['Descrição'].str.contains(search_term, case=False, na=False)]
        
        if not filtered_descriptions.empty:
            search_results = filtered_descriptions.groupby('Descrição').agg({
                'Valor_Absoluto': ['sum', 'mean', 'count'],
                'Data': ['min', 'max']
            }).round(2)
            
            search_results.columns = ['Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Transacao', 'Ultima_Transacao']
            search_results = search_results.sort_values('Total_Gasto', ascending=False)
            
            st.write(f"🎯 **Encontrados {len(search_results)} resultados com '{search_term}'**")
            
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
                    st.metric("📅 Período", f"{row['Primeira_Transacao'].strftime('%m/%Y')} - {row['Ultima_Transacao'].strftime('%m/%Y')}")
                st.markdown("---")
        else:
            st.info(f"Nenhum resultado encontrado com '{search_term}'")
    
    # Lista completa com filtros
    st.markdown("#### 📋 Lista Completa")
    
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
            'Primeira_Transacao': lambda x: x.strftime('%d/%m/%Y'),
            'Ultima_Transacao': lambda x: x.strftime('%d/%m/%Y')
        }),
        use_container_width=True,
        height=400
    )

def main():
    """Função principal do dashboard"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>💰 Dashboard Financeiro Avançado</h1>
        <p>Análise Completa e Inteligente dos seus Gastos Pessoais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para configurações
    st.sidebar.title("⚙️ Configurações")
    st.sidebar.markdown("### 📁 Status dos Arquivos")
    
    # Carregar dados
    with st.spinner("🔄 Carregando dados..."):
        df, loaded_files, is_nubank_data = load_csv_files()
    
    if df.empty:
        st.error("⚠️ **Nenhum dado encontrado!**")
        
        st.markdown("""
        <div class="warning-box">
        <h4>📋 Como adicionar dados:</h4>
        <ol>
        <li><strong>Para dados do Nubank:</strong></li>
        <ul>
            <li>Baixe o extrato do cartão no app/site do Nubank</li>
            <li>Salve como <code>Nubank_YYYYMMDD.csv</code></li>
            <li>Formato esperado: <code>date, title, amount</code></li>
        </ul>
        <li><strong>Para dados bancários tradicionais:</strong></li>
        <ul>
            <li>Exporte extratos em CSV</li>
            <li>Formato esperado: <code>Data, Descrição, Valor</code></li>
        </ul>
        <li><strong>Coloque os arquivos em:</strong></li>
        <ul>
            <li>Pasta atual (raiz do projeto)</li>
            <li><code>data/raw/</code></li>
            <li><code>extratos/</code></li>
        </ul>
        <li><strong>Atualize a página (F5)</strong></li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload de arquivo
        st.markdown("### 📤 Upload de Extrato")
        uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")
        
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
    
    # Detectar tipo de dados e mostrar indicador
    if is_nubank_data:
        st.markdown("""
        <div class="nubank-mode-indicator">
        <h4>💳 Dados Nubank Detectados</h4>
        <p><strong>Processamento otimizado para dados do cartão Nubank:</strong></p>
        <ul>
            <li>🏪 <strong>Análise de estabelecimentos</strong> - Onde você mais usa o cartão</li>
            <li>🔄 <strong>Frequência de compras</strong> - Quantas vezes comprou em cada lugar</li>
            <li>💡 <strong>Categorização inteligente</strong> - Baseada em padrões do Nubank</li>
            <li>📊 <strong>Controle de gastos</strong> - Comparação entre períodos</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Processar dados
    with st.spinner("🔧 Processando dados financeiros..."):
        try:
            df = process_financial_data(df, is_nubank_data)
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
    
    if is_nubank_data:
        st.sidebar.markdown("""
        <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
        <h4>💳 Modo Nubank Ativo</h4>
        <p><strong>Características:</strong></p>
        <ul>
            <li>✅ Dados do cartão Nubank</li>
            <li>✅ Análise de estabelecimentos</li>
            <li>✅ Frequência de uso por local</li>
            <li>✅ Categorização otimizada</li>
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
        create_financial_summary_cards(filtered_df, monthly_analysis_filtered, is_nubank_data)
    
    st.markdown("---")
    
    # Criar visualizações
    if not monthly_analysis_filtered.empty:
        try:
            fig_monthly, fig_category, fig_fixed_var, fig_trends, fig_gauge = create_visualizations_nubank(
                filtered_df, monthly_analysis_filtered, is_nubank_data
            )
        except Exception as e:
            st.error(f"❌ Erro ao criar visualizações: {e}")
            fig_monthly = fig_category = fig_fixed_var = fig_trends = fig_gauge = None
        
        # Tabs organizadas
        tab_names = [
            "📊 Visão Geral", 
            "💡 Custos Fixos vs Variáveis", 
            "📈 Tendências", 
            "🏪 Estabelecimentos" if is_nubank_data else "📝 Detalhes",
            "📋 Dados Brutos",
            "📊 Relatórios"
        ]
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_names)
        
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
                    st.subheader("🔒 Custos Fixos Identificados")
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
                            st.info("Nenhum custo fixo identificado")
                
                with col2:
                    st.subheader("📊 Distribuição dos Gastos")
                    if 'Custo_Tipo' in filtered_df.columns:
                        despesas_only = filtered_df[filtered_df['Tipo'] == 'Despesa']
                        summary = despesas_only.groupby('Custo_Tipo')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
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
            
            # Top gastos
            top_label = "🔝 Maiores Gastos do Período" if is_nubank_data else "🔝 Maiores Transações do Período"
            st.subheader(top_label)
            
            despesas_filtered = filtered_df[filtered_df['Tipo'] == 'Despesa']
            top_expenses = despesas_filtered.nlargest(15, 'Valor_Absoluto')
            
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
        
        # Tab 4 - Estabelecimentos/Detalhes
        with tab4:
            show_expense_titles_analysis(filtered_df, is_nubank_data)
        
        # Tab 5 - Dados Brutos
        with tab5:
            data_title = "📋 Dados Completos do Nubank" if is_nubank_data else "📋 Dados Completos"
            st.subheader(data_title)
            
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
            cols_to_show = ['Data', 'Descrição', 'Categoria', 'Valor_Absoluto', 'Tipo']
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
            file_prefix = "dados_nubank" if is_nubank_data else "dados_financeiros"
            st.download_button(
                label="📥 Baixar dados (CSV)",
                data=csv,
                file_name=f"{file_prefix}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Tab 6 - Relatórios
        with tab6:
            report_title = "📊 Relatórios Nubank" if is_nubank_data else "📊 Relatórios Financeiros"
            st.subheader(report_title)
            
            report_options = ["Mensal Detalhado", "Por Categoria", "Estabelecimentos Frequentes", "Custos Fixos"] if is_nubank_data else \
                           ["Mensal Detalhado", "Por Categoria", "Transações Frequentes", "Custos Fixos"]
            
            report_type = st.selectbox("Tipo de Relatório", report_options)
            
            if st.button("📄 Gerar Relatório"):
                if report_type == "Mensal Detalhado":
                    st.write(f"### 📊 Relatório Mensal - {('Nubank' if is_nubank_data else 'Financeiro')}")
                    
                    for _, row in monthly_analysis_filtered.iterrows():
                        st.write(f"**Mês: {row['Mes_Str']}**")
                        
                        if 'Despesa' in row:
                            st.write(f"- Total despesas: R$ {row['Despesa']:,.2f}")
                        if 'Receita' in row and row['Receita'] > 0:
                            st.write(f"- Total receitas: R$ {row['Receita']:,.2f}")
                        if 'Saldo' in row:
                            st.write(f"- Saldo: R$ {row['Saldo']:,.2f}")
                        
                        # Calcular número de transações no mês
                        month_transactions = filtered_df[filtered_df['Mes_Str'] == row['Mes_Str']]
                        st.write(f"- Transações: {len(month_transactions)}")
                        st.write("---")
                
                elif report_type in ["Estabelecimentos Frequentes", "Transações Frequentes"]:
                    st.write(f"### 🏪 Relatório de {report_type}")
                    
                    establishment_report = filtered_df.groupby('Descrição').agg({
                        'Valor_Absoluto': ['sum', 'mean', 'count'],
                        'Data': ['min', 'max']
                    }).round(2)
                    
                    establishment_report.columns = ['Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Transacao', 'Ultima_Transacao']
                    establishment_report = establishment_report.sort_values('Frequencia', ascending=False).head(20)
                    
                    for desc, row in establishment_report.iterrows():
                        st.write(f"**{desc}**")
                        st.write(f"- Frequência: {int(row['Frequencia'])} vezes")
                        st.write(f"- Total: R$ {row['Total_Gasto']:,.2f}")
                        st.write(f"- Gasto médio: R$ {row['Gasto_Medio']:,.2f}")
                        st.write(f"- Período: {row['Primeira_Transacao'].strftime('%d/%m/%Y')} até {row['Ultima_Transacao'].strftime('%d/%m/%Y')}")
                        st.write("---")
                
                elif report_type == "Por Categoria":
                    st.write("### 🏷️ Relatório por Categoria")
                    
                    despesas_filtered = filtered_df[filtered_df['Tipo'] == 'Despesa']
                    category_report = despesas_filtered.groupby('Categoria').agg({
                        'Valor_Absoluto': ['sum', 'mean', 'count'],
                        'Data': ['min', 'max']
                    }).round(2)
                    
                    for categoria in category_report.index:
                        st.write(f"**{categoria}**")
                        st.write(f"- Total: R$ {category_report.loc[categoria, ('Valor_Absoluto', 'sum')]:,.2f}")
                        st.write(f"- Gasto médio: R$ {category_report.loc[categoria, ('Valor_Absoluto', 'mean')]:,.2f}")
                        st.write(f"- Número de transações: {category_report.loc[categoria, ('Valor_Absoluto', 'count')]:.0f}")
                        st.write("---")
                
                # Botão para exportar relatório
                report_content = f"Relatório {report_type} - {'Nubank' if is_nubank_data else 'Financeiro'}\nGerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                st.download_button(
                    label="📥 Baixar Relatório (TXT)",
                    data=report_content,
                    file_name=f"relatorio_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
    
    else:
        st.warning("⚠️ Não foi possível gerar as visualizações. Verifique se há dados suficientes.")
    
    # Footer
    footer_text = "💳 Dashboard Nubank" if is_nubank_data else "💰 Dashboard Financeiro"
    st.markdown(f"""
    <div class="footer">
        <h3>{footer_text}</h3>
        <p>Análise completa e inteligente dos seus dados financeiros | 🔒 Dados processados localmente</p>
        <p>Versão 4.0 - Otimizada para dados Nubank e bancários tradicionais</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()