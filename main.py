#!/usr/bin/env python3
"""
Dashboard Financeiro Completo - Launcher Principal
Sistema completo de análise financeira pessoal

Execute: python main.py

Funcionalidades:
- Dashboard interativo
- Categorização automática com LLM
- Sincronização Google Sheets
- Análise avançada e relatórios
- Configuração automática
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar pasta src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ASCII Art para o header
LOGO = """
 $$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$\  $$\   $$\ $$$$$$\ $$\      $$\  $$$$$$\  
$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$ |  $$ |\_$$  _|$$$\    $$$ |$$  __$$\ 
$$ /  \__|$$ |  $$ |$$ /  $$ |$$ /  \__|$$ |  $$ |  $$ |  $$$$\  $$$$ |$$ /  $$ |
\$$$$$$\  $$$$$$$  |$$$$$$$$ |\$$$$$$\  $$$$$$$$ |  $$ |  $$\$$\$$ $$ |$$ |  $$ |
 \____$$\ $$  ____/ $$  __$$ | \____$$\ $$  __$$ |  $$ |  $$ \$$$  $$ |$$ |  $$ |
$$\   $$ |$$ |      $$ |  $$ |$$\   $$ |$$ |  $$ |  $$ |  $$ |\$  /$$ |$$ |  $$ |
\$$$$$$  |$$ |      $$ |  $$ |\$$$$$$  |$$ |  $$ |$$$$$$\ $$ | \_/ $$ | $$$$$$  |
 \______/ \__|      \__|  \__| \______/ \__|  \__|\______|\__|     \__| \______/ 
