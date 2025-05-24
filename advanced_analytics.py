"""
Sistema de Análise Avançada e Relatórios Financeiros
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
    """Analisador avançado de dados financeiros"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador
        
        Args:
            df: DataFrame com dados financeiros processados
        """
        self.df = df.copy()
        self.alerts = []
        self.insights = []
        
        # Configurações de análise
        self.alert_thresholds = {
            'expense_spike': 1.5,  # 50% acima da média
            'low_savings_rate': 10,  # Menos de 10% de poupança
            'category_limit': 0.3,  # Mais de 30% em uma categoria
            'unusual_transaction': 3,  # 3 desvios padrão
            'recurring_anomaly': 0.2  # 20% de variação em custos fixos
        }
        
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepara dados para análise"""
        if self.df.empty:
            return
        
        # Garantir que as colunas necessárias existem
        required_cols = ['Data', 'Valor', 'Categoria']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias faltando: {missing_cols}")
        
        # Processar datas e valores
        self.df['Data'] = pd.to_datetime(self.df['Data'])
        self.df['Valor'] = pd.to_numeric(self.df['Valor'], errors='coerce')
        self.df = self.df.dropna(subset=['Data', 'Valor'])
        
        # Criar colunas auxiliares
        self.df['Mes'] = self.df['Data'].dt.to_period('M')
        self.df['Semana'] = self.df['Data'].dt.isocalendar().week
        self.df['Dia_Semana'] = self.df['Data'].dt.day_name()
        self.df['Tipo'] = self.df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
        self.df['Valor_Absoluto'] = self.df['Valor'].abs()
        
        # Separar receitas e despesas
        self.receitas = self.df[self.df['Tipo'] == 'Receita']
        self.despesas = self.df[self.df['Tipo'] == 'Despesa']
        
        print(f"✅ Dados preparados: {len(self.df)} transações")
    
    def generate_monthly_insights(self) -> Dict:
        """Gera insights mensais"""
        insights = {}
        
        if self.df.empty:
            return insights
        
        # Análise mensal
        monthly_data = self.df.groupby(['Mes', 'Tipo'])['Valor_Absoluto'].sum().unstack(fill_value=0)
        
        if 'Receita' in monthly_data.columns and 'Despesa' in monthly_data.columns:
            monthly_data['Saldo'] = monthly_data['Receita'] - monthly_data['Despesa']
            monthly_data['Taxa_Poupanca'] = (monthly_data['Saldo'] / monthly_data['Receita'] * 100).fillna(0)
            
            # Estatísticas
            insights['media_receitas'] = monthly_data['Receita'].mean()
            insights['media_despesas'] = monthly_data['Despesa'].mean()
            insights['media_saldo'] = monthly_data['Saldo'].mean()
            insights['taxa_poupanca_media'] = monthly_data['Taxa_Poupanca'].mean()
            
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
        
        return insights
    
    def _calculate_trend(self, series: pd.Series) -> Dict:
        """Calcula tendência de uma série temporal"""
        if len(series) < 2:
            return {'direction': 'stable', 'change': 0}
        
        # Regressão linear simples
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        
        # Porcentagem de mudança
        change_pct = (series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100
        
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
        """Detecta anomalias nos gastos"""
        alerts = []
        
        if self.despesas.empty:
            return alerts
        
        # 1. Gastos muito acima da média
        monthly_expenses = self.despesas.groupby('Mes')['Valor_Absoluto'].sum()
        if len(monthly_expenses) >= 3:
            mean_expense = monthly_expenses.mean()
            std_expense = monthly_expenses.std()
            
            for month, expense in monthly_expenses.items():
                if expense > mean_expense + (self.alert_thresholds['expense_spike'] * std_expense):
                    alerts.append(FinancialAlert(
                        type='expense_spike',
                        severity='high',
                        title='Gasto Elevado Detectado',
                        message=f'Gastos em {month} foram {((expense/mean_expense-1)*100):.1f}% acima da média',
                        value=expense,
                        date=pd.to_datetime(str(month))
                    ))
        
        # 2. Transações incomuns por valor
        for categoria in self.despesas['Categoria'].unique():
            cat_data = self.despesas[self.despesas['Categoria'] == categoria]['Valor_Absoluto']
            
            if len(cat_data) >= 5:  # Só analisar categorias com dados suficientes
                mean_val = cat_data.mean()
                std_val = cat_data.std()
                
                outliers = cat_data[cat_data > mean_val + (self.alert_thresholds['unusual_transaction'] * std_val)]
                
                for idx, valor in outliers.items():
                    alerts.append(FinancialAlert(
                        type='unusual_transaction',
                        severity='medium',
                        title='Transação Incomum',
                        message=f'Gasto de R$ {valor:.2f} em {categoria} está muito acima do normal',
                        value=valor,
                        category=categoria,
                        date=self.df.loc[idx, 'Data']
                    ))
        
        # 3. Categorias com gastos excessivos
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
        
        # 4. Taxa de poupança baixa
        if not self.receitas.empty:
            monthly_data = self.df.groupby(['Mes', 'Tipo'])['Valor_Absoluto'].sum().unstack(fill_value=0)
            if 'Receita' in monthly_data.columns and 'Despesa' in monthly_data.columns:
                monthly_data['Taxa_Poupanca'] = (monthly_data['Receita'] - monthly_data['Despesa']) / monthly_data['Receita'] * 100
                
                low_savings_months = monthly_data[monthly_data['Taxa_Poupanca'] < self.alert_thresholds['low_savings_rate']]
                
                for month, row in low_savings_months.iterrows():
                    if row['Taxa_Poupanca'] < 0:
                        severity = 'critical'
                        title = 'Déficit Financeiro'
                        message = f'Deficit de {abs(row["Taxa_Poupanca"]):.1f}% em {month}'
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
                        date=pd.to_datetime(str(month))
                    ))
        
        return alerts
    
    def analyze_spending_patterns(self) -> Dict:
        """Analisa padrões de gasto"""
        patterns = {}
        
        if self.despesas.empty:
            return patterns
        
        # 1. Análise por dia da semana
        weekday_spending = self.despesas.groupby('Dia_Semana')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
        patterns['por_dia_semana'] = {
            'maior_gasto': weekday_spending['sum'].idxmax(),
            'maior_valor': weekday_spending['sum'].max(),
            'menor_gasto': weekday_spending['sum'].idxmin(),
            'menor_valor': weekday_spending['sum'].min(),
            'detalhes': weekday_spending.to_dict()
        }
        
        # 2. Análise por categoria
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
        
        # 3. Sazonalidade mensal
        monthly_spending = self.despesas.groupby(self.despesas['Data'].dt.month)['Valor_Absoluto'].sum()
        patterns['sazonalidade'] = {
            'mes_mais_caro': monthly_spending.idxmax(),
            'valor_mes_mais_caro': monthly_spending.max(),
            'mes_mais_barato': monthly_spending.idxmin(),
            'valor_mes_mais_barato': monthly_spending.min(),
            'detalhes': monthly_spending.to_dict()
        }
        
        # 4. Análise de custos fixos vs variáveis (se disponível)
        if 'Custo_Tipo' in self.despesas.columns:
            fixed_var_analysis = self.despesas.groupby('Custo_Tipo')['Valor_Absoluto'].agg(['sum', 'mean', 'count'])
            patterns['fixos_vs_variaveis'] = fixed_var_analysis.to_dict()
        
        return patterns
    
    def generate_predictions(self) -> Dict:
        """Gera previsões financeiras"""
        predictions = {}
        
        # Previsão de gastos mensais
        monthly_expenses = self.despesas.groupby('Mes')['Valor_Absoluto'].sum()
        
        if len(monthly_expenses) >= 3:
            # Média móvel simples
            predictions['proximo_mes_media'] = monthly_expenses.rolling(3).mean().iloc[-1]
            
            # Tendência linear
            x = np.arange(len(monthly_expenses))
            slope, intercept = np.polyfit(x, monthly_expenses.values, 1)
            predictions['proximo_mes_tendencia'] = slope * len(monthly_expenses) + intercept
            
            # Previsão sazonal (baseado no mesmo mês do ano anterior)
            current_month = monthly_expenses.index[-1].month
            same_month_last_year = monthly_expenses[monthly_expenses.index.month == current_month]
            if len(same_month_last_year) > 1:
                predictions['proximo_mes_sazonal'] = same_month_last_year.mean()
        
        # Previsão por categoria
        category_predictions = {}
        for categoria in self.despesas['Categoria'].unique():
            cat_monthly = self.despesas[self.despesas['Categoria'] == categoria].groupby('Mes')['Valor_Absoluto'].sum()
            if len(cat_monthly) >= 3:
                category_predictions[categoria] = cat_monthly.rolling(3).mean().iloc[-1]
        
        predictions['por_categoria'] = category_predictions
        
        return predictions
    
    def calculate_financial_health_score(self) -> Dict:
        """Calcula score de saúde financeira"""
        score_components = {}
        total_score = 0
        max_score = 0
        
        if self.df.empty:
            return {'score': 0, 'components': {}}
        
        # 1. Taxa de Poupança (30 pontos)
        monthly_data = self.df.groupby(['Mes', 'Tipo'])['Valor_Absoluto'].sum().unstack(fill_value=0)
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
            total_score += savings_score
        max_score += 30
        
        # 2. Diversificação de Gastos (20 pontos)
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
        monthly_expenses = self.despesas.groupby('Mes')['Valor_Absoluto'].sum()
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
                'description': f'Coeficiente de variação: {cv:.2f}'
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
        
        score_components['controle_gastos'] = {
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
            'classification': self._classify_financial_health(final_score)
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
            'patterns': self.analyze_spending_patterns(),
            'predictions': self.generate_predictions(),
            'health_score': self.calculate_financial_health_score()
        }
        
        return report
    
    def export_report(self, report: Dict, format: str = 'json') -> str:
        """Exporta relatório em diferentes formatos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f'relatorio_financeiro_{timestamp}.json'
            
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
            filename = f'relatorio_financeiro_{timestamp}.txt'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO FINANCEIRO COMPLETO\n")
                f.write("=" * 50 + "\n\n")
                
                # Resumo
                f.write("RESUMO EXECUTIVO\n")
                f.write("-" * 20 + "\n")
                f.write(f"Período: {report['period']['start'].strftime('%d/%m/%Y')} até {report['period']['end'].strftime('%d/%m/%Y')}\n")
                f.write(f"Total de transações: {report['summary']['total_transactions']:,}\n")
                f.write(f"Receitas totais: R$ {report['summary']['total_income']:,.2f}\n")
                f.write(f"Despesas totais: R$ {report['summary']['total_expenses']:,.2f}\n")
                f.write(f"Saldo líquido: R$ {report['summary']['net_balance']:,.2f}\n\n")
                
                # Score de saúde financeira
                health = report['health_score']
                f.write("SAÚDE FINANCEIRA\n")
                f.write("-" * 20 + "\n")
                f.write(f"Score: {health['score']:.1f}/100 - {health['classification']}\n\n")
                
                # Alertas
                if report['alerts']:
                    f.write("ALERTAS\n")
                    f.write("-" * 20 + "\n")
                    for alert in report['alerts']:
                        f.write(f"[{alert.severity.upper()}] {alert.title}\n")
                        f.write(f"  {alert.message}\n\n")
                
                # Insights principais
                insights = report['insights']
                if insights:
                    f.write("INSIGHTS PRINCIPAIS\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Receita média mensal: R$ {insights.get('media_receitas', 0):,.2f}\n")
                    f.write(f"Despesa média mensal: R$ {insights.get('media_despesas', 0):,.2f}\n")
                    f.write(f"Taxa de poupança média: {insights.get('taxa_poupanca_media', 0):.1f}%\n")
        
        print(f"✅ Relatório exportado: {filename}")
        return filename

def main():
    """Função principal"""
    print("📈 Sistema de Análise Avançada Financeira")
    print("=" * 50)
    
    # Carregar dados (usando a mesma função do categorizador)
    from llm_categorizer import load_financial_data
    
    df = load_financial_data()
    if df.empty:
        print("❌ Nenhum dado encontrado!")
        return
    
    # Inicializar analisador
    print("\n🔧 Inicializando análise...")
    analyzer = FinancialAnalyzer(df)
    
    # Gerar relatório completo
    print("\n📊 Gerando análise completa...")
    report = analyzer.generate_comprehensive_report()
    
    # Mostrar resumo no terminal
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE")
    print("="*60)
    
    # Estatísticas básicas
    summary = report['summary']
    print(f"📅 Período: {report['period']['start'].strftime('%d/%m/%Y')} até {report['period']['end'].strftime('%d/%m/%Y')}")
    print(f"📊 Transações: {summary['total_transactions']:,}")
    print(f"💰 Receitas: R$ {summary['total_income']:,.2f}")
    print(f"💸 Despesas: R$ {summary['total_expenses']:,.2f}")
    print(f"💵 Saldo: R$ {summary['net_balance']:,.2f}")
    
    # Score de saúde financeira
    health = report['health_score']
    print(f"\n🏥 SAÚDE FINANCEIRA: {health['score']:.1f}/100 - {health['classification']}")
    
    # Alertas críticos
    critical_alerts = [alert for alert in report['alerts'] if alert.severity == 'critical']
    if critical_alerts:
        print(f"\n🚨 ALERTAS CRÍTICOS: {len(critical_alerts)}")
        for alert in critical_alerts[:3]:  # Mostrar apenas os 3 primeiros
            print(f"   • {alert.title}: {alert.message}")
    
    # Insights principais
    insights = report['insights']
    if insights:
        print(f"\n💡 INSIGHTS PRINCIPAIS:")
        print(f"   • Taxa de poupança média: {insights.get('taxa_poupanca_media', 0):.1f}%")
        if 'melhor_mes' in insights:
            print(f"   • Melhor mês: {insights['melhor_mes']['periodo']} (R$ {insights['melhor_mes']['saldo']:,.2f})")
        if 'pior_mes' in insights:
            print(f"   • Pior mês: {insights['pior_mes']['periodo']} (R$ {insights['pior_mes']['saldo']:,.2f})")
    
    # Padrões de gasto
    patterns = report['patterns']
    if 'por_categoria' in patterns:
        print(f"\n🏷️ CATEGORIA MAIS GASTA: {patterns['por_categoria']['mais_gasta']}")
        print(f"   Valor: R$ {patterns['por_categoria']['valor_mais_gasta']:,.2f}")
    
    # Previsões
    predictions = report['predictions']
    if 'proximo_mes_media' in predictions:
        print(f"\n🔮 PREVISÃO PRÓXIMO MÊS: R$ {predictions['proximo_mes_media']:,.2f}")
    
    print("\n" + "="*60)
    
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

if __name__ == "__main__":
    main()

# ===== UTILITÁRIOS PARA INTEGRAÇÃO =====

def quick_health_check(df: pd.DataFrame) -> float:
    """Verificação rápida de saúde financeira"""
    if df.empty:
        return 0
    
    analyzer = FinancialAnalyzer(df)
    health_score = analyzer.calculate_financial_health_score()
    return health_score['score']

def get_monthly_summary(df: pd.DataFrame) -> Dict:
    """Resumo mensal rápido"""
    if df.empty:
        return {}
    
    analyzer = FinancialAnalyzer(df)
    return analyzer.generate_monthly_insights()

def detect_spending_alerts(df: pd.DataFrame) -> List[FinancialAlert]:
    """Detecta apenas alertas de gastos"""
    if df.empty:
        return []
    
    analyzer = FinancialAnalyzer(df)
    return analyzer.detect_anomalies()

# Exemplo de uso em outros módulos:
"""
from advanced_analytics import FinancialAnalyzer, quick_health_check

# Análise rápida
score = quick_health_check(df)
print(f"Score de saúde: {score:.1f}")

# Análise completa
analyzer = FinancialAnalyzer(df)
report = analyzer.generate_comprehensive_report()
analyzer.export_report(report, 'json')
"""