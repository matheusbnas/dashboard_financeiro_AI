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
            "folders_checked": []
        }
        
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
        print("\033[92m" + "="*80 + "\033[0m")
        
        # Status do sistema
        print(f"\n📊 STATUS DO SISTEMA:")
        print(f"   • Arquivos CSV encontrados: {self.data_stats['csv_files']}")
        
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
            ("2", "🤖 Categorizar Transações (LLM)", "categorize", self.data_stats['csv_files'] > 0),
            ("3", "☁️  Sincronizar Google Sheets", "sync", self.data_stats['csv_files'] > 0),
            ("4", "📈 Análise Avançada e Relatórios", "analyze", self.data_stats['csv_files'] > 0),
            ("5", "⚙️  Configuração Inicial", "setup", True),
            ("6", "🔧 Configurações do Sistema", "config", True),
            ("7", "ℹ️  Ajuda e Documentação", "help", True),
            ("8", "🔄 Atualizar Status dos Dados", "refresh", True),
            ("0", "❌ Sair", "exit", True)
        ]
        
        for num, title, action, enabled in options:
            status = "" if enabled else " (❌ Sem dados)"
            color = "\033[92m" if enabled else "\033[91m"
            print(f"{color}{num}. {title}{status}\033[0m")
        
        print("="*60)
        
        while True:
            choice = input("\n📝 Escolha uma opção (0-8): ").strip()
            
            selected_option = next((opt for opt in options if opt[0] == choice), None)
            if selected_option:
                _, title, action, enabled = selected_option
                if enabled:
                    return action
                else:
                    print("❌ Esta opção requer dados CSV. Configure primeiro!")
            else:
                print("⚠️ Opção inválida! Digite um número de 0 a 8.")
    
    def execute_dashboard(self):
        """Executa dashboard principal"""
        print("\n🚀 Iniciando Dashboard Interativo...")
        
        # Verificar se o arquivo existe
        dashboard_files = ["dashboard.py", "improved_dashboard.py"]
        dashboard_file = None
        
        for file in dashboard_files:
            if os.path.exists(file):
                dashboard_file = file
                break
        
        if not dashboard_file:
            print("❌ Arquivo do dashboard não encontrado!")
            print("📋 Arquivos procurados:", ", ".join(dashboard_files))
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
        
        if not os.path.exists("llm_categorizer.py"):
            print("❌ Módulo de categorização não encontrado!")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, "llm_categorizer.py"])
        except Exception as e:
            print(f"❌ Erro na categorização: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_sync(self):
        """Executa sincronização com Google Sheets"""
        print("\n☁️ Iniciando Sincronização...")
        
        if not os.path.exists("google_sheets_sync.py"):
            print("❌ Módulo de sincronização não encontrado!")
            input("Pressione Enter para continuar...")
            return
        
        if not self.config["google_sheets_configured"]:
            print("⚠️ Google Sheets não configurado!")
            print("📋 Configure primeiro em: Configuração do Sistema")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, "google_sheets_sync.py"])
        except Exception as e:
            print(f"❌ Erro na sincronização: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_analysis(self):
        """Executa análise avançada"""
        print("\n📈 Iniciando Análise Avançada...")
        
        if not os.path.exists("advanced_analytics.py"):
            print("❌ Módulo de análise não encontrado!")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, "advanced_analytics.py"])
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_setup(self):
        """Executa configuração inicial"""
        print("\n⚙️ Configuração Inicial do Sistema")
        print("="*40)
        
        # 1. Verificar estrutura de pastas
        print("📁 Verificando estrutura de pastas...")
        
        required_folders = ["data/raw", "data/processed", "data/exports", "credentials"]
        for folder in required_folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                print(f"  ✅ Criada: {folder}")
            else:
                print(f"  ✅ Existe: {folder}")
        
        # 2. Criar arquivos de configuração
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
        
        # 3. Verificar dependências
        print("\n📦 Verificando dependências...")
        required_packages = ["streamlit", "pandas", "plotly", "gspread"]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - não instalado")
        
        # 4. Configurar Google Sheets
        print("\n☁️ Configuração Google Sheets:")
        if os.path.exists("credentials/google_credentials.json"):
            print("  ✅ Credenciais encontradas")
            self.config["google_sheets_configured"] = True
        else:
            print("  ❌ Credenciais não encontradas")
            print("  📋 Para configurar:")
            print("     1. Acesse: https://console.cloud.google.com/")
            print("     2. Crie um projeto ou selecione existente")
            print("     3. Habilite Google Sheets API e Google Drive API")
            print("     4. Crie Service Account e baixe JSON")
            print("     5. Coloque em: credentials/google_credentials.json")
        
        # 5. Configurar LLM
        print("\n🤖 Configuração de LLM para categorização:")
        print("1. Groq (Gratuito) - Recomendado")
        print("2. OpenAI (Pago)")
        print("3. Apenas regras (Sem IA)")
        
        llm_choice = input("Escolha (1-3, Enter para manter atual): ").strip()
        
        if llm_choice == "1":
            self.config["llm_provider"] = "groq"
            print("  ✅ Configurado para Groq")
            print("  📋 Configure GROQ_API_KEY no arquivo .env")
        elif llm_choice == "2":
            self.config["llm_provider"] = "openai"
            print("  ✅ Configurado para OpenAI")
            print("  📋 Configure OPENAI_API_KEY no arquivo .env")
        elif llm_choice == "3":
            self.config["llm_provider"] = "local"
            print("  ✅ Configurado para usar apenas regras")
        
        # 6. Configurar pastas de dados
        print("\n📂 Onde estão seus CSVs do Nubank?")
        print("1. data/raw/ (Recomendado)")
        print("2. extratos/")
        print("3. Pasta atual")
        print("4. Outra pasta")
        
        folder_choice = input("Escolha (1-4): ").strip()
        
        if folder_choice == "1":
            data_folder = "data/raw"
        elif folder_choice == "2":
            data_folder = "extratos"
            os.makedirs(data_folder, exist_ok=True)
        elif folder_choice == "3":
            data_folder = "."
        elif folder_choice == "4":
            data_folder = input("Digite o caminho da pasta: ").strip()
            if not os.path.exists(data_folder):
                os.makedirs(data_folder, exist_ok=True)
        else:
            data_folder = "data/raw"
        
        if data_folder not in self.config["data_folders"]:
            self.config["data_folders"].insert(0, data_folder)
        
        print(f"  ✅ Pasta configurada: {data_folder}")
        
        # 7. Finalizar
        self.config["first_run"] = False
        self.save_config()
        
        print("\n✅ CONFIGURAÇÃO INICIAL CONCLUÍDA!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Coloque seus CSVs do Nubank na pasta configurada")
        print("2. Configure as chaves de API no arquivo .env (opcional)")
        print("3. Execute o Dashboard ou Categorização")
        
        input("\nPressione Enter para continuar...")
    
    def execute_config(self):
        """Configurações do sistema"""
        print("\n🔧 Configurações do Sistema")
        print("="*30)
        
        while True:
            print(f"\nConfiguração atual:")
            print(f"• Provedor LLM: {self.config['llm_provider']}")
            print(f"• Google Sheets: {'✅' if self.config['google_sheets_configured'] else '❌'}")
            print(f"• Pastas de dados: {', '.join(self.config['data_folders'])}")
            print(f"• Auto-categorizar: {'✅' if self.config['user_preferences']['auto_categorize'] else '❌'}")
            
            print(f"\nOpções:")
            print("1. Alterar provedor LLM")
            print("2. Testar Google Sheets")
            print("3. Gerenciar pastas de dados")
            print("4. Preferências do usuário")
            print("5. Resetar configurações")
            print("0. Voltar")
            
            choice = input("Escolha: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.config_llm_provider()
            elif choice == "2":
                self.test_google_sheets()
            elif choice == "3":
                self.manage_data_folders()
            elif choice == "4":
                self.config_user_preferences()
            elif choice == "5":
                self.reset_config()
    
    def config_llm_provider(self):
        """Configura provedor de LLM"""
        print("\nProvedores disponíveis:")
        print("1. Groq (Llama - Gratuito)")
        print("2. OpenAI (GPT - Pago)")
        print("3. Local (Apenas regras)")
        
        choice = input("Escolha: ").strip()
        
        if choice == "1":
            self.config["llm_provider"] = "groq"
        elif choice == "2":
            self.config["llm_provider"] = "openai"
        elif choice == "3":
            self.config["llm_provider"] = "local"
        
        self.save_config()
        print(f"✅ Provedor alterado para: {self.config['llm_provider']}")
    
    def test_google_sheets(self):
        """Testa conexão com Google Sheets"""
        if not os.path.exists("credentials/google_credentials.json"):
            print("❌ Credenciais não encontradas!")
            return
        
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            
            scopes = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "credentials/google_credentials.json", scopes
            )
            
            client = gspread.authorize(creds)
            print("✅ Conexão com Google Sheets bem-sucedida!")
            self.config["google_sheets_configured"] = True
            self.save_config()
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            self.config["google_sheets_configured"] = False
            self.save_config()
    
    def show_help(self):
        """Exibe ajuda e documentação"""
        print("\n📖 AJUDA E DOCUMENTAÇÃO")
        print("="*50)
        
        help_topics = [
            ("Início Rápido", [
                "1. Coloque CSVs do Nubank na pasta data/raw/",
                "2. Execute 'Configuração Inicial'",
                "3. Use o Dashboard Interativo",
                "4. Categorize transações com LLM (opcional)",
                "5. Sincronize com Google Sheets (opcional)"
            ]),
            ("Estrutura de Arquivos", [
                "data/raw/ - CSVs do Nubank",
                "data/processed/ - Dados processados",
                "credentials/ - Credenciais Google",
                ".env - Variáveis de ambiente",
                "config.json - Configurações do sistema"
            ]),
            ("Formato dos CSVs", [
                "Colunas obrigatórias: ID, Data, Valor, Descrição",
                "Coluna opcional: Categoria",
                "Data no formato: YYYY-MM-DD",
                "Valor numérico (negativo = despesa, positivo = receita)"
            ]),
            ("Google Sheets", [
                "1. Acesse console.cloud.google.com",
                "2. Crie projeto e habilite APIs",
                "3. Crie Service Account",
                "4. Baixe JSON para credentials/",
                "5. Compartilhe planilha com email do Service Account"
            ]),
            ("Solução de Problemas", [
                "Erro de CSV: Verifique encoding (UTF-8, Latin-1)",
                "Erro de dependência: pip install -r requirements.txt",
                "Erro Google: Verifique credenciais e permissões",
                "Erro LLM: Configure chaves de API no .env"
            ])
        ]
        
        for topic, items in help_topics:
            print(f"\n📋 {topic}:")
            for item in items:
                print(f"   • {item}")
        
        print(f"\n🔗 LINKS ÚTEIS:")
        print("   • Google Cloud Console: https://console.cloud.google.com/")
        print("   • Groq API: https://console.groq.com/")
        print("   • OpenAI API: https://platform.openai.com/")
        print("   • Streamlit Docs: https://docs.streamlit.io/")
        
        input("\nPressione Enter para continuar...")
    
    def refresh_data_status(self):
        """Atualiza status dos dados"""
        print("\n🔄 Atualizando status dos dados...")
        self.data_stats = self.check_data_availability()
        print("✅ Status atualizado!")
        
        if self.data_stats["csv_files"] == 0:
            print("\n📋 Para adicionar dados:")
            print("1. Baixe extratos do Nubank em CSV")
            print("2. Coloque na pasta configurada")
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
                    print("💡 Seus dados estão seguros e não foram compartilhados.")
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
            print("💡 Tente executar os módulos individualmente")

