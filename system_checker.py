#!/usr/bin/env python3
"""
Sistema de Verificação do Dashboard Financeiro
Testa todos os componentes e gera relatório de status
Execute: python system_checker.py
"""

import os
import sys
import pandas as pd
import glob
from datetime import datetime
from pathlib import Path
import json

class SystemChecker:
    """Verificador completo do sistema Dashboard Financeiro"""
    
    def __init__(self):
        self.report = {
            'timestamp': datetime.now(),
            'status': 'INICIANDO',
            'tests': {},
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
    def log_test(self, test_name: str, status: str, message: str, details: dict = None):
        """Registra resultado de um teste"""
        self.report['tests'][test_name] = {
            'status': status,
            'message': message,
            'details': details or {}
        }
        
        if status == 'ERROR':
            self.report['errors'].append(f"{test_name}: {message}")
        elif status == 'WARNING':
            self.report['warnings'].append(f"{test_name}: {message}")
    
    def check_project_structure(self):
        """Verifica estrutura do projeto"""
        print("📁 Verificando estrutura do projeto...")
        
        required_structure = {
            'files': [
                'main.py',
                'dashboard.py',
                'requirements.txt',
                'README.md'
            ],
            'src_modules': [
                'src/llm_categorizer.py',
                'src/google_sheets_sync.py',
                'src/advanced_analytics.py',
                'src/__init__.py'
            ],
            'folders': [
                'src',
                'data/raw',
                'data/processed',
                'data/exports',
                'credentials',
                'css',
                'config'
            ],
            'optional_files': [
                '.env',
                '.gitignore',
                'css/dashboard_styles.css',
                'config.json'
            ]
        }
        
        structure_report = {
            'files_found': 0,
            'files_missing': [],
            'modules_found': 0,
            'modules_missing': [],
            'folders_found': 0,
            'folders_missing': []
        }
        
        # Verificar arquivos principais
        for file in required_structure['files']:
            if os.path.exists(file):
                structure_report['files_found'] += 1
            else:
                structure_report['files_missing'].append(file)
        
        # Verificar módulos src/
        for module in required_structure['src_modules']:
            if os.path.exists(module):
                structure_report['modules_found'] += 1
            else:
                structure_report['modules_missing'].append(module)
        
        # Verificar pastas
        for folder in required_structure['folders']:
            if os.path.exists(folder):
                structure_report['folders_found'] += 1
            else:
                structure_report['folders_missing'].append(folder)
        
        # Determinar status
        critical_missing = structure_report['files_missing'] + structure_report['modules_missing']
        
        if not critical_missing:
            status = 'SUCCESS'
            message = f"Estrutura completa: {structure_report['files_found']} arquivos, {structure_report['modules_found']} módulos"
        elif len(critical_missing) <= 2:
            status = 'WARNING'
            message = f"Estrutura quase completa - faltam: {', '.join(critical_missing[:2])}"
        else:
            status = 'ERROR'
            message = f"Estrutura incompleta - faltam {len(critical_missing)} arquivos críticos"
        
        self.log_test('project_structure', status, message, structure_report)
    
    def check_dependencies(self):
        """Verifica dependências Python"""
        print("📦 Verificando dependências...")
        
        required_deps = [
            'streamlit', 'pandas', 'plotly', 'numpy',
            'gspread', 'oauth2client', 'python-dotenv'
        ]
        
        optional_deps = [
            'langchain-openai', 'langchain-groq', 'langchain-core'
        ]
        
        deps_report = {
            'required_installed': [],
            'required_missing': [],
            'optional_installed': [],
            'optional_missing': []
        }
        
        # Verificar dependências obrigatórias
        for dep in required_deps:
            try:
                __import__(dep.replace('-', '_'))
                deps_report['required_installed'].append(dep)
            except ImportError:
                deps_report['required_missing'].append(dep)
        
        # Verificar dependências opcionais
        for dep in optional_deps:
            try:
                __import__(dep.replace('-', '_'))
                deps_report['optional_installed'].append(dep)
            except ImportError:
                deps_report['optional_missing'].append(dep)
        
        # Determinar status
        if not deps_report['required_missing']:
            status = 'SUCCESS'
            message = f"Todas as {len(deps_report['required_installed'])} dependências obrigatórias instaladas"
        elif len(deps_report['required_missing']) <= 2:
            status = 'WARNING'
            message = f"Faltam dependências: {', '.join(deps_report['required_missing'])}"
        else:
            status = 'ERROR'
            message = f"Muitas dependências faltando ({len(deps_report['required_missing'])})"
        
        self.log_test('dependencies', status, message, deps_report)
    
    def check_data_files(self):
        """Verifica arquivos de dados"""
        print("📊 Verificando arquivos de dados...")
        
        # Procurar CSVs
        csv_patterns = [
            "Nubank_*.csv",
            "*.csv",
            "data/raw/*.csv",
            "extratos/*.csv"
        ]
        
        data_report = {
            'nubank_files': [],
            'other_csv_files': [],
            'total_files': 0,
            'sample_analysis': {}
        }
        
        all_csvs = []
        for pattern in csv_patterns:
            files = glob.glob(pattern)
            all_csvs.extend(files)
        
        # Remover duplicatas
        all_csvs = list(set(all_csvs))
        data_report['total_files'] = len(all_csvs)
        
        # Separar arquivos Nubank
        for file in all_csvs:
            if 'Nubank_' in os.path.basename(file):
                data_report['nubank_files'].append(file)
            else:
                data_report['other_csv_files'].append(file)
        
        # Analisar arquivo de exemplo
        if all_csvs:
            try:
                sample_file = all_csvs[0]
                df = pd.read_csv(sample_file)
                
                data_report['sample_analysis'] = {
                    'file': os.path.basename(sample_file),
                    'rows': len(df),
                    'columns': list(df.columns),
                    'is_nubank_format': all(col in df.columns for col in ['date', 'title', 'amount'])
                }
                
                # Análise adicional se for Nubank
                if data_report['sample_analysis']['is_nubank_format']:
                    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                    total_transactions = len(df)
                    total_expenses = len(df[df['amount'] < 0])
                    total_income = len(df[df['amount'] > 0])
                    
                    data_report['sample_analysis'].update({
                        'total_transactions': total_transactions,
                        'expenses': total_expenses,
                        'income': total_income,
                        'date_range': {
                            'start': df['date'].min(),
                            'end': df['date'].max()
                        }
                    })
                
            except Exception as e:
                data_report['sample_analysis'] = {'error': str(e)}
        
        # Determinar status
        if data_report['total_files'] == 0:
            status = 'ERROR'
            message = "Nenhum arquivo CSV encontrado"
        elif data_report['nubank_files']:
            status = 'SUCCESS'
            message = f"Dados Nubank encontrados: {len(data_report['nubank_files'])} arquivos"
        else:
            status = 'WARNING'
            message = f"CSVs encontrados mas não são do Nubank: {data_report['total_files']} arquivos"
        
        self.log_test('data_files', status, message, data_report)
    
    def check_configuration(self):
        """Verifica configurações"""
        print("⚙️ Verificando configurações...")
        
        config_report = {
            'env_file': os.path.exists('.env'),
            'config_json': os.path.exists('config.json'),
            'google_credentials': os.path.exists('credentials/google_credentials.json'),
            'env_vars': {},
            'config_data': {}
        }
        
        # Verificar arquivo .env
        if config_report['env_file']:
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                    config_report['env_vars'] = {
                        'GROQ_API_KEY': 'GROQ_API_KEY=' in env_content,
                        'OPENAI_API_KEY': 'OPENAI_API_KEY=' in env_content,
                        'GOOGLE_CREDENTIALS_PATH': 'GOOGLE_CREDENTIALS_PATH=' in env_content
                    }
            except Exception as e:
                config_report['env_vars']['error'] = str(e)
        
        # Verificar config.json
        if config_report['config_json']:
            try:
                with open('config.json', 'r') as f:
                    config_data = json.load(f)
                    config_report['config_data'] = {
                        'first_run': config_data.get('first_run', True),
                        'google_sheets_configured': config_data.get('google_sheets_configured', False),
                        'llm_provider': config_data.get('llm_provider', 'local')
                    }
            except Exception as e:
                config_report['config_data']['error'] = str(e)
        
        # Determinar status
        issues = []
        if not config_report['env_file']:
            issues.append("arquivo .env")
        if not config_report['google_credentials']:
            issues.append("credenciais Google")
        
        if not issues:
            status = 'SUCCESS'
            message = "Configurações básicas presentes"
        elif len(issues) == 1:
            status = 'WARNING'  
            message = f"Falta: {issues[0]}"
        else:
            status = 'WARNING'
            message = f"Faltam: {', '.join(issues)}"
        
        self.log_test('configuration', status, message, config_report)
    
    def test_core_functionality(self):
        """Testa funcionalidades principais"""
        print("🧪 Testando funcionalidades principais...")
        
        func_report = {
            'data_loading': False,
            'data_processing': False,
            'categorization': False,
            'visualization': False
        }
        
        try:
            # Teste 1: Carregar dados
            csv_files = glob.glob("*.csv") + glob.glob("data/raw/*.csv") + glob.glob("Nubank_*.csv")
            if csv_files:
                test_file = csv_files[0]
                df = pd.read_csv(test_file)
                func_report['data_loading'] = len(df) > 0
            
            # Teste 2: Processamento básico
            if func_report['data_loading']:
                # Verificar se é formato Nubank
                is_nubank = all(col in df.columns for col in ['date', 'title', 'amount'])
                
                if is_nubank:
                    # Processamento Nubank
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                    processed_df = df.dropna(subset=['date', 'amount'])
                    func_report['data_processing'] = len(processed_df) > 0
                else:
                    # Processamento tradicional
                    func_report['data_processing'] = True
            
            # Teste 3: Categorização (se módulo existe)
            if os.path.exists('src/llm_categorizer.py'):
                sys.path.insert(0, 'src')
                try:
                    from llm_categorizer import FinancialCategorizer
                    categorizer = FinancialCategorizer(provider="local")
                    func_report['categorization'] = True
                except Exception:
                    func_report['categorization'] = False
            
            # Teste 4: Visualização (Plotly)
            try:
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(x=[1, 2, 3], y=[1, 2, 3]))
                func_report['visualization'] = True
            except Exception:
                func_report['visualization'] = False
                
        except Exception as e:
            func_report['error'] = str(e)
        
        # Determinar status
        working_functions = sum([v for v in func_report.values() if isinstance(v, bool) and v])
        total_functions = len([v for v in func_report.values() if isinstance(v, bool)])
        
        if working_functions == total_functions:
            status = 'SUCCESS'
            message = f"Todas as {total_functions} funcionalidades testadas funcionam"
        elif working_functions >= total_functions * 0.7:
            status = 'WARNING'
            message = f"{working_functions}/{total_functions} funcionalidades funcionando"
        else:
            status = 'ERROR'
            message = f"Apenas {working_functions}/{total_functions} funcionalidades funcionando"
        
        self.log_test('core_functionality', status, message, func_report)
    
    def check_nubank_data_detailed(self):
        """Análise detalhada dos dados Nubank"""
        print("💳 Analisando dados Nubank em detalhes...")
        
        nubank_files = glob.glob("Nubank_*.csv")
        
        if not nubank_files:
            self.log_test('nubank_analysis', 'WARNING', "Nenhum arquivo Nubank encontrado")
            return
        
        nubank_report = {
            'files_analyzed': [],
            'total_transactions': 0,
            'date_range': {},
            'amount_stats': {},
            'categories_sample': {},
            'establishments_sample': []
        }
        
        try:
            all_data = []
            
            for file in nubank_files:
                df = pd.read_csv(file)
                
                # Verificar formato
                if not all(col in df.columns for col in ['date', 'title', 'amount']):
                    continue
                
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                df = df.dropna(subset=['date', 'amount'])
                
                all_data.append(df)
                nubank_report['files_analyzed'].append({
                    'file': os.path.basename(file),
                    'transactions': len(df),
                    'date_range': {
                        'start': df['date'].min().strftime('%d/%m/%Y'),
                        'end': df['date'].max().strftime('%d/%m/%Y')
                    }
                })
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                nubank_report['total_transactions'] = len(combined_df)
                
                # Estatísticas de valores
                expenses = combined_df[combined_df['amount'] < 0]
                income = combined_df[combined_df['amount'] > 0]
                
                nubank_report['amount_stats'] = {
                    'total_expenses': abs(expenses['amount'].sum()) if not expenses.empty else 0,
                    'total_income': income['amount'].sum() if not income.empty else 0,
                    'avg_expense': abs(expenses['amount'].mean()) if not expenses.empty else 0,
                    'max_expense': abs(expenses['amount'].min()) if not expenses.empty else 0,
                    'expense_count': len(expenses),
                    'income_count': len(income)
                }
                
                # Range de datas
                nubank_report['date_range'] = {
                    'start': combined_df['date'].min().strftime('%d/%m/%Y'),
                    'end': combined_df['date'].max().strftime('%d/%m/%Y'),
                    'days': (combined_df['date'].max() - combined_df['date'].min()).days
                }
                
                # Amostra de estabelecimentos
                if not expenses.empty:
                    top_establishments = expenses['title'].value_counts().head(10)
                    nubank_report['establishments_sample'] = [
                        {'name': name, 'frequency': freq} 
                        for name, freq in top_establishments.items()
                    ]
                
                # Categorização básica de amostra
                sample_categories = {}
                for title in combined_df['title'].unique()[:20]:
                    title_lower = title.lower()
                    if any(term in title_lower for term in ['google', 'netflix', 'spotify']):
                        sample_categories[title] = 'Entretenimento'
                    elif any(term in title_lower for term in ['drogaria', 'farmacia']):
                        sample_categories[title] = 'Saúde'
                    elif any(term in title_lower for term in ['supermercado', 'mercado']):
                        sample_categories[title] = 'Mercado'
                    else:
                        sample_categories[title] = 'Outros'
                
                nubank_report['categories_sample'] = sample_categories
            
            status = 'SUCCESS'
            message = f"Análise completa: {len(nubank_files)} arquivos, {nubank_report['total_transactions']} transações"
            
        except Exception as e:
            status = 'ERROR'
            message = f"Erro na análise: {str(e)}"
            nubank_report['error'] = str(e)
        
        self.log_test('nubank_analysis', status, message, nubank_report)
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos testes"""
        print("💡 Gerando recomendações...")
        
        recommendations = []
        
        # Baseado na estrutura
        if 'project_structure' in self.report['tests']:
            structure = self.report['tests']['project_structure']
            if structure['details'].get('modules_missing'):
                recommendations.append(
                    "Mova os módulos para a pasta src/: " + 
                    ", ".join(structure['details']['modules_missing'])
                )
        
        # Baseado nas dependências
        if 'dependencies' in self.report['tests']:
            deps = self.report['tests']['dependencies']
            if deps['details'].get('required_missing'):
                recommendations.append(
                    "Instale dependências faltantes: pip install " + 
                    " ".join(deps['details']['required_missing'])
                )
        
        # Baseado nos dados
        if 'data_files' in self.report['tests']:
            data = self.report['tests']['data_files']
            if data['status'] == 'ERROR':
                recommendations.append(
                    "Adicione arquivos CSV do Nubank na pasta atual ou data/raw/"
                )
            elif not data['details'].get('nubank_files'):
                recommendations.append(
                    "Para melhor experiência, use extratos do Nubank no formato date,title,amount"
                )
        
        # Baseado nas configurações
        if 'configuration' in self.report['tests']:
            config = self.report['tests']['configuration']
            if not config['details'].get('google_credentials'):
                recommendations.append(
                    "Configure Google Sheets API para sincronização automática"
                )
            if not config['details'].get('env_file'):
                recommendations.append(
                    "Crie arquivo .env com suas chaves de API (GROQ_API_KEY, etc.)"
                )
        
        # Baseado na funcionalidade
        if 'core_functionality' in self.report['tests']:
            func = self.report['tests']['core_functionality']
            if not func['details'].get('categorization'):
                recommendations.append(
                    "Instale langchain-groq para categorização automática com IA"
                )
        
        # Baseado nos dados Nubank
        if 'nubank_analysis' in self.report['tests']:
            nubank = self.report['tests']['nubank_analysis']
            if nubank['status'] == 'SUCCESS':
                total = nubank['details'].get('total_transactions', 0)
                if total > 100:
                    recommendations.append(
                        f"Você tem {total} transações - ideal para análise automática com IA"
                    )
        
        self.report['recommendations'] = recommendations
    
    def run_all_checks(self):
        """Executa todas as verificações"""
        print("🚀 Iniciando verificação completa do sistema...")
        print("=" * 60)
        
        self.check_project_structure()
        self.check_dependencies()
        self.check_data_files()
        self.check_configuration()
        self.test_core_functionality()
        self.check_nubank_data_detailed()
        self.generate_recommendations()
        
        # Determinar status geral
        statuses = [test['status'] for test in self.report['tests'].values()]
        error_count = statuses.count('ERROR')
        warning_count = statuses.count('WARNING')
        success_count = statuses.count('SUCCESS')
        
        if error_count == 0 and warning_count == 0:
            self.report['status'] = 'EXCELLENT'
        elif error_count == 0:
            self.report['status'] = 'GOOD'
        elif error_count <= 2:
            self.report['status'] = 'NEEDS_ATTENTION'
        else:
            self.report['status'] = 'CRITICAL'
        
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL")
        print("=" * 60)
        
        return self.report
    
    def print_summary_report(self, report):
        """Imprime relatório resumido"""
        
        # Status geral
        status_colors = {
            'EXCELLENT': '🟢',
            'GOOD': '🟡', 
            'NEEDS_ATTENTION': '🟠',
            'CRITICAL': '🔴'
        }
        
        print(f"\n{status_colors.get(report['status'], '⚪')} **STATUS GERAL:** {report['status']}")
        
        # Resumo dos testes
        print(f"\n📊 **RESUMO DOS TESTES:**")
        for test_name, test_data in report['tests'].items():
            status_icon = {'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌'}.get(test_data['status'], '❓')
            print(f"   {status_icon} {test_name}: {test_data['message']}")
        
        # Erros críticos
        if report['errors']:
            print(f"\n❌ **ERROS CRÍTICOS:**")
            for error in report['errors']:
                print(f"   • {error}")
        
        # Avisos
        if report['warnings']:
            print(f"\n⚠️ **AVISOS:**")
            for warning in report['warnings']:
                print(f"   • {warning}")
        
        # Recomendações
        if report['recommendations']:
            print(f"\n💡 **RECOMENDAÇÕES:**")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        # Dados Nubank específicos
        if 'nubank_analysis' in report['tests'] and report['tests']['nubank_analysis']['status'] == 'SUCCESS':
            nubank_data = report['tests']['nubank_analysis']['details']
            print(f"\n💳 **RESUMO DADOS NUBANK:**")
            print(f"   • Arquivos: {len(nubank_data.get('files_analyzed', []))}")
            print(f"   • Transações: {nubank_data.get('total_transactions', 0):,}")
            
            amount_stats = nubank_data.get('amount_stats', {})
            if amount_stats:
                print(f"   • Total gasto: R$ {amount_stats.get('total_expenses', 0):,.2f}")
                print(f"   • Gasto médio: R$ {amount_stats.get('avg_expense', 0):,.2f}")
                print(f"   • Compras: {amount_stats.get('expense_count', 0):,}")
                
                if amount_stats.get('total_income', 0) > 0:
                    print(f"   • Receitas/Estornos: R$ {amount_stats.get('total_income', 0):,.2f}")
        
        print(f"\n🕐 **Relatório gerado em:** {report['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
    
    def save_detailed_report(self, report, filename="system_check_report.json"):
        """Salva relatório detalhado em JSON"""
        try:
            # Converter datetime para string para JSON
            report_copy = report.copy()
            report_copy['timestamp'] = report['timestamp'].isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_copy, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 **Relatório detalhado salvo:** {filename}")
            return True
        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")
            return False

def main():
    """Função principal"""
    print("🔍 VERIFICADOR DO SISTEMA DASHBOARD FINANCEIRO")
    print("💳 Especializado em dados Nubank")
    print("=" * 60)
    
    checker = SystemChecker()
    report = checker.run_all_checks()
    
    # Mostrar relatório
    checker.print_summary_report(report)
    
    # Salvar relatório detalhado
    checker.save_detailed_report(report)
    
    # Ações baseadas no status
    if report['status'] == 'EXCELLENT':
        print(f"\n🎉 **PARABÉNS!** Seu sistema está perfeito para uso!")
        print(f"🚀 Execute: python main.py para começar")
    elif report['status'] == 'GOOD':
        print(f"\n✨ **MUITO BOM!** Sistema funcional com pequenos ajustes opcionais")
        print(f"🚀 Execute: python main.py para começar")
    elif report['status'] == 'NEEDS_ATTENTION':
        print(f"\n🔧 **ATENÇÃO NECESSÁRIA** - Resolva os avisos para melhor experiência")
        print(f"💡 Siga as recomendações acima")
    else:
        print(f"\n🚨 **AÇÃO REQUERIDA** - Sistema precisa de correções antes do uso")
        print(f"❗ Resolva os erros críticos antes de prosseguir")
    
    return report

if __name__ == "__main__":
    main()

# ===== FUNÇÕES UTILITÁRIAS =====

def quick_check():
    """Verificação rápida - apenas status essencial"""
    print("⚡ VERIFICAÇÃO RÁPIDA")
    
    issues = []
    
    # Estrutura básica
    if not os.path.exists('main.py'):
        issues.append("main.py faltando")
    if not os.path.exists('dashboard.py'):
        issues.append("dashboard.py faltando")
    if not os.path.exists('src'):
        issues.append("pasta src/ faltando")
    
    # Dados
    csv_files = glob.glob("*.csv") + glob.glob("Nubank_*.csv") + glob.glob("data/raw/*.csv")
    if not csv_files:
        issues.append("nenhum CSV encontrado")
    
    # Dependências críticas
    try:
        import streamlit, pandas, plotly
    except ImportError as e:
        issues.append(f"dependência faltando: {e}")
    
    if not issues:
        print("✅ SISTEMA OK - Pronto para uso!")
        return True
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"   • {issue}")
        return False

def check_nubank_files_only():
    """Verifica apenas arquivos Nubank"""
    print("💳 VERIFICAÇÃO ESPECÍFICA - ARQUIVOS NUBANK")
    
    nubank_files = glob.glob("Nubank_*.csv")
    
    if not nubank_files:
        print("❌ Nenhum arquivo Nubank_*.csv encontrado")
        print("💡 Baixe extratos do Nubank e nomeie como Nubank_YYYYMMDD.csv")
        return False
    
    print(f"✅ {len(nubank_files)} arquivo(s) Nubank encontrado(s):")
    
    total_transactions = 0
    for file in nubank_files:
        try:
            df = pd.read_csv(file)
            if all(col in df.columns for col in ['date', 'title', 'amount']):
                print(f"   ✅ {os.path.basename(file)}: {len(df)} transações")
                total_transactions += len(df)
            else:
                print(f"   ❌ {os.path.basename(file)}: formato inválido")
        except Exception as e:
            print(f"   ❌ {os.path.basename(file)}: erro - {e}")
    
    print(f"\n📊 Total: {total_transactions:,} transações Nubank")
    return total_transactions > 0

# Para execução rápida:
# python system_checker.py quick -> quick_check()
# python system_checker.py nubank -> check_nubank_files_only()
if len(sys.argv) > 1:
    if sys.argv[1] == 'quick':
        quick_check()
    elif sys.argv[1] == 'nubank':
        check_nubank_files_only()
    else:
        main()
