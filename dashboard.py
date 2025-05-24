import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob
from datetime import datetime, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="💰 Dashboard Financeiro Avançado",
    page_icon="💰",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stMetric > label {
        color: #2c3e50 !important;
        font-weight: bold !important;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_csv_files():
    """Carrega todos os CSVs da pasta especificada"""
    # Procurar CSVs tanto na pasta atual quanto em subpastas
    csv_patterns = [
        "*.csv",
        "data/*.csv", 
        "data/raw/*.csv",
        "extratos/*.csv"
    ]
    
    all_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
    
    if not all_files:
        return pd.DataFrame()
    
    dfs = []
    for file in all_files:
        try:
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is not None:
                df['arquivo_origem'] = os.path.basename(file)
                dfs.append(df)
                st.sidebar.success(f"✅ {os.path.basename(file)}")
            else:
                st.sidebar.error(f"❌ Erro: {os.path.basename(file)}")
                
        except Exception as e:
            st.sidebar.error(f"❌ {os.path.basename(file)}: {str(e)}")
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

@st.cache_data
def process_financial_data(df):
    """Processa e limpa os dados financeiros"""
    if df.empty:
        return df
    
    # Converter data
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])
    
    # Criar colunas de tempo
    df['Mes'] = df['Data'].dt.to_period('M')
    df['Mes_Str'] = df['Data'].dt.strftime('%Y-%m')
    df['Ano'] = df['Data'].dt.year
    df['Mes_Nome'] = df['Data'].dt.strftime('%B')
    df['Dia_Semana'] = df['Data'].dt.strftime('%A')
    
    # Processar valores
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df = df.dropna(subset=['Valor'])
    
    # Classificar receitas e despesas
    df['Tipo'] = df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
    df['Valor_Absoluto'] = df['Valor'].abs()
    
    # Limpar descrições
    if 'Descrição' in df.columns:
        df['Descrição'] = df['Descrição'].fillna('Sem descrição')
        df['Descrição'] = df['Descrição'].str.strip()
    
    # Preencher categorias faltantes
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].fillna('Outros')
    else:
        df['Categoria'] = 'Outros'
    
    # Identificar custos fixos automaticamente
    df = identify_fixed_costs(df)
    
    # Remover duplicatas se existir coluna ID
    if 'ID' in df.columns:
        df = df.drop_duplicates(subset=['ID'], keep='first')
    
    return df

def identify_fixed_costs(df):
    """Identifica custos fixos vs variáveis"""
    df['Custo_Tipo'] = 'Variável'
    
    # Padrões conhecidos de custos fixos
    fixed_patterns = {
        'Moradia': ['FERREIRA IMOVEIS', 'ALUGUEL', 'CONDOMINIO', 'IPTU'],
        'Educação': ['ESCOLA', 'GREMIO NAUTICO', 'MENSALIDADE'],
        'Telefone': ['CLARO', 'TIM SA', 'VIVO', 'OI'],
        'Transferências para terceiros': ['COPE SERVICOS', 'CONTABIL'],
        'Saúde': ['PLANO DE SAUDE', 'UNIMED', 'BRADESCO SAUDE']
    }
    
    for categoria, patterns in fixed_patterns.items():
        for pattern in patterns:
            if 'Descrição' in df.columns:
                mask = (df['Categoria'] == categoria) & \
                       (df['Descrição'].str.contains(pattern, case=False, na=False))
                df.loc[mask, 'Custo_Tipo'] = 'Fixo'
    
    # Identificar gastos recorrentes (aparecem em pelo menos 3 meses)
    if len(df) > 0:
        despesas = df[df['Tipo'] == 'Despesa'].copy()
        if not despesas.empty and 'Descrição' in despesas.columns:
            # Contar frequência por descrição
            freq_descriptions = despesas.groupby('Descrição')['Mes'].nunique()
            recurring_descriptions = freq_descriptions[freq_descriptions >= 3].index
            
            # Marcar como fixo
            mask = df['Descrição'].isin(recurring_descriptions) & (df['Tipo'] == 'Despesa')
            df.loc[mask, 'Custo_Tipo'] = 'Fixo'
    
    return df