def main():
    """Função principal"""
    launcher = FinancialDashboardLauncher()
    launcher.run()

if __name__ == "__main__":
    main()

# ===== SCRIPTS DE CONVENIÊNCIA =====

def quick_start():
    """Início rápido para usuários experientes"""
    print("⚡ INÍCIO RÁPIDO")
    print("Escolha:")
    print("1. Dashboard")
    print("2. Análise")
    print("3. Configuração")
    
    choice = input("Opção: ").strip()
    
    if choice == "1":
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    elif choice == "2":
        subprocess.run([sys.executable, "advanced_analytics.py"])
    elif choice == "3":
        launcher = FinancialDashboardLauncher()
        launcher.execute_setup()

def check_system():
    """Verificação rápida do sistema"""
    print("🔍 VERIFICAÇÃO DO SISTEMA")
    print("="*30)
    
    # Arquivos essenciais
    essential_files = [
        "dashboard.py",
        "llm_categorizer.py", 
        "google_sheets_sync.py",
        "advanced_analytics.py"
    ]
    
    print("📄 Arquivos essenciais:")
    for file in essential_files:
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
    
    # Configuração
    print("\n⚙️ Configuração:")
    print(f"   📝 .env: {'✅' if os.path.exists('.env') else '❌'}")
    print(f"   🔑 Google: {'✅' if os.path.exists('credentials/google_credentials.json') else '❌'}")

# Para execução direta de funcionalidades específicas
if len(sys.argv) > 1:
    command = sys.argv[1].lower()
    
    if command == "quick":
        quick_start()
    elif command == "check":
        check_system()
    elif command == "dashboard":
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    elif command == "analyze":
        subprocess.run([sys.executable, "advanced_analytics.py"])
    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos disponíveis: quick, check, dashboard, analyze")
else:
    main()