import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ExpenseAnalyzer:
    def __init__(self, df):
        self.df = df
    
    def monthly_analysis(self):
        """Análise mensal detalhada"""
        monthly_data = self.df.groupby(['Mes', 'Tipo']).agg({
            'Valor_Absoluto': 'sum',
            'ID': 'count'
        }).reset_index()
        
        # Pivot para ter receitas e despesas lado a lado
        monthly_pivot = monthly_data.pivot(
            index='Mes',
            columns='Tipo',
            values='Valor_Absoluto'
        ).fillna(0)
        
        monthly_pivot['Saldo'] = monthly_pivot.get('Receita', 0) - monthly_pivot.get('Despesa', 0)
        monthly_pivot['Taxa_Poupanca'] = (monthly_pivot['Saldo'] / monthly_pivot.get('Receita', 1)) * 100
        
        return monthly_pivot.reset_index()
    
    def fixed_vs_variable_analysis(self):
        """Análise custos fixos vs variáveis"""
        fixed_var_analysis = self.df[self.df['Tipo'] == 'Despesa'].groupby(['Mes', 'Custo_Tipo']).agg({
            'Valor_Absoluto': 'sum'
        }).reset_index()
        
        return fixed_var_analysis.pivot(
            index='Mes',
            columns='Custo_Tipo',
            values='Valor_Absoluto'
        ).fillna(0).reset_index()
    
    def category_trends(self):
        """Tendências por categoria"""
        category_monthly = self.df[self.df['Tipo'] == 'Despesa'].groupby(['Mes', 'Categoria']).agg({
            'Valor_Absoluto': 'sum'
        }).reset_index()
        
        return category_monthly
    
    def expense_predictions(self):
        """Previsões baseadas em tendências"""
        monthly_expenses = self.df[self.df['Tipo'] == 'Despesa'].groupby('Mes')['Valor_Absoluto'].sum()
        
        # Média dos últimos 3 meses
        last_3_months = monthly_expenses.tail(3).mean()
        
        # Tendência linear simples
        if len(monthly_expenses) >= 3:
            x = np.arange(len(monthly_expenses))
            y = monthly_expenses.values
            trend = np.polyfit(x, y, 1)
            next_month_prediction = trend[0] * len(monthly_expenses) + trend[1]
        else:
            next_month_prediction = last_3_months
        
        return {
            'media_3_meses': last_3_months,
            'previsao_proximo_mes': next_month_prediction,
            'tendencia': 'Alta' if next_month_prediction > last_3_months else 'Baixa'
        }
    
    def top_expenses_analysis(self, top_n=10):
        """Análise dos maiores gastos"""
        top_expenses = self.df[self.df['Tipo'] == 'Despesa'].nlargest(top_n, 'Valor_Absoluto')
        return top_expenses[['Data', 'Descrição', 'Categoria', 'Valor_Absoluto', 'Custo_Tipo']]