def create_monthly_analysis(df):
    """Cria análise mensal"""
    monthly_data = df.groupby(['Mes_Str', 'Tipo']).agg({
        'Valor_Absoluto': 'sum',
        'ID': 'count' if 'ID' in df.columns else 'size'
    }).reset_index()
    
    # Pivot para ter receitas e despesas lado a lado
    monthly_pivot = monthly_data.pivot(
        index='Mes_Str',
        columns='Tipo',
        values='Valor_Absoluto'
    ).fillna(0)
    
    # Calcular saldo e taxa de poupança
    monthly_pivot['Saldo'] = monthly_pivot.get('Receita', 0) - monthly_pivot.get('Despesa', 0)
    monthly_pivot['Taxa_Poupanca'] = (
        monthly_pivot['Saldo'] / monthly_pivot.get('Receita', 1) * 100
    ).replace([np.inf, -np.inf], 0)
    
    return monthly_pivot.reset_index()

def create_visualizations(df, monthly_analysis):
    """Cria todas as visualizações"""
    
    # 1. Gráfico de receitas vs despesas
    fig_monthly = go.Figure()
    
    fig_monthly.add_trace(go.Bar(
        name='Receitas',
        x=monthly_analysis['Mes_Str'],
        y=monthly_analysis.get('Receita', 0),
        marker_color='#2ecc71',
        yaxis='y'
    ))
    
    fig_monthly.add_trace(go.Bar(
        name='Despesas',
        x=monthly_analysis['Mes_Str'],
        y=monthly_analysis.get('Despesa', 0),
        marker_color='#e74c3c',
        yaxis='y'
    ))
    
    fig_monthly.add_trace(go.Scatter(
        name='Saldo',
        x=monthly_analysis['Mes_Str'],
        y=monthly_analysis['Saldo'],
        mode='lines+markers',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    fig_monthly.update_layout(
        title='📊 Receitas vs Despesas Mensais',
        xaxis_title='Mês',
        yaxis=dict(title='Valor (R$)', side='left'),
        yaxis2=dict(title='Saldo (R$)', overlaying='y', side='right'),
        barmode='group',
        height=500,
        hovermode='x unified'
    )
    
    # 2. Gráfico de pizza por categoria
    category_data = df[df['Tipo'] == 'Despesa'].groupby('Categoria')['Valor_Absoluto'].sum().reset_index()
    category_data = category_data.sort_values('Valor_Absoluto', ascending=False)
    
    fig_category = px.pie(
        category_data, 
        values='Valor_Absoluto', 
        names='Categoria',
        title='🏷️ Distribuição de Gastos por Categoria',
        hole=0.4
    )
    fig_category.update_traces(textposition='inside', textinfo='percent+label')
    
    # 3. Custos fixos vs variáveis
    if 'Custo_Tipo' in df.columns:
        fixed_var_data = df[df['Tipo'] == 'Despesa'].groupby(['Mes_Str', 'Custo_Tipo'])['Valor_Absoluto'].sum().reset_index()
        
        fig_fixed_var = px.bar(
            fixed_var_data,
            x='Mes_Str',
            y='Valor_Absoluto',
            color='Custo_Tipo',
            title='💡 Custos Fixos vs Variáveis por Mês',
            color_discrete_map={'Fixo': '#e74c3c', 'Variável': '#3498db'}
        )
        fig_fixed_var.update_layout(height=400)
    else:
        fig_fixed_var = None
    
    # 4. Tendências por categoria (top 6)
    top_categories = category_data.head(6)['Categoria']
    trend_data = df[
        (df['Categoria'].isin(top_categories)) & 
        (df['Tipo'] == 'Despesa')
    ].groupby(['Mes_Str', 'Categoria'])['Valor_Absoluto'].sum().reset_index()
    
    fig_trends = px.line(
        trend_data,
        x='Mes_Str',
        y='Valor_Absoluto',
        color='Categoria',
        title='📈 Tendência dos Gastos por Categoria (Top 6)',
        markers=True
    )
    fig_trends.update_layout(height=400)
    
    # 5. Gauge da taxa de poupança
    latest_rate = monthly_analysis['Taxa_Poupanca'].iloc[-1] if len(monthly_analysis) > 0 else 0
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=latest_rate,
        delta={'reference': 20},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Taxa de Poupança (%)"},
        gauge={
            'axis': {'range': [None, 50]},
            'bar': {'color': "#3498db"},
            'steps': [
                {'range': [0, 10], 'color': "#ecf0f1"},
                {'range': [10, 20], 'color': "#f39c12"},
                {'range': [20, 50], 'color': "#2ecc71"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 20
            }
        }
    ))
    
    return fig_monthly, fig_category, fig_fixed_var, fig_trends, fig_gauge

def main():
    """Função principal do dashboard"""
    
    # Header
    st.title("💰 Dashboard Financeiro Avançado")
    st.markdown("### 📊 Análise Completa dos seus Gastos Pessoais")
    st.markdown("---")
    
    # Sidebar para configurações
    st.sidebar.title("⚙️ Configurações")
    st.sidebar.markdown("### 📁 Status dos Arquivos")
    
    # Carregar dados
    with st.spinner("🔄 Carregando dados..."):
        df = load_csv_files()
    
    if df.empty:
        st.error("⚠️ **Nenhum dado encontrado!**")
        st.info("""
        📋 **Como adicionar dados:**
        1. Coloque seus arquivos CSV do Nubank em uma das pastas:
           - Pasta atual
           - `data/` ou `data/raw/`
           - `extratos/`
        2. Atualize a página (F5)
        
        📄 **Formato esperado:**
        - ID, Data, Valor, Descrição, Categoria
        """)
        return
    
    # Processar dados
    with st.spinner("🔧 Processando dados..."):
        df = process_financial_data(df)
    
    if df.empty:
        st.error("❌ Erro ao processar os dados!")
        return
    
    # Análise mensal
    monthly_analysis = create_monthly_analysis(df)
    
    # Sidebar com informações
    st.sidebar.success(f"✅ **{len(df):,}** transações carregadas")
    st.sidebar.info(f"📅 **Período:** {df['Data'].min().date()} até {df['Data'].max().date()}")
    
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
    
    # Filtro de tipo de custo
    if 'Custo_Tipo' in df.columns:
        cost_type = st.sidebar.selectbox(
            "💡 Tipo de Custo",
            options=['Todos', 'Fixo', 'Variável']
        )
    else:
        cost_type = 'Todos'
    
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
    
    # Filtro de tipo de custo
    if cost_type != 'Todos' and 'Custo_Tipo' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Custo_Tipo'] == cost_type]
    
    # Recalcular análise mensal com dados filtrados
    monthly_analysis_filtered = create_monthly_analysis(filtered_df)
    
    # Métricas principais
    if not filtered_df.empty:
        latest_month = filtered_df['Mes_Str'].max()
        current_month_data = filtered_df[filtered_df['Mes_Str'] == latest_month]
        
        total_receitas = current_month_data[current_month_data['Tipo'] == 'Receita']['Valor_Absoluto'].sum()
        total_despesas = current_month_data[current_month_data['Tipo'] == 'Despesa']['Valor_Absoluto'].sum()
        saldo = total_receitas - total_despesas
        taxa_poupanca = (saldo / total_receitas * 100) if total_receitas > 0 else 0
        
        # Custos fixos do mês
        if 'Custo_Tipo' in current_month_data.columns:
            custos_fixos = current_month_data[
                (current_month_data['Tipo'] == 'Despesa') & 
                (current_month_data['Custo_Tipo'] == 'Fixo')
            ]['Valor_Absoluto'].sum()
        else:
            custos_fixos = 0
        
        # Exibir métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Receitas do Mês", 
                f"R$ {total_receitas:,.2f}",
                help="Total de receitas do último mês"
            )
        
        with col2:
            st.metric(
                "💸 Despesas do Mês", 
                f"R$ {total_despesas:,.2f}",
                help="Total de despesas do último mês"
            )
        
        with col3:
            delta_color = "normal" if saldo >= 0 else "inverse"
            st.metric(
                "💵 Saldo do Mês", 
                f"R$ {saldo:,.2f}",
                delta=f"{taxa_poupanca:.1f}% poupança",
                help="Saldo = Receitas - Despesas"
            )
        
        with col4:
            st.metric(
                "🔒 Custos Fixos", 
                f"R$ {custos_fixos:,.2f}",
                help="Gastos recorrentes identificados"
            )
    
    st.markdown("---")
    
    # Criar visualizações
    if not monthly_analysis_filtered.empty:
        fig_monthly, fig_category, fig_fixed_var, fig_trends, fig_gauge = create_visualizations(filtered_df, monthly_analysis_filtered)
        
        # Tabs para organizar o conteúdo
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Visão Geral", 
            "💡 Custos Fixos vs Variáveis", 
            "📈 Tendências", 
            "🔍 Análise Detalhada",
            "📋 Dados Brutos"
        ])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(fig_monthly, use_container_width=True)
            
            with col2:
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Gráfico de pizza
            st.plotly_chart(fig_category, use_container_width=True)
        
        with tab2:
            if fig_fixed_var:
                st.plotly_chart(fig_fixed_var, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔒 Principais Custos Fixos")
                    if 'Custo_Tipo' in filtered_df.columns:
                        fixed_expenses = filtered_df[
                            (filtered_df['Custo_Tipo'] == 'Fixo') & 
                            (filtered_df['Tipo'] == 'Despesa')
                        ].groupby('Descrição')['Valor_Absoluto'].mean().sort_values(ascending=False).head(10)
                        
                        if not fixed_expenses.empty:
                            st.dataframe(
                                fixed_expenses.to_frame('Valor Médio').style.format({'Valor Médio': 'R$ {:.2f}'}),
                                use_container_width=True
                            )
                        else:
                            st.info("Nenhum custo fixo identificado")
                    else:
                        st.info("Análise de custos fixos não disponível")
                
                with col2:
                    st.subheader("📊 Resumo por Tipo")
                    if 'Custo_Tipo' in filtered_df.columns:
                        summary = filtered_df[filtered_df['Tipo'] == 'Despesa'].groupby('Custo_Tipo')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
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
                st.info("💡 Análise de custos fixos vs variáveis não disponível")
        
        with tab3:
            st.plotly_chart(fig_trends, use_container_width=True)
            
            # Top gastos
            st.subheader("🔝 Maiores Gastos do Período")
            top_expenses = filtered_df[filtered_df['Tipo'] == 'Despesa'].nlargest(15, 'Valor_Absoluto')
            
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
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Resumo Mensal")
                if not monthly_analysis_filtered.empty:
                    display_monthly = monthly_analysis_filtered.copy()
                    display_monthly = display_monthly.style.format({
                        'Receita': 'R$ {:.2f}',
                        'Despesa': 'R$ {:.2f}',
                        'Saldo': 'R$ {:.2f}',
                        'Taxa_Poupanca': '{:.1f}%'
                    })
                    st.dataframe(display_monthly, use_container_width=True)
            
            with col2:
                st.subheader("🏷️ Gastos por Categoria")
                category_summary = filtered_df[filtered_df['Tipo'] == 'Despesa'].groupby('Categoria')['Valor_Absoluto'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
                category_summary.columns = ['Total', 'Qtd', 'Média']
                
                st.dataframe(
                    category_summary.style.format({
                        'Total': 'R$ {:.2f}',
                        'Qtd': '{:.0f}',
                        'Média': 'R$ {:.2f}'
                    }),
                    use_container_width=True
                )
            
            # Previsões simples
            if len(monthly_analysis_filtered) >= 3:
                st.subheader("🔮 Previsões Simples")
                
                # Média dos últimos 3 meses
                last_3_months = monthly_analysis_filtered['Despesa'].tail(3).mean()
                
                # Tendência linear
                x = np.arange(len(monthly_analysis_filtered))
                y = monthly_analysis_filtered['Despesa'].values
                if len(y) > 1:
                    trend = np.polyfit(x, y, 1)
                    next_month_prediction = trend[0] * len(monthly_analysis_filtered) + trend[1]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Média 3 Meses", f"R$ {last_3_months:,.2f}")
                    with col2:
                        st.metric("🔮 Previsão Próximo Mês", f"R$ {next_month_prediction:,.2f}")
                    with col3:
                        trend_direction = "📈 Alta" if next_month_prediction > last_3_months else "📉 Baixa"
                        st.metric("📊 Tendência", trend_direction)
        
        with tab5:
            st.subheader("📋 Dados Completos")
            
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
            cols_to_show = ['Data', 'Descrição', 'Categoria', 'Valor', 'Tipo']
            if 'Custo_Tipo' in display_df.columns:
                cols_to_show.append('Custo_Tipo')
            
            st.dataframe(
                display_df[cols_to_show].style.format({
                    'Data': lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '',
                    'Valor': 'R$ {:.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Botão de download
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados filtrados (CSV)",
                data=csv,
                file_name=f"dados_financeiros_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        💰 Dashboard Financeiro Avançado | 
        Desenvolvido para análise pessoal de gastos | 
        🔒 Seus dados são processados localmente
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()