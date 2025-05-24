import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class FinancialVisualizations:
    def __init__(self, df):
        self.df = df
    
    def monthly_balance_chart(self, monthly_data):
        """Gráfico de saldo mensal"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Receitas',
            x=monthly_data['Mes'].astype(str),
            y=monthly_data.get('Receita', 0),
            marker_color='green'
        ))
        
        fig.add_trace(go.Bar(
            name='Despesas',
            x=monthly_data['Mes'].astype(str),
            y=monthly_data.get('Despesa', 0),
            marker_color='red'
        ))
        
        fig.add_trace(go.Scatter(
            name='Saldo',
            x=monthly_data['Mes'].astype(str),
            y=monthly_data['Saldo'],
            mode='lines+markers',
            line=dict(color='blue', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Receitas vs Despesas Mensais',
            xaxis_title='Mês',
            yaxis_title='Valor (R$)',
            yaxis2=dict(title='Saldo (R$)', overlaying='y', side='right'),
            barmode='group',
            height=500
        )
        
        return fig
    
    def fixed_variable_comparison(self, fixed_var_data):
        """Gráfico custos fixos vs variáveis"""
        fig = px.bar(
            fixed_var_data.melt(id_vars=['Mes'], var_name='Tipo', value_name='Valor'),
            x='Mes',
            y='Valor',
            color='Tipo',
            title='Custos Fixos vs Variáveis por Mês',
            color_discrete_map={'Fixo': '#FF6B6B', 'Variável': '#4ECDC4'}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def category_sunburst(self):
        """Gráfico sunburst por categoria"""
        category_data = self.df[self.df['Tipo'] == 'Despesa'].groupby(['Categoria', 'Custo_Tipo'])['Valor_Absoluto'].sum().reset_index()
        
        fig = px.sunburst(
            category_data,
            path=['Categoria', 'Custo_Tipo'],
            values='Valor_Absoluto',
            title='Distribuição de Gastos por Categoria e Tipo'
        )
        
        return fig
    
    def expense_trend_by_category(self, category_trends):
        """Tendência de gastos por categoria"""
        top_categories = category_trends.groupby('Categoria')['Valor_Absoluto'].sum().nlargest(6).index
        
        filtered_data = category_trends[category_trends['Categoria'].isin(top_categories)]
        
        fig = px.line(
            filtered_data,
            x='Mes',
            y='Valor_Absoluto',
            color='Categoria',
            title='Tendência dos Gastos por Categoria (Top 6)',
            markers=True
        )
        
        fig.update_layout(height=400)
        return fig
    
    def savings_rate_gauge(self, monthly_data):
        """Gauge da taxa de poupança"""
        latest_rate = monthly_data['Taxa_Poupanca'].iloc[-1] if len(monthly_data) > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = latest_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Taxa de Poupança (%)"},
            gauge = {
                'axis': {'range': [None, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 10], 'color': "lightgray"},
                    {'range': [10, 25], 'color': "gray"},
                    {'range': [25, 50], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 20
                }
            }
        ))
        
        return fig