"""

class FinancialDashboardLauncher:
    """Launcher principal do sistema"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()
        self.data_stats = self.check_data_availability()
        
        # Caminhos dos módulos na estrutura src/
        self.modules = {
            'dashboard': 'dashboard.py',
            'categorizer': 'src/llm_categorizer.py',
            'sync': 'src/google_sheets_sync.py',
            'analytics': 'src/advanced_analytics.py'
        }
    
    def load_config(self) -> dict:
        """Carrega configuração do sistema"""
        default_config = {
            "first_run": True,
            "google_sheets_configured": False,
            "llm_provider": "groq",
            "data_folders": ["data/raw", "extratos", "."],
            "last_analysis": None,
            "user_preferences": {
                "default_action": "dashboard",
                "auto_categorize": True,
                "auto_sync": False
            },
            "project_structure": {
                "modules_in_src": True,
                "css_folder": "css",
                "config_folder": "config"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Mesclar com defaults para novos campos
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")
                return default_config
        
        return default_config
    
    def save_config(self):
        """Salva configuração"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar config: {e}")
    
    def check_data_availability(self) -> dict:
        """Verifica disponibilidade de dados"""
        stats = {
            "csv_files": 0,
            "total_transactions": 0,
            "date_range": None,
            "categories_available": False,
            "folders_checked": [],
            "modules_status": {}
        }
        
        # Verificar status dos módulos
        for module_name, module_path in self.modules.items():
            stats["modules_status"][module_name] = os.path.exists(module_path)
        
        # Procurar CSVs
        csv_files = []
        for folder in self.config["data_folders"]:
            if os.path.exists(folder):
                stats["folders_checked"].append(folder)
                folder_csvs = list(Path(folder).glob("*.csv"))
                csv_files.extend(folder_csvs)
        
        stats["csv_files"] = len(csv_files)
        
        if csv_files:
            try:
                # Tentar carregar um arquivo para estatísticas básicas
                sample_df = pd.read_csv(csv_files[0])
                if 'Data' in sample_df.columns:
                    sample_df['Data'] = pd.to_datetime(sample_df['Data'], errors='coerce')
                    stats["date_range"] = {
                        "start": sample_df['Data'].min(),
                        "end": sample_df['Data'].max()
                    }
                
                stats["total_transactions"] = len(sample_df)
                stats["categories_available"] = 'Categoria' in sample_df.columns
                
            except Exception as e:
                print(f"⚠️ Erro ao analisar dados: {e}")
        
        return stats
    
    def show_welcome_screen(self):
        """Exibe tela de boas-vindas"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\033[96m" + LOGO + "\033[0m")
        print("\033[92m" + "="*80 + "\033[0m")
        print("\033[93m" + "         DASHBOARD FINANCEIRO PESSOAL COMPLETO".center(80) + "\033[0m")
        print("\033[94m" + "                    Estrutura Organizada src/".center(80) + "\033[0m")
        print("\033[92m" + "="*80 + "\033[0m")
        
        # Status do sistema
        print(f"\n📊 STATUS DO SISTEMA:")
        print(f"   • Arquivos CSV encontrados: {self.data_stats['csv_files']}")
        
        # Status dos módulos
        print(f"\n🔧 STATUS DOS MÓDULOS:")
        module_names = {
            'dashboard': '📊 Dashboard',
            'categorizer': '🤖 Categorizador', 
            'sync': '☁️ Google Sheets',
            'analytics': '📈 Analytics'
        }
        
        for module_key, status in self.data_stats["modules_status"].items():
            module_display = module_names.get(module_key, module_key)
            status_icon = "✅" if status else "❌"
            print(f"   • {module_display}: {status_icon}")
        
        if self.data_stats['csv_files'] > 0:
            print(f"   • Transações estimadas: {self.data_stats['total_transactions']:,}")
            if self.data_stats['date_range']:
                start = self.data_stats['date_range']['start']
                end = self.data_stats['date_range']['end']
                if pd.notna(start) and pd.notna(end):
                    print(f"   • Período: {start.strftime('%d/%m/%Y')} até {end.strftime('%d/%m/%Y')}")
            print(f"   • Categorias: {'✅ Disponíveis' if self.data_stats['categories_available'] else '❌ Não categorizadas'}")
        
        # Status das integrações
        print(f"\n🔧 INTEGRAÇÕES:")
        print(f"   • Google Sheets: {'✅ Configurado' if self.config['google_sheets_configured'] else '❌ Não configurado'}")
        print(f"   • LLM para categorização: {'✅ ' + self.config['llm_provider'].upper() if self.config['llm_provider'] != 'local' else '❌ Apenas regras'}")
        
        # Estrutura do projeto
        print(f"\n📁 ESTRUTURA ORGANIZADA:")
        print(f"   • Módulos principais: src/")
        print(f"   • Dashboard: raiz do projeto")
        print(f"   • Configurações: {self.config.get('project_structure', {}).get('config_folder', 'config')}/")
        print(f"   • Estilos: {self.config.get('project_structure', {}).get('css_folder', 'css')}/")
        
        # Primeira execução
        if self.config["first_run"]:
            print(f"\n🎉 BEM-VINDO! Esta é sua primeira execução.")
            print(f"   Recomendamos começar pela configuração inicial.")
    
    def show_main_menu(self):
        """Exibe menu principal"""
        print(f"\n" + "="*60)
        print("MENU PRINCIPAL")
        print("="*60)
        
        options = [
            ("1", "🚀 Executar Dashboard Interativo", "dashboard", self.data_stats['csv_files'] > 0),
            ("2", "🤖 Categorizar Transações (LLM)", "categorize", self.data_stats['csv_files'] > 0 and self.data_stats["modules_status"].get('categorizer', False)),
            ("3", "☁️  Sincronizar Google Sheets", "sync", self.data_stats['csv_files'] > 0 and self.data_stats["modules_status"].get('sync', False)),
            ("4", "📈 Análise Avançada e Relatórios", "analyze", self.data_stats['csv_files'] > 0 and self.data_stats["modules_status"].get('analytics', False)),
            ("5", "⚙️  Configuração Inicial", "setup", True),
            ("6", "🔧 Configurações do Sistema", "config", True),
            ("7", "📁 Verificar Estrutura do Projeto", "structure", True),
            ("8", "ℹ️  Ajuda e Documentação", "help", True),
            ("9", "🔄 Atualizar Status dos Dados", "refresh", True),
            ("0", "❌ Sair", "exit", True)
        ]
        
        for num, title, action, enabled in options:
            if not enabled and action in ['categorize', 'sync', 'analyze']:
                status = " (❌ Módulo não encontrado em src/)"
            elif not enabled:
                status = " (❌ Sem dados)"
            else:
                status = ""
                
            color = "\033[92m" if enabled else "\033[91m"
            print(f"{color}{num}. {title}{status}\033[0m")
        
        print("="*60)
        
        while True:
            choice = input("\n📝 Escolha uma opção (0-9): ").strip()
            
            selected_option = next((opt for opt in options if opt[0] == choice), None)
            if selected_option:
                _, title, action, enabled = selected_option
                if enabled:
                    return action
                else:
                    if action in ['categorize', 'sync', 'analyze']:
                        print("❌ Este módulo não foi encontrado na pasta src/!")
                        print("💡 Verifique se os arquivos estão na pasta correta")
                    else:
                        print("❌ Esta opção requer dados CSV. Configure primeiro!")
            else:
                print("⚠️ Opção inválida! Digite um número de 0 a 9.")
    
    def execute_dashboard(self):
        """Executa dashboard principal"""
        print("\n🚀 Iniciando Dashboard Interativo...")
        
        dashboard_file = self.modules['dashboard']
        
        if not os.path.exists(dashboard_file):
            print(f"❌ Arquivo do dashboard não encontrado: {dashboard_file}")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_file])
        except Exception as e:
            print(f"❌ Erro ao executar dashboard: {e}")
            print("💡 Tente executar manualmente: streamlit run dashboard.py")
            input("Pressione Enter para continuar...")
    
    def execute_categorization(self):
        """Executa categorização automática"""
        print("\n🤖 Iniciando Categorização Automática...")
        
        categorizer_file = self.modules['categorizer']
        
        if not os.path.exists(categorizer_file):
            print(f"❌ Módulo de categorização não encontrado: {categorizer_file}")
            print("💡 Verifique se llm_categorizer.py está em src/")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, categorizer_file])
        except Exception as e:
            print(f"❌ Erro na categorização: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_sync(self):
        """Executa sincronização com Google Sheets"""
        print("\n☁️ Iniciando Sincronização...")
        
        sync_file = self.modules['sync']
        
        if not os.path.exists(sync_file):
            print(f"❌ Módulo de sincronização não encontrado: {sync_file}")
            print("💡 Verifique se google_sheets_sync.py está em src/")
            input("Pressione Enter para continuar...")
            return
        
        if not self.config["google_sheets_configured"]:
            print("⚠️ Google Sheets não configurado!")
            print("📋 Configure primeiro em: Configuração do Sistema")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, sync_file])
        except Exception as e:
            print(f"❌ Erro na sincronização: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_analysis(self):
        """Executa análise avançada"""
        print("\n📈 Iniciando Análise Avançada...")
        
        analytics_file = self.modules['analytics']
        
        if not os.path.exists(analytics_file):
            print(f"❌ Módulo de análise não encontrado: {analytics_file}")
            print("💡 Verifique se advanced_analytics.py está em src/")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, analytics_file])
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_setup(self):
        """Executa configuração inicial"""
        print("\n⚙️ Configuração Inicial do Sistema")
        print("="*40)
        
        # 1. Verificar estrutura de pastas
        print("📁 Verificando estrutura de pastas...")
        
        required_folders = [
            "src", "data/raw", "data/processed", "data/exports", 
            "credentials", "css", "config"
        ]
        
        for folder in required_folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                print(f"  ✅ Criada: {folder}")
            else:
                print(f"  ✅ Existe: {folder}")
        
        # 2. Verificar módulos na pasta src/
        print("\n🔧 Verificando módulos em src/...")
        
        missing_modules = []
        for module_name, module_path in self.modules.items():
            if module_name != 'dashboard':  # Dashboard fica na raiz
                if os.path.exists(module_path):
                    print(f"  ✅ {module_name}: {module_path}")
                else:
                    print(f"  ❌ {module_name}: {module_path} - NÃO ENCONTRADO")
                    missing_modules.append((module_name, module_path))
        
        if missing_modules:
            print(f"\n⚠️ MÓDULOS FALTANDO:")
            for module_name, module_path in missing_modules:
                print(f"   • {module_path}")
            print(f"\n💡 Mova os arquivos para a pasta src/ ou verifique se existem")
        
        # 3. Criar arquivo __init__.py na pasta src se não existir
        src_init = "src/__init__.py"
        if not os.path.exists(src_init):
            with open(src_init, 'w', encoding='utf-8') as f:
                f.write('"""Módulos principais do Dashboard Financeiro"""\n')
            print(f"  ✅ Criado: {src_init}")
        
        # 4. Criar arquivos de configuração
        if not os.path.exists(".env"):
            print("\n📝 Criando arquivo .env...")
            env_content = """# Google Sheets
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
SPREADSHEET_NAME=Dashboard Financeiro Pessoal
GOOGLE_DRIVE_FOLDER_ID=

# APIs para categorização automática
OPENAI_API_KEY=
GROQ_API_KEY=

# Configurações
DEFAULT_CURRENCY=BRL
"""
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("  ✅ Arquivo .env criado")
        
        # 5. Resto da configuração continua igual...
        # [código existente para Google Sheets, LLM, etc.]
        
        # 6. Atualizar config para refletir estrutura src/
        self.config["first_run"] = False
        self.config["project_structure"]["modules_in_src"] = True
        self.save_config()
        
        print("\n✅ CONFIGURAÇÃO INICIAL CONCLUÍDA!")
        print("\n📋 ESTRUTURA ORGANIZADA:")
        print("   • Módulos principais: src/")
        print("   • Dashboard: raiz (dashboard.py)")
        print("   • Configurações: config/")
        print("   • Estilos: css/")
        
        input("\nPressione Enter para continuar...")
    
    def check_project_structure(self):
        """Verifica e exibe estrutura do projeto"""
        print("\n📁 VERIFICAÇÃO DA ESTRUTURA DO PROJETO")
        print("="*50)
        
        # Estrutura esperada
        expected_structure = {
            "📄 Arquivos principais": [
                "main.py",
                "dashboard.py", 
                "requirements.txt",
                "README.md"
            ],
            "📁 src/ (Módulos principais)": [
                "src/llm_categorizer.py",
                "src/google_sheets_sync.py", 
                "src/advanced_analytics.py",
                "src/__init__.py"
            ],
            "📁 config/ (Configurações)": [
                "config/settings.py"
            ],
            "📁 css/ (Estilos)": [
                "css/dashboard_styles.css"
            ],
            "📁 data/ (Dados)": [
                "data/raw/",
                "data/processed/",
                "data/exports/"
            ],
            "📁 credentials/ (Segurança)": [
                "credentials/",
                ".env",
                ".gitignore"
            ]
        }
        
        for category, files in expected_structure.items():
            print(f"\n{category}:")
            for file_path in files:
                if file_path.endswith('/'):
                    # É uma pasta
                    exists = os.path.isdir(file_path)
                else:
                    # É um arquivo
                    exists = os.path.exists(file_path)
                
                status = "✅" if exists else "❌"
                print(f"   {status} {file_path}")
        
        # Verificar se há arquivos na raiz que deveriam estar em src/
        root_files = [f for f in os.listdir('.') if f.endswith('.py') and f not in ['main.py', 'dashboard.py']]
        if root_files:
            print(f"\n⚠️ Arquivos Python na raiz (considere mover para src/):")
            for file in root_files:
                print(f"   📄 {file}")
        
        print(f"\n💡 RECOMENDAÇÕES:")
        print("   • Mantenha main.py e dashboard.py na raiz")
        print("   • Mova módulos auxiliares para src/")
        print("   • Use config/ para configurações")
        print("   • Use css/ para estilos")
        print("   • Proteja dados/ e credentials/ no .gitignore")
        
        input("\nPressione Enter para continuar...")
    
    def show_help(self):
        """Exibe ajuda e documentação atualizada"""
        print("\n📖 AJUDA E DOCUMENTAÇÃO - ESTRUTURA src/")
        print("="*60)
        
        help_topics = [
            ("Estrutura do Projeto", [
                "📁 src/ - Módulos principais (llm_categorizer, google_sheets_sync, advanced_analytics)",
                "📄 dashboard.py - Interface principal (na raiz)",
                "📄 main.py - Launcher do sistema (na raiz)",
                "📁 config/ - Arquivos de configuração",
                "📁 css/ - Estilos visuais",
                "📁 data/ - CSVs e dados processados"
            ]),
            ("Comandos por Módulo", [
                "python main.py - Menu principal",
                "streamlit run dashboard.py - Dashboard direto",
                "python src/llm_categorizer.py - Categorização",
                "python src/google_sheets_sync.py - Sincronização",
                "python src/advanced_analytics.py - Análise avançada"
            ]),
            ("Imports e Dependências", [
                "Módulos src/ são importados automaticamente",
                "Use 'from src.module import ...' se necessário",
                "Dashboard pode importar de src/ diretamente",
                "config.json mantém configurações centralizadas"
            ])
        ]
        
        for topic, items in help_topics:
            print(f"\n📋 {topic}:")
            for item in items:
                print(f"   • {item}")
        
        input("\nPressione Enter para continuar...")
    
    def refresh_data_status(self):
        """Atualiza status dos dados e módulos"""
        print("\n🔄 Atualizando status dos dados e módulos...")
        self.data_stats = self.check_data_availability()
        print("✅ Status atualizado!")
        
        # Mostrar status dos módulos
        print(f"\n📊 STATUS DOS MÓDULOS:")
        for module, status in self.data_stats["modules_status"].items():
            icon = "✅" if status else "❌"
            path = self.modules[module]
            print(f"   {icon} {module}: {path}")
        
        if self.data_stats["csv_files"] == 0:
            print("\n📋 Para adicionar dados:")
            print("1. Baixe extratos do Nubank em CSV")
            print("2. Coloque na pasta data/raw/")
            print("3. Use 'Atualizar Status' novamente")
        
        input("Pressione Enter para continuar...")
    
    def run(self):
        """Executa o launcher principal"""
        try:
            while True:
                self.show_welcome_screen()
                
                action = self.show_main_menu()
                
                if action == "exit":
                    print("\n👋 Obrigado por usar o Dashboard Financeiro!")
                    print("💡 Seus dados estão seguros e organizados na estrutura src/")
                    break
                elif action == "dashboard":
                    self.execute_dashboard()
                elif action == "categorize":
                    self.execute_categorization()
                elif action == "sync":
                    self.execute_sync()
                elif action == "analyze":
                    self.execute_analysis()
                elif action == "setup":
                    self.execute_setup()
                elif action == "config":
                    self.execute_config()
                elif action == "structure":
                    self.check_project_structure()
                elif action == "help":
                    self.show_help()
                elif action == "refresh":
                    self.refresh_data_status()
                
                # Salvar configuração após cada ação
                self.save_config()
        
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("💡 Verifique se todos os módulos estão na pasta src/")
    
    def execute_config(self):
        """Configurações do sistema (implementação básica)"""
        print("\n🔧 Configurações do Sistema")
        print("Funcionalidade em desenvolvimento...")
        input("Pressione Enter para continuar...")

