"""
Sistema de Análise Avançada e Relatórios Financeiros
ATUALIZADO para suportar formato Nubank (date, title, amount)
Gera insights, alertas e relatórios detalhados
Execute: python advanced_analytics.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
from typing import Dict, List, Tuple, Optional
import json
import glob
from dataclasses import dataclass

warnings.filterwarnings('ignore')

@dataclass
class FinancialAlert:
    """Representa um alerta financeiro"""
    type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    title: str
    message: str
    value: Optional[float] = None
    category: Optional[str] = None
    date: Optional[datetime] = None

class FinancialAnalyzer:
    """Analisador avançado de dados financeiros - Otimizado para Nubank"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador
        
        Args:
            df: DataFrame com dados financeiros processados
        """
        self.df = df.copy()
        self.alerts = []
        self.insights = []
        self.is_nubank_data = self._detect_nubank_format()
        
        # Configurações de análise
        self.alert_thresholds = {
            'expense_spike': 1.5,  # 50% acima da média
            'low_savings_rate': 10,  # Menos de 10% de poupança
            'category_limit': 0.3,  # Mais de 30% em uma categoria
            'unusual_transaction': 3,  # 3 desvios padrão
            'recurring_anomaly': 0.2  # 20% de variação em custos fixos
        }
        
        self._prepare_data()
    
    def _detect_nubank_format(self) -> bool:
        """Detecta se o DataFrame está no formato Nubank"""
        nubank_columns = ['date', 'title', 'amount']
        return all(col in self.df.columns for col in nubank_columns)
    
    def _prepare_data(self):
        """Prepara dados para análise"""
        if self.df.empty:
            return
        
        print(f"📊 Preparando dados - Formato: {'Nubank' if self.is_nubank_data else 'Tradicional'}")
        
        if self.is_nubank_data:
            # Formato Nubank: date, title, amount
            required_cols = ['date', 'title', 'amount']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            
            if missing_cols:
                raise ValueError(f"Colunas Nubank obrigatórias faltando: {missing_cols}")
            
            # Normalizar colunas para análise
            self.df['Data'] = pd.to_datetime(self.df['date'], errors='coerce')
            self.df['Descrição'] = self.df['title'].fillna('Sem descrição')
            self.df['Valor'] = pd.to_numeric(self.df['amount'], errors='coerce')
            
            # No Nubank: negativos = despesas, positivos = receitas/estornos
            self.df['Tipo'] = self.df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
            self.df['Valor_Absoluto'] = self.df['Valor'].abs()
            
            # Categoria padrão se não existir
            if 'Categoria' not in self.df.columns:
                self.df['Categoria'] = 'Outros'
        else:
            # Formato tradicional
            required_cols = ['Data', 'Valor']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            
            if missing_cols:
                raise ValueError(f"Colunas obrigatórias faltando: {missing_cols}")
            
            # Processar formato tradicional
            self.df['Data'] = pd.to_datetime(self.df['Data'], errors='coerce')
            self.df['Valor'] = pd.to_numeric(self.df['Valor'], errors='coerce')
            self.df['Tipo'] = self.df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
            self.df['Valor_Absoluto'] = self.df['Valor'].abs()
            
            if 'Descrição' not in self.df.columns:
                self.df['Descrição'] = 'Sem descrição'
            if 'Categoria' not in self.df.columns:
                self.df['Categoria'] = 'Outros'
        
        # Limpar dados inválidos
        self.df = self.df.dropna(subset=['Data', 'Valor'])
        
        # Criar colunas auxiliares
        self.df['Mes'] = self.df['Data'].dt.to_period('M')
        self.df['Semana'] = self.df['Data'].dt.isocalendar().week
        self.df['Dia_Semana'] = self.df['Data'].dt.day_name()
        self.df['Mes_Str'] = self.df['Data'].dt.strftime('%Y-%m')
        
        # Separar receitas e despesas
        self.receitas = self.df[self.df['Tipo'] == 'Receita']
        self.despesas = self.df[self.df['Tipo'] == 'Despesa']
        
        print(f"✅ Dados preparados: {len(self.df)} transações")
        print(f"   • Receitas: {len(self.receitas)}")
        print(f"   • Despesas: {len(self.despesas)}")
    
    def generate_monthly_insights(self) -> Dict:
        """Gera insights mensais"""
        insights = {}
        
        if self.df.empty:
            return insights
        
        print("📈 Gerando insights mensais...")
        
        # Análise mensal
        monthly_data = self.df.groupby(['Mes_Str', 'Tipo'])['Valor_Absoluto'].sum().unstack(fill_value=0)
        
        if not monthly_data.empty:
            if 'Receita' in monthly_data.columns and 'Despesa' in monthly_data.columns:
                monthly_data['Saldo'] = monthly_data['Receita'] - monthly_data['Despesa']
                monthly_data['Taxa_Poupanca'] = (monthly_data['Saldo'] / monthly_data['Receita'] * 100).fillna(0)
                
                # Estatísticas
                insights['media_receitas'] = monthly_data['Receita'].mean()
                insights['media_despesas'] = monthly_data['Despesa'].mean()
                insights['media_saldo'] = monthly_data['Saldo'].mean()
                insights['taxa_poupanca_media'] = monthly_data['Taxa_Poupanca'].mean()
                
                # Para dados Nubank, calcular insights específicos
                if self.is_nubank_data:
                    insights['gasto_medio_cartao'] = monthly_data['Despesa'].mean()
                    insights['maior_gasto_mensal'] = monthly_data['Despesa'].max()
                    insights['menor_gasto_mensal'] = monthly_data['Despesa'].min()
                    
                    # Variação de gastos no cartão
                    if len(monthly_data) > 1:
                        insights['variacao_gastos_cartao'] = monthly_data['Despesa'].pct_change().mean() * 100
                
                # Tendências
                if len(monthly_data) >= 2:
                    insights['tendencia_receitas'] = self._calculate_trend(monthly_data['Receita'])
                    insights['tendencia_despesas'] = self._calculate_trend(monthly_data['Despesa'])
                    insights['tendencia_saldo'] = self._calculate_trend(monthly_data['Saldo'])
                
                # Melhor e pior mês
                insights['melhor_mes'] = {
                    'periodo': str(monthly_data['Saldo'].idxmax()),
                    'saldo': monthly_data['Saldo'].max()
                }
                insights['pior_mes'] = {
                    'periodo': str(monthly_data['Saldo'].idxmin()),
                    'saldo': monthly_data['Saldo'].min()
                }
            
            elif 'Despesa' in monthly_data.columns:
                # Só despesas (caso comum no Nubank)
                insights['media_despesas'] = monthly_data['Despesa'].mean()
                insights['maior_gasto_mensal'] = monthly_data['Despesa'].max()
                insights['menor_gasto_mensal'] = monthly_data['Despesa'].min()
                
                if len(monthly_data) >= 2:
                    insights['tendencia_despesas'] = self._calculate_trend(monthly_data['Despesa'])
                
                insights['mes_maior_gasto'] = {
                    'periodo': str(monthly_data['Despesa'].idxmax()),
                    'valor': monthly_data['Despesa'].max()
                }
                insights['mes_menor_gasto'] = {
                    'periodo': str(monthly_data['Despesa'].idxmin()),
                    'valor': monthly_data['Despesa'].min()
                }
        
        return insights
    
    def _calculate_trend(self, series: pd.Series) -> Dict:
        """Calcula tendência de uma série temporal"""
        if len(series) < 2:
            return {'direction': 'stable', 'change': 0}
        
        # Regressão linear simples
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        
        # Porcentagem de mudança
        change_pct = (series.iloc[-1] - series.iloc[0]) / abs(series.iloc[0]) * 100 if series.iloc[0] != 0 else 0
        
        if slope > 0:
            direction = 'increasing'
        elif slope < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change': change_pct,
            'slope': slope
        }
    
    def detect_anomalies(self) -> List[FinancialAlert]:
        """Detecta anomalias nos gastos - otimizado para Nubank"""
        alerts = []
        
        if self.despesas.empty:
            return alerts
        
        print("🚨 Detectando anomalias...")
        
        # 1. Gastos muito acima da média mensal
        monthly_expenses = self.despesas.groupby('Mes_Str')['Valor_Absoluto'].sum()
        if len(monthly_expenses) >= 3:
            mean_expense = monthly_expenses.mean()
            std_expense = monthly_expenses.std()
            
            for month, expense in monthly_expenses.items():
                if expense > mean_expense + (self.alert_thresholds['expense_spike'] * std_expense):
                    alerts.append(FinancialAlert(
                        type='expense_spike',
                        severity='high',
                        title='Gasto Elevado Detectado' if not self.is_nubank_data else 'Gasto Elevado no Cartão',
                        message=f'Gastos em {month} foram {((expense/mean_expense-1)*100):.1f}% acima da média',
                        value=expense,
                        date=pd.to_datetime(month)
                    ))
        
        # 2. Transações incomuns por valor (específico para Nubank)
        if self.is_nubank_data:
            # Detectar compras muito grandes no cartão
            large_threshold = self.despesas['Valor_Absoluto'].quantile(0.95)
            large_transactions = self.despesas[self.despesas['Valor_Absoluto'] > large_threshold]
            
            for idx, row in large_transactions.iterrows():
                alerts.append(FinancialAlert(
                    type='large_transaction',
                    severity='medium',
                    title='Compra Grande no Cartão',
                    message=f'Compra de R$ {row["Valor_Absoluto"]:.2f} em {row["Descrição"][:30]} está entre os 5% maiores gastos',
                    value=row['Valor_Absoluto'],
                    category=row.get('Categoria', 'Outros'),
                    date=row['Data']
                ))
        
        # 3. Categorias com gastos excessivos
        if 'Categoria' in self.despesas.columns:
            total_despesas = self.despesas['Valor_Absoluto'].sum()
            category_spending = self.despesas.groupby('Categoria')['Valor_Absoluto'].sum()
            
            for categoria, valor in category_spending.items():
                percentage = valor / total_despesas
                if percentage > self.alert_thresholds['category_limit']:
                    alerts.append(FinancialAlert(
                        type='category_overspending',
                        severity='medium',
                        title='Categoria com Gastos Elevados',
                        message=f'{categoria} representa {percentage*100:.1f}% dos gastos totais',
                        value=valor,
                        category=categoria
                    ))
        
        # 4. Taxa de poupança baixa ou déficit (se houver receitas)
        if not self.receitas.empty:
            monthly_data = self.df.groupby(['Mes_Str', 'Tipo'])['Valor_Absoluto'].sum().unstack(fill_value=0)
            if 'Receita' in monthly_data.columns and 'Despesa' in monthly_data.columns:
                monthly_data['Taxa_Poupanca'] = (monthly_data['Receita'] - monthly_data['Despesa']) / monthly_data['Receita'] * 100
                
                low_savings_months = monthly_data[monthly_data['Taxa_Poupanca'] < self.alert_thresholds['low_savings_rate']]
                
                for month, row in low_savings_months.iterrows():
                    if row['Taxa_Poupanca'] < 0:
                        severity = 'critical'
                        title = 'Déficit Financeiro'
                        message = f'Déficit de {abs(row["Taxa_Poupanca"]):.1f}% em {month}'
                    else:
                        severity = 'medium'
                        title = 'Taxa de Poupança Baixa'
                        message = f'Taxa de poupança de apenas {row["Taxa_Poupanca"]:.1f}% em {month}'
                    
                    alerts.append(FinancialAlert(
                        type='low_savings',
                        severity=severity,
                        title=title,
                        message=message,
                        value=row['Taxa_Poupanca'],
                        date=pd.to_datetime(month)
                    ))
        
        # 5. Análise específica para Nubank - estabelecimentos com gastos crescentes
        if self.is_nubank_data and len(self.despesas) > 20:
            establishment_monthly = self.despesas.groupby(['Descrição', 'Mes_Str'])['Valor_Absoluto'].sum().unstack(fill_value=0)
            
            for establishment in establishment_monthly.index:
                monthly_values = establishment_monthly.loc[establishment]
                non_zero_months = monthly_values[monthly_values > 0]
                
                if len(non_zero_months) >= 3:
                    # Verificar tendência crescente
                    trend = self._calculate_trend(non_zero_months)
                    if trend['direction'] == 'increasing' and trend['change'] > 50:
                        alerts.append(FinancialAlert(
                            type='establishment_growth',
                            severity='low',
                            title='Gasto Crescente em Estabelecimento',
                            message=f'Gastos em {establishment[:30]} aumentaram {trend["change"]:.1f}%',
                            value=trend['change'],
                            category='Estabelecimento'
                        ))
        
        return alerts
    
    def analyze_spending_patterns_nubank(self) -> Dict:
        """Analisa padrões de gasto específicos para Nubank"""
        patterns = {}
        
        if self.despesas.empty:
            return patterns
        
        print("🔍 Analisando padrões de gasto...")
        
        # 1. Análise por dia da semana (específica para cartão)
        weekday_spending = self.despesas.groupby('Dia_Semana')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
        patterns['por_dia_semana'] = {
            'maior_gasto': weekday_spending['sum'].idxmax(),
            'maior_valor': weekday_spending['sum'].max(),
            'menor_gasto': weekday_spending['sum'].idxmin(),
            'menor_valor': weekday_spending['sum'].min(),
            'detalhes': weekday_spending.to_dict()
        }
        
        # 2. Análise por categoria
        if 'Categoria' in self.despesas.columns:
            category_analysis = self.despesas.groupby('Categoria')['Valor_Absoluto'].agg(['sum', 'mean', 'count', 'std'])
            category_analysis['cv'] = category_analysis['std'] / category_analysis['mean']  # Coeficiente de variação
            
            patterns['por_categoria'] = {
                'mais_gasta': category_analysis['sum'].idxmax(),
                'valor_mais_gasta': category_analysis['sum'].max(),
                'mais_frequente': category_analysis['count'].idxmax(),
                'freq_mais_frequente': category_analysis['count'].max(),
                'mais_variavel': category_analysis['cv'].idxmax(),
                'cv_mais_variavel': category_analysis['cv'].max(),
                'detalhes': category_analysis.to_dict()
            }
        
        # 3. Análise de estabelecimentos (específica para Nubank)
        if self.is_nubank_data:
            establishment_analysis = self.despesas.groupby('Descrição')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
            establishment_analysis = establishment_analysis.sort_values('count', ascending=False)
            
            patterns['estabelecimentos'] = {
                'mais_frequente': establishment_analysis.index[0] if len(establishment_analysis) > 0 else 'N/A',
                'freq_mais_frequente': establishment_analysis['count'].iloc[0] if len(establishment_analysis) > 0 else 0,
                'maior_gasto_total': establishment_analysis['sum'].idxmax() if len(establishment_analysis) > 0 else 'N/A',
                'valor_maior_gasto': establishment_analysis['sum'].max() if len(establishment_analysis) > 0 else 0,
                'top_10_frequentes': establishment_analysis.head(10).to_dict() if len(establishment_analysis) > 0 else {}
            }
        
        # 4. Sazonalidade mensal
        monthly_spending = self.despesas.groupby(self.despesas['Data'].dt.month)['Valor_Absoluto'].sum()
        patterns['sazonalidade'] = {
            'mes_mais_caro': monthly_spending.idxmax(),
            'valor_mes_mais_caro': monthly_spending.max(),
            'mes_mais_barato': monthly_spending.idxmin(),
            'valor_mes_mais_barato': monthly_spending.min(),
            'detalhes': monthly_spending.to_dict()
        }
        
        # 5. Análise de custos fixos vs variáveis (se disponível)
        if 'Custo_Tipo' in self.despesas.columns:
            fixed_var_analysis = self.despesas.groupby('Custo_Tipo')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
            patterns['fixos_vs_variaveis'] = fixed_var_analysis.to_dict()
        
        return patterns
    
    def generate_predictions(self) -> Dict:
        """Gera previsões financeiras"""
        predictions = {}
        
        print("🔮 Gerando previsões...")
        
        # Previsão de gastos mensais
        monthly_expenses = self.despesas.groupby('Mes_Str')['Valor_Absoluto'].sum()
        
        if len(monthly_expenses) >= 3:
            # Média móvel simples
            predictions['proximo_mes_media'] = monthly_expenses.rolling(3).mean().iloc[-1]
            
            # Tendência linear
            x = np.arange(len(monthly_expenses))
            slope, intercept = np.polyfit(x, monthly_expenses.values, 1)
            predictions['proximo_mes_tendencia'] = slope * len(monthly_expenses) + intercept
            
            # Previsão sazonal (baseado no mesmo mês do ano anterior)
            current_month = pd.to_datetime(monthly_expenses.index[-1]).month
            same_month_previous = monthly_expenses[pd.to_datetime(monthly_expenses.index).month == current_month]
            if len(same_month_previous) > 1:
                predictions['proximo_mes_sazonal'] = same_month_previous.mean()
        
        # Previsão por categoria
        category_predictions = {}
        if 'Categoria' in self.despesas.columns:
            for categoria in self.despesas['Categoria'].unique():
                cat_monthly = self.despesas[self.despesas['Categoria'] == categoria].groupby('Mes_Str')['Valor_Absoluto'].sum()
                if len(cat_monthly) >= 3:
                    category_predictions[categoria] = cat_monthly.rolling(3).mean().iloc[-1]
        
        predictions['por_categoria'] = category_predictions
        
        # Previsões específicas para Nubank
        if self.is_nubank_data:
            # Previsão de gastos por estabelecimento frequente
            top_establishments = self.despesas['Descrição'].value_counts().head(5).index
            establishment_predictions = {}
            
            for establishment in top_establishments:
                est_monthly = self.despesas[self.despesas['Descrição'] == establishment].groupby('Mes_Str')['Valor_Absoluto'].sum()
                if len(est_monthly) >= 2:
                    establishment_predictions[establishment] = est_monthly.mean()
            
            predictions['estabelecimentos_frequentes'] = establishment_predictions
        
        return predictions
    
    def calculate_financial_health_score(self) -> Dict:
        """Calcula score de saúde financeira - adaptado para Nubank"""
        score_components = {}
        total_score = 0
        max_score = 0
        
        if self.df.empty:
            return {'score': 0, 'components': {}}
        
        print("🏥 Calculando score de saúde financeira...")
        
        # 1. Taxa de Poupança (30 pontos) - ou Controle de Gastos para Nubank
        if not self.receitas.empty:
            # Com receitas - calcular taxa de poupança tradicional
            monthly_data = self.df.groupby(['Mes_Str', 'Tipo'])['Valor_Absoluto'].sum().unstack(fill_value=0)
            if 'Receita' in monthly_data.columns and 'Despesa' in monthly_data.columns:
                savings_rate = ((monthly_data['Receita'] - monthly_data['Despesa']) / monthly_data['Receita'] * 100).mean()
                
                if savings_rate >= 20:
                    savings_score = 30
                elif savings_rate >= 10:
                    savings_score = 20
                elif savings_rate >= 0:
                    savings_score = 10
                else:
                    savings_score = 0
                
                score_components['taxa_poupanca'] = {
                    'score': savings_score,
                    'max_score': 30,
                    'value': savings_rate,
                    'description': f'Taxa de poupança média: {savings_rate:.1f}%'
                }
        else:
            # Apenas despesas (Nubank) - calcular controle de gastos
            monthly_expenses = self.despesas.groupby('Mes_Str')['Valor_Absoluto'].sum()
            if len(monthly_expenses) >= 2:
                # Calcular variabilidade dos gastos (menor variabilidade = melhor controle)
                cv = monthly_expenses.std() / monthly_expenses.mean()
                
                if cv <= 0.15:
                    control_score = 30
                elif cv <= 0.25:
                    control_score = 20
                elif cv <= 0.35:
                    control_score = 15
                else:
                    control_score = 10
                
                score_components['controle_gastos'] = {
                    'score': control_score,
                    'max_score': 30,
                    'value': cv,
                    'description': f'Variabilidade dos gastos: {cv:.2f} (menor = melhor)'
                }
            else:
                control_score = 15  # Score neutro para poucos dados
                score_components['controle_gastos'] = {
                    'score': control_score,
                    'max_score': 30,
                    'value': 0,
                    'description': 'Poucos dados para análise'
                }
        
        total_score += score_components.get('taxa_poupanca', score_components.get('controle_gastos', {})).get('score', 0)
        max_score += 30
        
        # 2. Diversificação de Gastos (20 pontos)
        if 'Categoria' in self.despesas.columns:
            category_distribution = self.despesas.groupby('Categoria')['Valor_Absoluto'].sum()
            total_expenses = category_distribution.sum()
            category_percentages = category_distribution / total_expenses
            
            # Calcular índice de Gini (diversificação)
            sorted_percentages = np.sort(category_percentages.values)
            n = len(sorted_percentages)
            gini = (2 * np.arange(1, n + 1) - n - 1) @ sorted_percentages / (n * sorted_percentages.sum())
            
            # Converter Gini para score (Gini baixo = mais diversificado = melhor score)
            diversification_score = max(0, 20 * (1 - gini))
            
            score_components['diversificacao'] = {
                'score': diversification_score,
                'max_score': 20,
                'value': gini,
                'description': f'Índice de diversificação: {(1-gini)*100:.1f}%'
            }
            total_score += diversification_score
        max_score += 20
        
        # 3. Estabilidade de Gastos (25 pontos)
        monthly_expenses = self.despesas.groupby('Mes_Str')['Valor_Absoluto'].sum()
        if len(monthly_expenses) >= 3:
            cv = monthly_expenses.std() / monthly_expenses.mean()  # Coeficiente de variação
            
            if cv <= 0.1:
                stability_score = 25
            elif cv <= 0.2:
                stability_score = 20
            elif cv <= 0.3:
                stability_score = 15
            else:
                stability_score = 10
            
            score_components['estabilidade'] = {
                'score': stability_score,
                'max_score': 25,
                'value': cv,
                'description': f'Coeficiente de variação mensal: {cv:.2f}'
            }
            total_score += stability_score
        max_score += 25
        
        # 4. Controle de Gastos Grandes (25 pontos)
        large_transactions = self.despesas[self.despesas['Valor_Absoluto'] > self.despesas['Valor_Absoluto'].quantile(0.95)]
        large_transaction_ratio = len(large_transactions) / len(self.despesas)
        
        if large_transaction_ratio <= 0.02:
            control_score = 25
        elif large_transaction_ratio <= 0.05:
            control_score = 20
        elif large_transaction_ratio <= 0.10:
            control_score = 15
        else:
            control_score = 10
        
        score_components['controle_grandes_gastos'] = {
            'score': control_score,
            'max_score': 25,
            'value': large_transaction_ratio,
            'description': f'Transações grandes: {large_transaction_ratio*100:.1f}% do total'
        }
        total_score += control_score
        max_score += 25
        
        # Score final
        final_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'score': final_score,
            'components': score_components,
            'classification': self._classify_financial_health(final_score),
            'data_type': 'Nubank' if self.is_nubank_data else 'Tradicional'
        }
    
    def _classify_financial_health(self, score: float) -> str:
        """Classifica saúde financeira baseado no score"""
        if score >= 80:
            return 'Excelente'
        elif score >= 65:
            return 'Boa'
        elif score >= 50:
            return 'Regular'
        elif score >= 35:
            return 'Ruim'
        else:
            return 'Crítica'
    
    def generate_comprehensive_report(self) -> Dict:
        """Gera relatório completo"""
        print("📊 Gerando relatório completo...")
        
        report = {
            'timestamp': datetime.now(),
            'data_type': 'Nubank' if self.is_nubank_data else 'Tradicional',
            'period': {
                'start': self.df['Data'].min(),
                'end': self.df['Data'].max(),
                'total_days': (self.df['Data'].max() - self.df['Data'].min()).days
            },
            'summary': {
                'total_transactions': len(self.df),
                'total_income': self.receitas['Valor_Absoluto'].sum() if not self.receitas.empty else 0,
                'total_expenses': self.despesas['Valor_Absoluto'].sum() if not self.despesas.empty else 0,
                'net_balance': (self.receitas['Valor_Absoluto'].sum() if not self.receitas.empty else 0) - 
                              (self.despesas['Valor_Absoluto'].sum() if not self.despesas.empty else 0)
            },
            'insights': self.generate_monthly_insights(),
            'alerts': self.detect_anomalies(),
            'patterns': self.analyze_spending_patterns_nubank(),
            'predictions': self.generate_predictions(),
            'health_score': self.calculate_financial_health_score()
        }
        
        # Estatísticas específicas para Nubank
        if self.is_nubank_data:
            report['nubank_stats'] = {
                'unique_establishments': self.despesas['Descrição'].nunique() if not self.despesas.empty else 0,
                'most_frequent_establishment': self.despesas['Descrição'].mode().iloc[0] if not self.despesas.empty and not self.despesas['Descrição'].mode().empty else 'N/A',
                'average_transaction': self.despesas['Valor_Absoluto'].mean() if not self.despesas.empty else 0,
                'largest_transaction': self.despesas['Valor_Absoluto'].max() if not self.despesas.empty else 0,
                'transactions_per_month': len(self.despesas) / max(report['period']['total_days'] / 30, 1) if report['period']['total_days'] > 0 else 0
            }
        
        return report
    
    def export_report(self, report: Dict, format: str = 'json') -> str:
        """Exporta relatório em diferentes formatos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_suffix = 'nubank' if self.is_nubank_data else 'financeiro'
        
        if format == 'json':
            filename = f'relatorio_{data_suffix}_{timestamp}.json'
            
            # Converter objetos não serializáveis
            def convert_for_json(obj):
                if isinstance(obj, (datetime, pd.Timestamp)):
                    return obj.isoformat()
                elif isinstance(obj, np.int64):
                    return int(obj)
                elif isinstance(obj, np.float64):
                    return float(obj)
                elif isinstance(obj, FinancialAlert):
                    return {
                        'type': obj.type,
                        'severity': obj.severity,
                        'title': obj.title,
                        'message': obj.message,
                        'value': obj.value,
                        'category': obj.category,
                        'date': obj.date.isoformat() if obj.date else None
                    }
                return obj
            
            # Serializar recursivamente
            def deep_convert(obj):
                if isinstance(obj, dict):
                    return {k: deep_convert(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [deep_convert(item) for item in obj]
                else:
                    return convert_for_json(obj)
            
            serializable_report = deep_convert(report)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_report, f, ensure_ascii=False, indent=2)
        
        elif format == 'txt':
            filename = f'relatorio_{data_suffix}_{timestamp}.txt'
            
            with open(filename, 'w', encoding='utf-8') as f:
                data_type_name = "CARTÃO NUBANK" if self.is_nubank_data else "FINANCEIRO"
                f.write(f"RELATÓRIO {data_type_name} COMPLETO\n")
                f.write("=" * 60 + "\n\n")
                
                # Resumo
                f.write("RESUMO EXECUTIVO\n")
                f.write("-" * 20 + "\n")
                f.write(f"Tipo de dados: {report['data_type']}\n")
                f.write(f"Período: {report['period']['start'].strftime('%d/%m/%Y')} até {report['period']['end'].strftime('%d/%m/%Y')}\n")
                f.write(f"Total de transações: {report['summary']['total_transactions']:,}\n")
                
                if self.is_nubank_data:
                    f.write(f"Total gasto no cartão: R$ {report['summary']['total_expenses']:,.2f}\n")
                    if report['summary']['total_income'] > 0:
                        f.write(f"Receitas/Estornos: R$ {report['summary']['total_income']:,.2f}\n")
                    
                    # Stats específicos do Nubank
                    nubank_stats = report.get('nubank_stats', {})
                    f.write(f"Estabelecimentos únicos: {nubank_stats.get('unique_establishments', 0)}\n")
                    f.write(f"Estabelecimento mais frequente: {nubank_stats.get('most_frequent_establishment', 'N/A')}\n")
                    f.write(f"Gasto médio por transação: R$ {nubank_stats.get('average_transaction', 0):.2f}\n")
                    f.write(f"Maior gasto: R$ {nubank_stats.get('largest_transaction', 0):.2f}\n")
                else:
                    f.write(f"Receitas totais: R$ {report['summary']['total_income']:,.2f}\n")
                    f.write(f"Despesas totais: R$ {report['summary']['total_expenses']:,.2f}\n")
                    f.write(f"Saldo líquido: R$ {report['summary']['net_balance']:,.2f}\n")
                
                f.write("\n")
                
                # Score de saúde financeira
                health = report['health_score']
                f.write("SAÚDE FINANCEIRA\n")
                f.write("-" * 20 + "\n")
                f.write(f"Score: {health['score']:.1f}/100 - {health['classification']}\n")
                f.write(f"Tipo de análise: {health['data_type']}\n\n")
                
                # Alertas
                if report['alerts']:
                    f.write("ALERTAS IMPORTANTES\n")
                    f.write("-" * 20 + "\n")
                    for alert in report['alerts']:
                        f.write(f"[{alert.severity.upper()}] {alert.title}\n")
                        f.write(f"  {alert.message}\n\n")
                
                # Insights principais
                insights = report['insights']
                if insights:
                    f.write("INSIGHTS PRINCIPAIS\n")
                    f.write("-" * 20 + "\n")
                    if self.is_nubank_data:
                        f.write(f"Gasto médio mensal no cartão: R$ {insights.get('media_despesas', 0):,.2f}\n")
                        f.write(f"Maior gasto mensal: R$ {insights.get('maior_gasto_mensal', 0):,.2f}\n")
                        f.write(f"Menor gasto mensal: R$ {insights.get('menor_gasto_mensal', 0):,.2f}\n")
                    else:
                        f.write(f"Receita média mensal: R$ {insights.get('media_receitas', 0):,.2f}\n")
                        f.write(f"Despesa média mensal: R$ {insights.get('media_despesas', 0):,.2f}\n")
                        f.write(f"Taxa de poupança média: {insights.get('taxa_poupanca_media', 0):.1f}%\n")
                    
                    if 'melhor_mes' in insights:
                        f.write(f"Melhor mês: {insights['melhor_mes']['periodo']} (R$ {insights['melhor_mes']['saldo']:,.2f})\n")
                    if 'pior_mes' in insights:
                        f.write(f"Pior mês: {insights['pior_mes']['periodo']} (R$ {insights['pior_mes']['saldo']:,.2f})\n")
                
                # Padrões de gasto
                patterns = report['patterns']
                if 'estabelecimentos' in patterns and self.is_nubank_data:
                    f.write(f"\nESTABELECIMENTOS\n")
                    f.write(f"-" * 20 + "\n")
                    f.write(f"Mais frequente: {patterns['estabelecimentos']['mais_frequente']}\n")
                    f.write(f"Maior gasto total: {patterns['estabelecimentos']['maior_gasto_total']}\n")
                
                if 'por_categoria' in patterns:
                    f.write(f"\nCATEGORIAS\n")
                    f.write(f"-" * 20 + "\n")
                    f.write(f"Categoria mais gasta: {patterns['por_categoria']['mais_gasta']}\n")
                    f.write(f"Valor: R$ {patterns['por_categoria']['valor_mais_gasta']:,.2f}\n")
                
                # Previsões
                predictions = report['predictions']
                if 'proximo_mes_media' in predictions:
                    f.write(f"\nPREVISÕES\n")
                    f.write(f"-" * 20 + "\n")
                    f.write(f"Previsão próximo mês (média): R$ {predictions['proximo_mes_media']:,.2f}\n")
        
        print(f"✅ Relatório exportado: {filename}")
        return filename

def load_financial_data():
    """Carrega dados financeiros com prioridade para arquivos Nubank"""
    print("📁 Carregando dados financeiros...")
    
    # Priorizar arquivos Nubank
    csv_patterns = [
        "Nubank_*.csv",  # Prioritário
        "*.csv",
        "data/*.csv", 
        "data/raw/*.csv",
        "extratos/*.csv"
    ]
    
    all_files = []
    nubank_files = []
    
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
        if "Nubank_" in pattern:
            nubank_files.extend(files)
    
    # Remover duplicatas
    all_files = list(dict.fromkeys(all_files))
    
    if not all_files:
        print("❌ Nenhum arquivo CSV encontrado!")
        return pd.DataFrame()
    
    # Priorizar Nubank se disponível
    files_to_process = nubank_files if nubank_files else all_files
    is_nubank_priority = len(nubank_files) > 0
    
    print(f"📄 Processando {len(files_to_process)} arquivo(s)")
    if is_nubank_priority:
        print("💳 Dados Nubank detectados - análise otimizada")
    
    dfs = []
    for file in files_to_process:
        try:
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is not None:
                dfs.append(df)
                print(f"  ✅ {os.path.basename(file)}")
        except Exception as e:
            print(f"  ❌ {os.path.basename(file)}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"✅ {len(combined_df)} transações carregadas")
    
    return combined_df

def main():
    """Função principal"""
    print("📈 Sistema de Análise Avançada Financeira")
    print("💳 Otimizado para dados Nubank")
    print("=" * 60)
    
    # Carregar dados
    df = load_financial_data()
    if df.empty:
        print("❌ Nenhum dado encontrado!")
        print("💡 Coloque arquivos CSV na pasta atual ou data/raw/")
        return
    
    # Verificar formato
    is_nubank = all(col in df.columns for col in ['date', 'title', 'amount'])
    
    if is_nubank:
        print("💳 FORMATO NUBANK DETECTADO")
        print("   • Análise otimizada para cartão Nubank")
        print("   • Foco em padrões de gastos e estabelecimentos")
    else:
        print("🏦 FORMATO BANCÁRIO TRADICIONAL DETECTADO")
    
    # Inicializar analisador
    print("\n🔧 Inicializando análise...")
    try:
        analyzer = FinancialAnalyzer(df)
    except Exception as e:
        print(f"❌ Erro ao inicializar análise: {e}")
        return
    
    # Gerar relatório completo
    print("\n📊 Gerando análise completa...")
    report = analyzer.generate_comprehensive_report()
    
    # Mostrar resumo no terminal
    print("\n" + "="*80)
    print("RESUMO DA ANÁLISE")
    print("="*80)
    
    # Estatísticas básicas
    summary = report['summary']
    print(f"📅 Período: {report['period']['start'].strftime('%d/%m/%Y')} até {report['period']['end'].strftime('%d/%m/%Y')}")
    print(f"📊 Transações: {summary['total_transactions']:,}")
    print(f"📱 Tipo de dados: {report['data_type']}")
    
    if is_nubank:
        print(f"💳 Total gasto no cartão: R$ {summary['total_expenses']:,.2f}")
        if summary['total_income'] > 0:
            print(f"💰 Receitas/Estornos: R$ {summary['total_income']:,.2f}")
        
        # Stats específicos do Nubank
        nubank_stats = report.get('nubank_stats', {})
        print(f"🏪 Estabelecimentos únicos: {nubank_stats.get('unique_establishments', 0)}")
        print(f"📊 Gasto médio por compra: R$ {nubank_stats.get('average_transaction', 0):.2f}")
        print(f"💸 Maior compra: R$ {nubank_stats.get('largest_transaction', 0):.2f}")
    else:
        print(f"💰 Receitas: R$ {summary['total_income']:,.2f}")
        print(f"💸 Despesas: R$ {summary['total_expenses']:,.2f}")
        print(f"💵 Saldo: R$ {summary['net_balance']:,.2f}")
    
    # Score de saúde financeira
    health = report['health_score']
    print(f"\n🏥 SAÚDE FINANCEIRA: {health['score']:.1f}/100 - {health['classification']}")
    
    # Alertas críticos e importantes
    alerts_by_severity = {}
    for alert in report['alerts']:
        if alert.severity not in alerts_by_severity:
            alerts_by_severity[alert.severity] = []
        alerts_by_severity[alert.severity].append(alert)
    
    if 'critical' in alerts_by_severity:
        print(f"\n🚨 ALERTAS CRÍTICOS: {len(alerts_by_severity['critical'])}")
        for alert in alerts_by_severity['critical'][:3]:
            print(f"   • {alert.title}: {alert.message}")
    
    if 'high' in alerts_by_severity:
        print(f"\n⚠️ ALERTAS IMPORTANTES: {len(alerts_by_severity['high'])}")
        for alert in alerts_by_severity['high'][:3]:
            print(f"   • {alert.title}: {alert.message}")
    
    # Insights principais
    insights = report['insights']
    if insights:
        print(f"\n💡 INSIGHTS PRINCIPAIS:")
        if is_nubank:
            print(f"   • Gasto médio mensal no cartão: R$ {insights.get('media_despesas', 0):,.2f}")
            if 'tendencia_despesas' in insights:
                trend = insights['tendencia_despesas']
                trend_text = "crescendo" if trend['direction'] == 'increasing' else "diminuindo" if trend['direction'] == 'decreasing' else "estável"
                print(f"   • Tendência dos gastos: {trend_text} ({trend['change']:+.1f}%)")
        else:
            print(f"   • Taxa de poupança média: {insights.get('taxa_poupanca_media', 0):.1f}%")
            if 'melhor_mes' in insights:
                print(f"   • Melhor mês: {insights['melhor_mes']['periodo']} (R$ {insights['melhor_mes']['saldo']:,.2f})")
    
    # Padrões específicos
    patterns = report['patterns']
    if 'estabelecimentos' in patterns and is_nubank:
        est_patterns = patterns['estabelecimentos']
        print(f"\n🏪 ESTABELECIMENTOS:")
        print(f"   • Mais frequente: {est_patterns['mais_frequente']}")
        print(f"   • Maior gasto total: {est_patterns['maior_gasto_total']}")
    
    if 'por_categoria' in patterns:
        cat_patterns = patterns['por_categoria']
        print(f"\n🏷️ CATEGORIAS:")
        print(f"   • Mais gasta: {cat_patterns['mais_gasta']} (R$ {cat_patterns['valor_mais_gasta']:,.2f})")
        print(f"   • Mais frequente: {cat_patterns['mais_frequente']}")
    
    # Previsões
    predictions = report['predictions']
    if 'proximo_mes_media' in predictions:
        print(f"\n🔮 PREVISÃO PRÓXIMO MÊS: R$ {predictions['proximo_mes_media']:,.2f}")
    
    print("\n" + "="*80)
    
    # Opções de export
    print("\n💾 Opções de exportação:")
    print("1. JSON (completo)")
    print("2. TXT (resumo)")
    print("3. Ambos")
    print("4. Não exportar")
    
    choice = input("Escolha (1-4): ").strip()
    
    if choice in ['1', '3']:
        json_file = analyzer.export_report(report, 'json')
    if choice in ['2', '3']:
        txt_file = analyzer.export_report(report, 'txt')
    
    print("\n✅ Análise concluída!")
    
    # Sugestão de próximos passos
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    if is_nubank:
        print("   • Execute o dashboard para visualizar os dados: streamlit run dashboard.py")
        print("   • Use categorização automática: python src/llm_categorizer.py")
        print("   • Sincronize com Google Sheets: python src/google_sheets_sync.py")
    else:
        print("   • Execute o dashboard: streamlit run dashboard.py")
        print("   • Configure dados Nubank para análise mais detalhada")

if __name__ == "__main__":
    main()

# ===== UTILITÁRIOS PARA INTEGRAÇÃO =====

def quick_health_check(df: pd.DataFrame) -> float:
    """Verificação rápida de saúde financeira"""
    if df.empty:
        return 0
    
    try:
        analyzer = FinancialAnalyzer(df)
        health_score = analyzer.calculate_financial_health_score()
        return health_score['score']
    except Exception:
        return 0

def get_monthly_summary(df: pd.DataFrame) -> Dict:
    """Resumo mensal rápido"""
    if df.empty:
        return {}
    
    try:
        analyzer = FinancialAnalyzer(df)
        return analyzer.generate_monthly_insights()
    except Exception:
        return {}

def detect_spending_alerts(df: pd.DataFrame) -> List[FinancialAlert]:
    """Detecta apenas alertas de gastos"""
    if df.empty:
        return []
    
    try:
        analyzer = FinancialAnalyzer(df)
        return analyzer.detect_anomalies()
    except Exception:
        return []

def analyze_nubank_data(df: pd.DataFrame) -> Dict:
    """Análise específica para dados Nubank"""
    if df.empty:
        return {}
    
    # Verificar se é formato Nubank
    is_nubank = all(col in df.columns for col in ['date', 'title', 'amount'])
    
    if not is_nubank:
        return {'error': 'Não é formato Nubank'}
    
    try:
        analyzer = FinancialAnalyzer(df)
        return analyzer.generate_comprehensive_report()
    except Exception as e:
        return {'error': str(e)}

# Exemplo de uso em outros módulos:
"""
# Para usar em outros scripts:
from src.advanced_analytics import FinancialAnalyzer, quick_health_check, analyze_nubank_data

# Análise rápida
score = quick_health_check(df)
print(f"Score de saúde: {score:.1f}")

# Análise completa Nubank
nubank_report = analyze_nubank_data(df)
if 'error' not in nubank_report:
    print(f"Estabelecimentos únicos: {nubank_report['nubank_stats']['unique_establishments']}")

# Análise completa tradicional
analyzer = FinancialAnalyzer(df)
report = analyzer.generate_comprehensive_report()
analyzer.export_report(report, 'json')
"""