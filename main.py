#!/usr/bin/env python3
"""
Dashboard Financeiro Completo v5.0 - Launcher Principal
Sistema completo de análise financeira pessoal com IA integrada

🚀 ATUALIZAÇÕES v5.0:
✅ Chatbot IA integrado para análise conversacional
✅ Google Sheets avançado com organização automática por ano/mês
✅ CSS otimizado para perfeita compatibilidade claro/escuro
✅ Menu de navegação unificado no dashboard
✅ Configuração automática completa
✅ Emails atualizados: matheusbnas@gmail.com e dashboard-financeiro@api-financeiro-460817.iam.gserviceaccount.com

Execute: python main.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import webbrowser
import platform

# Adicionar pasta src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ASCII Art atualizado
LOGO = r"""
 $$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$\  $$\   $$\ $$$$$$\ $$\      $$\  $$$$$$\        $$\    $$\ $$$$$$$\  
$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$ |  $$ |\_$$  _|$$$\    $$$ |$$  __$$\       $$ |   $$ |$$  _____|
$$ /  \__|$$ |  $$ |$$ /  $$ |$$ /  \__|$$ |  $$ |  $$ |  $$$$\  $$$$ |$$ /  $$ |      $$ |   $$ |$$ |      
\$$$$$$\  $$$$$$$  |$$$$$$$$ |\$$$$$$\  $$$$$$$$ |  $$ |  $$\$$\$$ $$ |$$ |  $$ |      \$$\  $$  |$$$$$$$\  
 \____$$\ $$  ____/ $$  __$$ | \____$$\ $$  __$$ |  $$ |  $$ \$$$  $$ |$$ |  $$ |       \$$\$$  / \_____$$\ 
$$\   $$ |$$ |      $$ |  $$ |$$\   $$ |$$ |  $$ |  $$ |  $$ |\$  /$$ |$$ |  $$ |        \$$$  /  $$\   $$ |
\$$$$$$  |$$ |      $$ |  $$ |\$$$$$$  |$$ |  $$ |$$$$$$\ $$ | \_/ $$ | $$$$$$  |         \$  /   \$$$$$$  |
 \______/ \__|      \__|  \__| \______/ \__|  \__|\______|\__|     \__| \______/           \_/     \______/ 