def main():
    """Função principal"""
    launcher = FinancialDashboardLauncher()
    launcher.run()

if __name__ == "__main__":
    main()

# ===== SCRIPTS DE CONVENIÊNCIA ATUALIZADOS =====

def quick_start():
    """Início rápido para usuários experientes"""
    print("⚡ INÍCIO RÁPIDO - Estrutura src/")
    print("Escolha:")
    print("1. Dashboard")
    print("2. Categorização (src/)")
    print("3. Análise (src/)")
    print("4. Configuração")
    
    choice = input("Opção: ").strip()
    
    if choice == "1":
        if os.path.exists("dashboard.py"):
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        else:
            print("❌ dashboard.py não encontrado na raiz")
    elif choice == "2":
        if os.path.exists("src/llm_categorizer.py"):
            subprocess.run([sys.executable, "src/llm_categorizer.py"])
        else:
            print("❌ src/llm_categorizer.py não encontrado")
    elif choice == "3":
        if os.path.exists("src/advanced_analytics.py"):
            subprocess.run([sys.executable, "src/advanced_analytics.py"])
        else:
            print("❌ src/advanced_analytics.py não encontrado")
    elif choice == "4":
        launcher = FinancialDashboardLauncher()
        launcher.execute_setup()

def check_system():
    """Verificação rápida do sistema atualizada"""
    print("🔍 VERIFICAÇÃO DO SISTEMA - Estrutura src/")
    print("="*40)
    
    # Arquivos essenciais
    essential_files = {
        "📄 Raiz": ["main.py", "dashboard.py"],
        "📁 src/": ["src/llm_categorizer.py", "src/google_sheets_sync.py", "src/advanced_analytics.py"],
        "📁 Outros": ["requirements.txt", "README.md"]
    }
    
    for category, files in essential_files.items():
        print(f"\n{category}:")
        for file in files:
            status = "✅" if os.path.exists(file) else "❌"
            print(f"   {status} {file}")
    
    # Dependências
    print("\n📦 Dependências:")
    deps = ["streamlit", "pandas", "plotly", "gspread", "numpy"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep}")
    
    # Dados
    print("\n📊 Dados:")
    csv_count = len(list(Path(".").rglob("*.csv")))
    print(f"   📄 CSVs encontrados: {csv_count}")
    
    # Estrutura
    print("\n📁 Estrutura:")
    folders = ["src", "data/raw", "config", "css", "credentials"]
    for folder in folders:
        status = "✅" if os.path.exists(folder) else "❌"
        print(f"   {status} {folder}/")

# Para execução direta com estrutura src/
if len(sys.argv) > 1:
    command = sys.argv[1].lower()
    
    if command == "quick":
        quick_start()
    elif command == "check":
        check_system()
    elif command == "dashboard":
        if os.path.exists("dashboard.py"):
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        else:
            print("❌ dashboard.py não encontrado na raiz")
    elif command == "analyze":
        if os.path.exists("src/advanced_analytics.py"):
            subprocess.run([sys.executable, "src/advanced_analytics.py"])
        else:
            print("❌ src/advanced_analytics.py não encontrado")
    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos disponíveis: quick, check, dashboard, analyze")
else:
    main()