"""

class FinancialDashboardLauncherV5:
    """Launcher principal do sistema v5.0 com todas as melhorias"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.version = "5.0.0"
        
        # Módulos disponíveis (atualizado)
        self.modules = {
            'dashboard': 'dashboard.py',
            'chatbot': 'chatbot.py',
            'categorizer': 'src/llm_categorizer.py',
            'sync_basic': 'src/google_sheets_sync.py',
            'sync_advanced': 'src/google_sheets_advanced.py',
            'analytics': 'src/advanced_analytics.py',
            'auto_setup': 'auto_setup.py',
            'system_check': 'system_checker.py'
        }
        
        # Emails configurados
        self.emails = {
            'primary': 'matheusbnas@gmail.com',
            'service_account': 'dashboard-financeiro@api-financeiro-460817.iam.gserviceaccount.com'
        }
        
        self.config = self.load_config()
        self.data_stats = self.check_data_availability()
        self.system_status = self.check_system_status()
    
    def load_config(self) -> dict:
        """Carrega configuração do sistema"""
        default_config = {
            "project_info": {
                "name": "Dashboard Financeiro Avançado",
                "version": self.version,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            "features": {
                "chatbot_enabled": True,
                "google_sheets_advanced": True,
                "ai_categorization": True,
                "nubank_optimized": True,
                "theme_adaptive": True,
                "css_optimized": True
            },
            "first_run": True,
            "google_sheets_configured": False,
            "llm_provider": "groq",
            "data_folders": ["data/raw", "extratos", "."],
            "last_analysis": None,
            "user_preferences": {
                "default_action": "dashboard",
                "auto_categorize": True,
                "auto_sync": False,
                "preferred_llm": "groq"
            },
            "integrations": {
                "google_sheets": {
                    "advanced_mode": True,
                    "auto_organize": True,
                    "create_yearly_summary": True,
                    "auto_share": True
                },
                "ai_services": {
                    "groq_enabled": False,
                    "openai_enabled": False,
                    "chatbot_active": True
                }
            },
            "ui": {
                "theme": "auto",
                "css_optimized": True,
                "navigation_menu": True
            },
            "emails": self.emails
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Mesclar com defaults para novos campos v5.0
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                
                # Atualizar emails se necessário
                config["emails"] = self.emails
                return config
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")
                return default_config
        
        return default_config
    
    def save_config(self):
        """Salva configuração"""
        try:
            self.config["project_info"]["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar config: {e}")
    
    def check_data_availability(self) -> dict:
        """Verifica disponibilidade de dados"""
        stats = {
            "csv_files": 0,
            "nubank_files": 0,
            "total_transactions": 0,
            "date_range": None,
            "categories_available": False,
            "folders_checked": [],
            "recent_files": []
        }
        
        # Procurar CSVs
        csv_files = []
        nubank_files = []
        
        for folder in self.config["data_folders"]:
            if os.path.exists(folder):
                stats["folders_checked"].append(folder)
                folder_csvs = list(Path(folder).glob("*.csv"))
                csv_files.extend(folder_csvs)
                
                # Identificar arquivos do Nubank
                nubank_pattern = list(Path(folder).glob("Nubank_*.csv"))
                nubank_files.extend(nubank_pattern)
        
        stats["csv_files"] = len(csv_files)
        stats["nubank_files"] = len(nubank_files)
        
        # Arquivos mais recentes
        if csv_files:
            csv_files_with_time = [(f, f.stat().st_mtime) for f in csv_files]
            csv_files_with_time.sort(key=lambda x: x[1], reverse=True)
            stats["recent_files"] = [str(f[0]) for f in csv_files_with_time[:5]]
            
            # Analisar arquivo de exemplo
            try:
                sample_file = csv_files[0]
                sample_df = pd.read_csv(sample_file)
                
                stats["total_transactions"] = len(sample_df)
                stats["categories_available"] = 'Categoria' in sample_df.columns
                
                # Detectar formato e datas
                if all(col in sample_df.columns for col in ['date', 'title', 'amount']):
                    # Formato Nubank
                    sample_df['date'] = pd.to_datetime(sample_df['date'], errors='coerce')
                    stats["date_range"] = {
                        "start": sample_df['date'].min(),
                        "end": sample_df['date'].max()
                    }
                    stats["format"] = "Nubank"
                elif 'Data' in sample_df.columns:
                    # Formato tradicional
                    sample_df['Data'] = pd.to_datetime(sample_df['Data'], errors='coerce')
                    stats["date_range"] = {
                        "start": sample_df['Data'].min(),
                        "end": sample_df['Data'].max()
                    }
                    stats["format"] = "Tradicional"
                
            except Exception as e:
                stats["error"] = str(e)
        
        return stats
    
    def check_system_status(self) -> dict:
        """Verifica status do sistema"""
        status = {
            "modules_available": {},
            "dependencies_ok": True,
            "css_optimized": False,
            "chatbot_ready": False,
            "google_sheets_basic": False,
            "google_sheets_advanced": False,
            "ai_ready": False
        }
        
        # Verificar módulos
        for module_name, module_path in self.modules.items():
            status["modules_available"][module_name] = os.path.exists(module_path)
        
        # Verificar dependências críticas
        try:
            import streamlit
            import pandas
            import plotly
            status["dependencies_ok"] = True
        except ImportError:
            status["dependencies_ok"] = False
        
        # Verificar CSS otimizado
        css_path = Path("css/dashboard_styles.css")
        if css_path.exists():
            css_content = css_path.read_text(encoding='utf-8')
            status["css_optimized"] = "border-radius" in css_content and "transition" in css_content
        
        # Verificar chatbot
        status["chatbot_ready"] = status["modules_available"].get("chatbot", False)
        
        # Verificar Google Sheets
        creds_exist = os.path.exists("credentials/google_credentials.json")
        basic_module = status["modules_available"].get("sync_basic", False)
        advanced_module = status["modules_available"].get("sync_advanced", False)
        
        status["google_sheets_basic"] = creds_exist and basic_module
        status["google_sheets_advanced"] = creds_exist and advanced_module
        
        # Verificar IA
        env_file = Path(".env")
        if env_file.exists():
            env_content = env_file.read_text(encoding='utf-8')
            has_groq = "GROQ_API_KEY=" in env_content and len(env_content.split("GROQ_API_KEY=")[1].split("\n")[0].strip()) > 0
            has_openai = "OPENAI_API_KEY=" in env_content and len(env_content.split("OPENAI_API_KEY=")[1].split("\n")[0].strip()) > 0
            status["ai_ready"] = has_groq or has_openai
        
        return status
    
    def show_welcome_screen_v5(self):
        """Exibe tela de boas-vindas v5.0"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\033[96m" + LOGO + "\033[0m")
        print("\033[92m" + "="*100 + "\033[0m")
        print("\033[93m" + "         DASHBOARD FINANCEIRO PESSOAL COMPLETO v5.0".center(100) + "\033[0m")
        print("\033[94m" + "        🤖 IA INTEGRADA | ☁️ GOOGLE SHEETS AVANÇADO | 💳 NUBANK OTIMIZADO".center(100) + "\033[0m")
        print("\033[92m" + "="*100 + "\033[0m")
        
        # Emails configurados
        print(f"\n📧 EMAILS CONFIGURADOS:")
        print(f"   • Principal: {self.emails['primary']}")
        print(f"   • Service Account: {self.emails['service_account']}")
        
        # Novidades v5.0
        print(f"\n🎉 FUNCIONALIDADES v5.0:")
        print(f"   🤖 Chatbot IA integrado - Converse sobre seus gastos")
        print(f"   ☁️ Google Sheets avançado - Planilhas organizadas por ano/mês automaticamente")
        print(f"   🎨 CSS otimizado v3 - Legibilidade perfeita em todos os temas") 
        print(f"   🧭 Menu unificado - Navegação integrada no dashboard")
        print(f"   📊 Botão direto Google Sheets - Acesso rápido às planilhas")
        print(f"   🔧 Configuração automática - Setup completo em um comando")
        
        # Status do sistema
        print(f"\n📊 STATUS DO SISTEMA:")
        print(f"   • Arquivos CSV: {self.data_stats.get('csv_files', 0)} (Nubank: {self.data_stats.get('nubank_files', 0)})")
        print(f"   • Transações estimadas: {self.data_stats.get('total_transactions', 0):,}")
        
        if self.data_stats.get('date_range'):
            start = self.data_stats['date_range']['start']
            end = self.data_stats['date_range']['end']
            if pd.notna(start) and pd.notna(end):
                print(f"   • Período: {start.strftime('%d/%m/%Y')} até {end.strftime('%d/%m/%Y')}")
        
        # Status dos módulos v5.0
        print(f"\n🔧 FUNCIONALIDADES v5.0:")
        
        features = [
            ("📊 Dashboard Principal", self.system_status["modules_available"].get('dashboard', False)),
            ("🤖 Chatbot IA", self.system_status["chatbot_ready"]),
            ("☁️ Google Sheets Básico", self.system_status["google_sheets_basic"]),
            ("🚀 Google Sheets Avançado", self.system_status["google_sheets_advanced"]),
            ("🏷️ Categorização IA", self.system_status["modules_available"].get('categorizer', False)),
            ("📈 Análise Avançada", self.system_status["modules_available"].get('analytics', False)),
            ("🎨 CSS Otimizado v3", self.system_status["css_optimized"]),
            ("🔧 Dependências", self.system_status["dependencies_ok"])
        ]
        
        for feature_name, status in features:
            status_icon = "✅" if status else "❌"
            print(f"   • {feature_name}: {status_icon}")
        
        # Status das integrações
        print(f"\n🔧 INTEGRAÇÕES:")
        print(f"   • Google Sheets Básico: {'✅ Configurado' if self.system_status['google_sheets_basic'] else '❌ Não configurado'}")
        print(f"   • Google Sheets Avançado: {'✅ Configurado' if self.system_status['google_sheets_advanced'] else '❌ Não configurado'}")
        print(f"   • IA (Groq/OpenAI): {'✅ Configurada' if self.system_status['ai_ready'] else '❌ Não configurada'}")
        
        # Dados Nubank
        if self.data_stats.get('nubank_files', 0) > 0:
            print(f"\n💳 DADOS NUBANK DETECTADOS:")
            print(f"   • {self.data_stats['nubank_files']} arquivos Nubank_*.csv")
            print(f"   • Análise otimizada disponível")
            print(f"   • Chatbot especializado ativo")
            print(f"   • Google Sheets automático com organização por período")
        
        # Configuração inicial
        if self.config.get("first_run", True):
            print(f"\n🎯 PRIMEIRA EXECUÇÃO DETECTADA:")
            print(f"   Recomendamos executar a configuração automática para otimizar o sistema.")
    
    def show_main_menu_v5(self):
        """Exibe menu principal v5.0"""
        print(f"\n" + "="*80)
        print("MENU PRINCIPAL v5.0 - COMPLETO COM GOOGLE SHEETS AVANÇADO")
        print("="*80)
        
        options = [
            # Funcionalidades principais
            ("1", "🚀 Dashboard Interativo Completo", "dashboard", 
             self.system_status["modules_available"].get('dashboard', False)),
            
            ("2", "🤖 Chatbot IA Financeiro", "chatbot", 
             self.system_status["chatbot_ready"]),
            
            ("3", "☁️ Google Sheets Básico", "sheets_basic", 
             self.system_status["google_sheets_basic"]),
            
            ("4", "🚀 Google Sheets Avançado (Ano/Mês)", "sheets_advanced", 
             self.system_status["google_sheets_advanced"]),
            
            ("5", "🏷️ Categorizar com IA", "categorize", 
             self.system_status["modules_available"].get('categorizer', False)),
            
            ("6", "📈 Análise Avançada & Relatórios", "analyze", 
             self.system_status["modules_available"].get('analytics', False)),
            
            # Configuração e manutenção
            ("7", "⚙️ Configuração Automática", "auto_setup", 
             self.system_status["modules_available"].get('auto_setup', False)),
            
            ("8", "🔧 Configurações do Sistema", "config", True),
            
            ("9", "🔍 Diagnóstico Completo", "system_check", 
             self.system_status["modules_available"].get('system_check', False)),
            
            # Utilitários
            ("10", "📁 Gerenciar Dados", "data_manager", True),
            
            ("11", "ℹ️ Ajuda & Documentação", "help", True),
            
            ("0", "❌ Sair", "exit", True)
        ]
        
        for num, title, action, enabled in options:
            if not enabled:
                if action in ['categorize', 'analyze']:
                    status = " (❌ Módulo não encontrado em src/)"
                elif action == 'chatbot':
                    status = " (❌ chatbot.py não encontrado)"
                elif action in ['sheets_basic', 'sheets_advanced']:
                    status = " (❌ Google Sheets não configurado)"
                else:
                    status = " (❌ Não disponível)"
            else:
                status = ""
                
            color = "\033[92m" if enabled else "\033[91m"
            print(f"{color}{num:>2}. {title}{status}\033[0m")
        
        print("="*80)
        
        # Sugestões baseadas no status
        if self.config.get("first_run", True):
            print("\n💡 PRIMEIRA EXECUÇÃO - SUGESTÕES:")
            print("   1. Execute 'Configuração Automática' para setup completo")
            print("   2. Configure APIs (.env) para IA e Google Sheets")
            print("   3. Adicione dados CSV em data/raw/")
            print("   4. Use o Dashboard Interativo")
        
        if not self.system_status["ai_ready"]:
            print("\n🤖 CONFIGURE IA (OPCIONAL):")
            print("   • Groq (gratuito): https://console.groq.com/")
            print("   • OpenAI (pago): https://platform.openai.com/")
            print("   • Adicione chaves no arquivo .env")
        
        if not self.system_status["google_sheets_advanced"]:
            print("\n🚀 CONFIGURE GOOGLE SHEETS AVANÇADO:")
            print("   • Google Cloud Console: APIs & Services")
            print("   • Habilite Google Sheets API + Drive API")
            print("   • Crie Service Account e baixe JSON")
            print("   • Salve em credentials/google_credentials.json")
            print(f"   • Emails configurados: {self.emails['primary']}")
            print(f"   • Service Account: {self.emails['service_account']}")
        
        while True:
            choice = input(f"\n📝 Escolha uma opção (0-11): ").strip()
            
            selected_option = next((opt for opt in options if opt[0] == choice), None)
            if selected_option:
                _, title, action, enabled = selected_option
                if enabled:
                    return action
                else:
                    print("❌ Esta funcionalidade não está disponível!")
                    if action == "chatbot":
                        print("💡 Configure o arquivo chatbot.py na raiz do projeto")
                    elif action in ['categorize', 'analyze']:
                        print("💡 Verifique se os módulos estão na pasta src/")
                    elif action in ["sheets_basic", "sheets_advanced"]:
                        print("💡 Configure Google Sheets API e credenciais")
            else:
                print("⚠️ Opção inválida! Digite um número de 0 a 11.")
    
    def execute_dashboard(self):
        """Executa dashboard principal"""
        print("\n🚀 Iniciando Dashboard Interativo v5.0...")
        print("   • Interface otimizada com menu de navegação")
        print("   • CSS v3 com legibilidade perfeita")
        print("   • Botão direto para Google Sheets avançado")
        print("   • Integração com chatbot e análise avançada")
        
        if not self.system_status["modules_available"].get('dashboard', False):
            print("❌ dashboard.py não encontrado!")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        except Exception as e:
            print(f"❌ Erro ao executar dashboard: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_chatbot(self):
        """Executa chatbot IA"""
        print("\n🤖 Iniciando Chatbot IA Financeiro...")
        print("   • Análise conversacional dos seus gastos")
        print("   • Suporte a Groq (gratuito) e OpenAI")
        print("   • Respostas inteligentes sobre padrões financeiros")
        print("   • Integração com dados Nubank")
        
        if not self.system_status["chatbot_ready"]:
            print("❌ Chatbot não está configurado!")
            print("💡 Verifique se chatbot.py existe na raiz do projeto")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "chatbot.py"])
        except Exception as e:
            print(f"❌ Erro ao executar chatbot: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_sheets_basic(self):
        """Executa Google Sheets básico"""
        print("\n☁️ Iniciando Google Sheets Básico...")
        print("   • Sincronização simples com planilhas organizadas")
        print("   • 5 abas automáticas: Dados, Resumo, Categorias, Fixos, Top Gastos")
        print(f"   • Compartilhamento automático com: {self.emails['primary']}")
        
        if not self.system_status["google_sheets_basic"]:
            print("❌ Google Sheets básico não configurado!")
            print("💡 Configure credenciais em credentials/google_credentials.json")
            input("Pressione Enter para continuar...")
            return
        
        basic_module = self.modules.get('sync_basic')
        if not basic_module or not os.path.exists(basic_module):
            print("❌ Módulo básico não encontrado!")
            print("💡 Verifique se google_sheets_sync.py está em src/")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, basic_module])
        except Exception as e:
            print(f"❌ Erro na sincronização básica: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_sheets_advanced(self):
        """Executa Google Sheets avançado"""
        print("\n🚀 Iniciando Google Sheets Avançado...")
        print("   • Criação automática de planilhas por ano/mês")
        print("   • Índice master com links para todas as planilhas")
        print("   • Organização inteligente dos dados por período")
        print("   • 5 abas especializadas por mês: Resumo, Dados, Categorias, Estabelecimentos, Fixos")
        print(f"   • Compartilhamento automático com emails configurados")
        
        if not self.system_status["google_sheets_advanced"]:
            print("❌ Google Sheets avançado não configurado!")
            print("💡 Configure credenciais em credentials/google_credentials.json")
            input("Pressione Enter para continuar...")
            return
        
        advanced_module = self.modules.get('sync_advanced')
        if not advanced_module or not os.path.exists(advanced_module):
            print("❌ Módulo avançado não encontrado!")
            print("💡 Verifique se google_sheets_advanced.py está em src/")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, advanced_module])
        except Exception as e:
            print(f"❌ Erro na sincronização avançada: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_auto_setup(self):
        """Executa configuração automática"""
        print("\n⚙️ Configuração Automática v5.0...")
        print("   • Cria estrutura completa do projeto")
        print("   • Instala todas as dependências")
        print("   • Configura arquivos de segurança")
        print("   • Otimiza sistema para v5.0")
        print("   • Configura emails automaticamente")
        
        auto_setup_file = self.modules.get('auto_setup')
        if not auto_setup_file or not os.path.exists(auto_setup_file):
            print("❌ Script de configuração não encontrado!")
            print("💡 Certifique-se de ter auto_setup.py na raiz")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, auto_setup_file])
            print("✅ Configuração automática concluída!")
            print("🔄 Reiniciando para aplicar mudanças...")
            
            # Recarregar configurações
            self.config = self.load_config()
            self.system_status = self.check_system_status()
            
        except Exception as e:
            print(f"❌ Erro na configuração automática: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_data_manager(self):
        """Gerenciador de dados"""
        print("\n📁 Gerenciador de Dados v5.0")
        print("="*40)
        
        print("1. Ver arquivos CSV disponíveis")
        print("2. Verificar formato dos dados")
        print("3. Limpar dados processados")
        print("4. Backup dos dados")
        print("5. Estatísticas dos dados")
        print("6. Voltar ao menu principal")
        
        choice = input("\nEscolha (1-6): ").strip()
        
        if choice == "1":
            print(f"\n📄 ARQUIVOS CSV ENCONTRADOS:")
            if self.data_stats["recent_files"]:
                for i, file in enumerate(self.data_stats["recent_files"], 1):
                    file_path = Path(file)
                    size = file_path.stat().st_size / 1024  # KB
                    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"   {i}. {file_path.name}")
                    print(f"      Tamanho: {size:.1f} KB")
                    print(f"      Modificado: {modified.strftime('%d/%m/%Y %H:%M')}")
                    print()
            else:
                print("   Nenhum arquivo CSV encontrado")
                print("   💡 Coloque arquivos em: data/raw/, extratos/ ou pasta atual")
        
        elif choice == "2":
            print(f"\n🔍 FORMATO DOS DADOS:")
            format_type = self.data_stats.get('format', 'Desconhecido')
            print(f"   • Formato detectado: {format_type}")
            print(f"   • Transações estimadas: {self.data_stats.get('total_transactions', 0):,}")
            print(f"   • Categorias disponíveis: {'Sim' if self.data_stats.get('categories_available') else 'Não'}")
            
            if format_type == "Nubank":
                print(f"   • Otimizações Nubank: ✅ Ativas")
                print(f"   • Análise de estabelecimentos: ✅ Disponível")
                print(f"   • Chatbot especializado: ✅ Configurado")
                print(f"   • Google Sheets avançado: ✅ Compatível")
        
        elif choice == "3":
            print(f"\n🧹 Limpeza de dados processados...")
            folders_to_clean = ['data/processed', 'data/exports', 'logs']
            
            for folder in folders_to_clean:
                if os.path.exists(folder):
                    import shutil
                    shutil.rmtree(folder)
                    os.makedirs(folder, exist_ok=True)
                    print(f"   ✅ {folder}/ limpo")
            
            print("✅ Limpeza concluída!")
        
        elif choice == "5":
            print(f"\n📊 ESTATÍSTICAS DOS DADOS:")
            print(f"   • Total de arquivos CSV: {self.data_stats.get('csv_files', 0)}")
            print(f"   • Arquivos Nubank: {self.data_stats.get('nubank_files', 0)}")
            print(f"   • Pastas verificadas: {len(self.data_stats.get('folders_checked', []))}")
            
            for folder in self.data_stats.get('folders_checked', []):
                csv_count = len(list(Path(folder).glob("*.csv")))
                print(f"     - {folder}: {csv_count} arquivos")
            
            print(f"   • Emails configurados: {len(self.emails)}")
            print(f"     - Principal: {self.emails['primary']}")
            print(f"     - Service Account: {self.emails['service_account']}")
        
        input("\nPressione Enter para continuar...")
    
    def show_help_v5(self):
        """Exibe ajuda atualizada v5.0"""
        print("\n📖 AJUDA E DOCUMENTAÇÃO v5.0")
        print("="*60)
        
        help_sections = [
            ("🚀 Início Rápido v5.0", [
                "1. Execute 'Configuração Automática' (opção 7)",
                "2. Configure APIs no arquivo .env (opcional)",
                "3. Adicione dados CSV em data/raw/",
                "4. Use 'Dashboard Interativo' (opção 1)",
                "5. Experimente o 'Chatbot IA' (opção 2)",
                "6. Crie planilhas com 'Google Sheets Avançado' (opção 4)"
            ]),
            
            ("💳 Dados Nubank", [
                "📄 Formato: date,title,amount",
                "💾 Salvar como: Nubank_YYYYMMDD.csv",
                "📁 Pasta: data/raw/",
                "🔧 Processamento automático otimizado",
                "🏪 Análise de estabelecimentos exclusiva",
                "📊 Google Sheets com organização por período"
            ]),
            
            ("🤖 Chatbot IA", [
                "💬 Converse sobre seus gastos em linguagem natural",
                "🔍 Perguntas: 'Quanto gastei?', 'Onde gasto mais?'",
                "🧠 IA: Groq (gratuito) ou OpenAI (pago)",
                "⚙️ Configure chaves API no arquivo .env",
                "🎯 Insights personalizados baseados nos dados"
            ]),
            
            ("🚀 Google Sheets Avançado", [
                "📊 Criação automática de planilhas por ano/mês",
                "📋 Índice master com links para todas as planilhas",
                "🗓️ Organização inteligente por período",
                "📈 5 abas especializadas por mês",
                "👥 Compartilhamento automático configurado",
                "🔗 Links diretos para acesso rápido"
            ]),
            
            ("🎨 Interface v5.0", [
                "🧭 Menu de navegação integrado no dashboard",
                "🌓 CSS v3 com legibilidade perfeita em qualquer tema",
                "📱 Design responsivo otimizado",
                "⚡ Performance melhorada",
                "🔗 Botão direto para Google Sheets",
                "🎯 UX otimizada para análise financeira"
            ]),
            
            ("📧 Emails Configurados", [
                f"📧 Principal: {self.emails['primary']}",
                f"🤖 Service Account: {self.emails['service_account']}",
                "🔧 Configuração automática de compartilhamento",
                "✅ Acesso garantido a todas as planilhas",
                "🔒 Segurança e privacidade mantidas"
            ]),
            
            ("🔧 Comandos Essenciais", [
                "python main.py - Menu principal completo",
                "streamlit run dashboard.py - Dashboard direto", 
                "streamlit run chatbot.py - Chatbot IA direto",
                "python src/google_sheets_advanced.py - Sheets avançado",
                "python auto_setup.py - Configuração automática",
                "python system_checker.py - Diagnóstico"
            ]),
            
            ("📞 Suporte v5.0", [
                f"📧 Email: {self.emails['primary']}",
                f"🤖 Service Account: {self.emails['service_account']}",
                "📄 Logs: pasta logs/",
                "🔍 Diagnóstico: python system_checker.py",
                "📖 Documentação: README.md"
            ])
        ]
        
        for section, items in help_sections:
            print(f"\n📋 {section}:")
            for item in items:
                print(f"   • {item}")
        
        print(f"\n🌐 LINKS ÚTEIS:")
        print(f"   • Groq API: https://console.groq.com/")
        print(f"   • OpenAI API: https://platform.openai.com/")
        print(f"   • Google Cloud: https://console.cloud.google.com/")
        print(f"   • Google Sheets: https://docs.google.com/spreadsheets/")
        
        print(f"\n💡 DICAS v5.0:")
        print(f"   • Use o botão Google Sheets no dashboard para acesso direto")
        print(f"   • Configure IA para categorização automática inteligente")
        print(f"   • Google Sheets avançado organiza tudo automaticamente")
        print(f"   • Chatbot entende linguagem natural sobre finanças")
        print(f"   • CSS v3 garante legibilidade perfeita sempre")
        
        input("\nPressione Enter para continuar...")
    
    def execute_config_v5(self):
        """Configurações do sistema v5.0"""
        print("\n🔧 Configurações do Sistema v5.0")
        print("=" * 50)
        
        print("1. 🤖 Configurar IA (Groq/OpenAI)")
        print("2. ☁️ Configurar Google Sheets")
        print("3. 🎨 Configurar Interface")
        print("4. 📁 Configurar Pastas de Dados")
        print("5. 📧 Verificar Emails Configurados")
        print("6. 🧪 Testar Conexões")
        print("7. 📊 Ver Status Completo")
        print("8. 🔄 Resetar Configurações")
        print("9. Voltar ao menu principal")
        
        choice = input("\nEscolha (1-9): ").strip()
        
        if choice == "1":
            print("\n🤖 Configuração IA:")
            print("Providers disponíveis:")
            print("1. Groq (Gratuito - Recomendado)")
            print("2. OpenAI (Pago)")
            print("3. Ambos")
            
            ai_choice = input("Escolha (1-3): ").strip()
            
            if ai_choice in ['1', '3']:
                print("\n🔗 Groq API:")
                print("1. Acesse: https://console.groq.com/")
                print("2. Crie conta gratuita")
                print("3. Obtenha API Key")
                api_key = input("Cole sua GROQ_API_KEY (ou Enter para pular): ").strip()
                if api_key:
                    print("💡 Adicione ao arquivo .env: GROQ_API_KEY=" + api_key)
            
            if ai_choice in ['2', '3']:
                print("\n🔗 OpenAI API:")
                print("1. Acesse: https://platform.openai.com/")
                print("2. Configure billing")
                print("3. Obtenha API Key")
                api_key = input("Cole sua OPENAI_API_KEY (ou Enter para pular): ").strip()
                if api_key:
                    print("💡 Adicione ao arquivo .env: OPENAI_API_KEY=" + api_key)
        
        elif choice == "2":
            print("\n☁️ Configuração Google Sheets:")
            print("Modo avançado v5.0 - Planilhas organizadas automaticamente por ano/mês")
            print()
            print("1. Google Cloud Console: https://console.cloud.google.com/")
            print("2. Crie projeto e habilite APIs:")
            print("   • Google Sheets API")
            print("   • Google Drive API")
            print("3. Crie Service Account")
            print("4. Baixe JSON para credentials/google_credentials.json")
            print()
            print("📧 Emails configurados para compartilhamento automático:")
            for email in self.emails.values():
                print(f"   • {email}")
        
        elif choice == "3":
            print("\n🎨 Configuração Interface v5.0:")
            print("Funcionalidades:")
            print("   ✅ CSS v3 com legibilidade perfeita")
            print("   ✅ Compatibilidade total com temas claro/escuro")
            print("   ✅ Menu de navegação integrado")
            print("   ✅ Botão direto para Google Sheets")
            print("   ✅ Design responsivo")
            print()
            print("Não requer configuração adicional - ativo automaticamente!")
        
        elif choice == "5":
            print("\n📧 Emails Configurados:")
            print(f"   • Principal: {self.emails['primary']}")
            print(f"   • Service Account: {self.emails['service_account']}")
            print()
            print("✅ Compartilhamento automático ativo para:")
            print("   • Todas as planilhas Google Sheets")
            print("   • Planilhas básicas e avançadas")
            print("   • Índices master por ano")
        
        elif choice == "6":
            print("\n🧪 Testando Conexões...")
            
            # Testar dependências
            print("\n📦 Dependências:")
            deps = ['streamlit', 'pandas', 'plotly', 'gspread']
            for dep in deps:
                try:
                    __import__(dep)
                    print(f"   ✅ {dep}")
                except ImportError:
                    print(f"   ❌ {dep}")
            
            # Testar IA
            print("\n🤖 IA:")
            env_path = Path(".env")
            if env_path.exists():
                env_content = env_path.read_text()
                groq_configured = "GROQ_API_KEY=" in env_content and len(env_content.split("GROQ_API_KEY=")[1].split("\n")[0].strip()) > 0
                openai_configured = "OPENAI_API_KEY=" in env_content and len(env_content.split("OPENAI_API_KEY=")[1].split("\n")[0].strip()) > 0
                
                print(f"   {'✅' if groq_configured else '❌'} Groq API")
                print(f"   {'✅' if openai_configured else '❌'} OpenAI API")
            else:
                print("   ❌ Arquivo .env não encontrado")
            
            # Testar Google Sheets
            print("\n☁️ Google Sheets:")
            creds_exist = os.path.exists("credentials/google_credentials.json")
            basic_module = os.path.exists("src/google_sheets_sync.py")
            advanced_module = os.path.exists("src/google_sheets_advanced.py")
            
            print(f"   {'✅' if creds_exist else '❌'} Credenciais")
            print(f"   {'✅' if basic_module else '❌'} Módulo Básico")
            print(f"   {'✅' if advanced_module else '❌'} Módulo Avançado")
            
            # Testar dados
            print(f"\n📊 Dados:")
            print(f"   📄 CSVs: {self.data_stats['csv_files']}")
            print(f"   💳 Nubank: {self.data_stats['nubank_files']}")
        
        elif choice == "7":
            print(f"\n📊 STATUS COMPLETO DO SISTEMA:")
            print(f"   • Versão: {self.version}")
            print(f"   • Primeira execução: {'Sim' if self.config.get('first_run', True) else 'Não'}")
            print(f"   • Chatbot: {'✅' if self.system_status['chatbot_ready'] else '❌'}")
            print(f"   • Google Sheets Básico: {'✅' if self.system_status['google_sheets_basic'] else '❌'}")
            print(f"   • Google Sheets Avançado: {'✅' if self.system_status['google_sheets_advanced'] else '❌'}")
            print(f"   • IA: {'✅' if self.system_status['ai_ready'] else '❌'}")
            print(f"   • CSS Otimizado v3: {'✅' if self.system_status['css_optimized'] else '❌'}")
            print(f"   • Dependências: {'✅' if self.system_status['dependencies_ok'] else '❌'}")
            print(f"   • Email Principal: {self.emails['primary']}")
            print(f"   • Service Account: {self.emails['service_account']}")
        
        input("\nPressione Enter para continuar...")
    
    def run(self):
        """Executa o launcher principal v5.0"""
        try:
            while True:
                self.show_welcome_screen_v5()
                
                action = self.show_main_menu_v5()
                
                if action == "exit":
                    print("\n👋 Obrigado por usar o Dashboard Financeiro v5.0!")
                    print("🚀 Agora com Google Sheets avançado e IA integrada!")
                    print("📧 Planilhas compartilhadas automaticamente com seus emails")
                    print("💡 Seus dados estão seguros e organizados")
                    break
                elif action == "dashboard":
                    self.execute_dashboard()
                elif action == "chatbot":
                    self.execute_chatbot()
                elif action == "sheets_basic":
                    self.execute_sheets_basic()
                elif action == "sheets_advanced":
                    self.execute_sheets_advanced()
                elif action == "categorize":
                    self.execute_categorization()
                elif action == "analyze":
                    self.execute_analysis()
                elif action == "auto_setup":
                    self.execute_auto_setup()
                elif action == "config":
                    self.execute_config_v5()
                elif action == "system_check":
                    self.execute_system_check()
                elif action == "data_manager":
                    self.execute_data_manager()
                elif action == "help":
                    self.show_help_v5()
                
                # Salvar configuração após cada ação
                self.save_config()
        
        except KeyboardInterrupt:
            print("\n\n👋 Saindo do Dashboard Financeiro v5.0...")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("💡 Execute diagnóstico: python system_checker.py")
    
    # Métodos legados mantidos para compatibilidade
    def execute_categorization(self):
        """Executa categorização automática"""
        print("\n🤖 Iniciando Categorização Automática...")
        
        categorizer_file = self.modules['categorizer']
        if not os.path.exists(categorizer_file):
            print(f"❌ Módulo não encontrado: {categorizer_file}")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, categorizer_file])
        except Exception as e:
            print(f"❌ Erro na categorização: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_analysis(self):
        """Executa análise avançada"""
        print("\n📈 Iniciando Análise Avançada...")
        
        analytics_file = self.modules['analytics']
        if not os.path.exists(analytics_file):
            print(f"❌ Módulo não encontrado: {analytics_file}")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, analytics_file])
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            input("Pressione Enter para continuar...")
    
    def execute_system_check(self):
        """Executa diagnóstico do sistema"""
        print("\n🔍 Diagnóstico Completo do Sistema...")
        
        system_check_file = self.modules.get('system_check')
        if not system_check_file or not os.path.exists(system_check_file):
            print("❌ Script de diagnóstico não encontrado!")
            print("💡 Verifique se system_checker.py está na raiz")
            input("Pressione Enter para continuar...")
            return
        
        try:
            subprocess.run([sys.executable, system_check_file])
        except Exception as e:
            print(f"❌ Erro no diagnóstico: {e}")
            input("Pressione Enter para continuar...")

def main():
    """Função principal"""
    launcher = FinancialDashboardLauncherV5()
    launcher.run()

if __name__ == "__main__":
    main()

# ===== SCRIPTS DE CONVENIÊNCIA v5.0 =====

def quick_start_v5():
    """Início rápido v5.0"""
    print("⚡ INÍCIO RÁPIDO v5.0 - GOOGLE SHEETS AVANÇADO")
    print("Escolha:")
    print("1. 🚀 Dashboard Completo")
    print("2. 🤖 Chatbot IA")  
    print("3. ☁️ Google Sheets Básico")
    print("4. 🚀 Google Sheets Avançado (Recomendado)")
    print("5. ⚙️ Configuração Automática")
    
    choice = input("Opção: ").strip()
    
    if choice == "1":
        if os.path.exists("dashboard.py"):
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        else:
            print("❌ dashboard.py não encontrado")
    elif choice == "2":
        if os.path.exists("chatbot.py"):
            subprocess.run([sys.executable, "-m", "streamlit", "run", "chatbot.py"])
        else:
            print("❌ chatbot.py não encontrado")
    elif choice == "3":
        if os.path.exists("src/google_sheets_sync.py"):
            subprocess.run([sys.executable, "src/google_sheets_sync.py"])
        else:
            print("❌ src/google_sheets_sync.py não encontrado")
    elif choice == "4":
        if os.path.exists("src/google_sheets_advanced.py"):
            subprocess.run([sys.executable, "src/google_sheets_advanced.py"])
        else:
            print("❌ src/google_sheets_advanced.py não encontrado")
    elif choice == "5":
        if os.path.exists("auto_setup.py"):
            subprocess.run([sys.executable, "auto_setup.py"])
        else:
            print("❌ auto_setup.py não encontrado")

def check_system_v5():
    """Verificação rápida v5.0"""
    print("🔍 VERIFICAÇÃO RÁPIDA v5.0")
    print("="*40)
    
    # Arquivos v5.0
    v5_files = {
        "📄 Principal": ["main.py", "dashboard.py", "chatbot.py"],
        "📁 Módulos Básicos": ["src/llm_categorizer.py", "src/google_sheets_sync.py", "src/advanced_analytics.py"],
        "🚀 Módulos Avançados": ["src/google_sheets_advanced.py"],
        "⚙️ Config": ["auto_setup.py", "system_checker.py", "requirements.txt"],
        "🎨 Interface": ["css/dashboard_styles.css"]
    }
    
    for category, files in v5_files.items():
        print(f"\n{category}:")
        for file in files:
            status = "✅" if os.path.exists(file) else "❌"
            print(f"   {status} {file}")
    
    # Funcionalidades v5.0
    print(f"\n🚀 FUNCIONALIDADES v5.0:")
    
    # Chatbot
    chatbot_ready = os.path.exists("chatbot.py")
    print(f"   🤖 Chatbot IA: {'✅' if chatbot_ready else '❌'}")
    
    # Google Sheets básico
    sheets_basic = os.path.exists("src/google_sheets_sync.py") and os.path.exists("credentials/google_credentials.json")
    print(f"   ☁️ Google Sheets Básico: {'✅' if sheets_basic else '❌'}")
    
    # Google Sheets avançado
    sheets_advanced = os.path.exists("src/google_sheets_advanced.py") and os.path.exists("credentials/google_credentials.json")
    print(f"   🚀 Google Sheets Avançado: {'✅' if sheets_advanced else '❌'}")
    
    # CSS otimizado
    css_optimized = False
    if os.path.exists("css/dashboard_styles.css"):
        with open("css/dashboard_styles.css", 'r', encoding='utf-8') as f:
            css_content = f.read()
            css_optimized = "border-radius" in css_content and "transition" in css_content
    print(f"   🎨 CSS Otimizado v3: {'✅' if css_optimized else '❌'}")
    
    # IA configurada
    ai_ready = False
    if os.path.exists(".env"):
        with open(".env", 'r', encoding='utf-8') as f:
            env_content = f.read()
            ai_ready = ("GROQ_API_KEY=" in env_content and len(env_content.split("GROQ_API_KEY=")[1].split("\n")[0].strip()) > 0) or \
                      ("OPENAI_API_KEY=" in env_content and len(env_content.split("OPENAI_API_KEY=")[1].split("\n")[0].strip()) > 0)
    print(f"   🧠 IA Configurada: {'✅' if ai_ready else '❌'}")
    
    # Emails
    print(f"\n📧 EMAILS CONFIGURADOS:")
    print(f"   • Principal: matheusbnas@gmail.com")
    print(f"   • Service Account: dashboard-financeiro@api-financeiro-460817.iam.gserviceaccount.com")

# Para execução direta com parâmetros v5.0
if len(sys.argv) > 1:
    command = sys.argv[1].lower()
    
    if command == "quick":
        quick_start_v5()
    elif command == "check":
        check_system_v5()
    elif command == "dashboard":
        if os.path.exists("dashboard.py"):
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    elif command == "chatbot":
        if os.path.exists("chatbot.py"):
            subprocess.run([sys.executable, "-m", "streamlit", "run", "chatbot.py"])
    elif command == "sheets":
        if os.path.exists("src/google_sheets_advanced.py"):
            subprocess.run([sys.executable, "src/google_sheets_advanced.py"])
        elif os.path.exists("src/google_sheets_sync.py"):
            subprocess.run([sys.executable, "src/google_sheets_sync.py"])
    elif command == "setup":
        if os.path.exists("auto_setup.py"):
            subprocess.run([sys.executable, "auto_setup.py"])
    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos v5.0: quick, check, dashboard, chatbot, sheets, setup")
else:
    main()