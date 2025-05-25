#!/usr/bin/env python3
"""
Script de configuração automática do Dashboard Financeiro
Executa: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def create_project_structure():
    """Cria a estrutura de pastas do projeto"""
    print("📁 Criando estrutura de pastas...")
    
    folders = [
        'config',
        'src', 
        'data/raw',
        'data/processed',
        'data/exports',
        'credentials'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {folder}/")
    
    # Criar arquivos __init__.py
    init_files = ['config/__init__.py', 'src/__init__.py', 'data/__init__.py']
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)
        print(f"  ✅ {init_file}")

def create_gitignore():
    """Cria arquivo .gitignore"""
    print("🔒 Criando .gitignore...")
    
    gitignore_content = """# Dados sensíveis
.env
data/raw/*.csv
credentials/
*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Streamlit
.streamlit/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("  ✅ .gitignore criado")

def create_requirements():
    """Cria arquivo requirements.txt"""
    print("📦 Criando requirements.txt...")
    
    requirements = """streamlit
pandas
plotly
gspread
oauth2client
python-dotenv
ofxparse
langchain-openai
langchain-groq
langchain-core
numpy
openpyxl
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("  ✅ requirements.txt criado")

def create_env_template():
    """Cria template do arquivo .env"""
    print("⚙️ Criando template .env...")
    
    env_template = """# Google Sheets
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
SPREADSHEET_NAME=Dashboard Financeiro Pessoal
GOOGLE_DRIVE_FOLDER_ID=

# APIs (opcional para categorização automática)
OPENAI_API_KEY=
GROQ_API_KEY=
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("  ✅ .env criado (configure suas chaves)")
    else:
        print("  ℹ️ .env já existe (mantendo configuração atual)")

def install_dependencies():
    """Instala dependências do Python"""
    print("🚀 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("  ✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError:
        print("  ❌ Erro ao instalar dependências")
        print("     Execute manualmente: pip install -r requirements.txt")

def create_readme():
    """Cria README.md básico"""
    print("📖 Criando README.md...")
    
    readme_content = """# 💰 Dashboard Financeiro Avançado

Dashboard para análise de gastos pessoais com integração ao Google Sheets.

## 🚀 Início Rápido

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar Google Sheets:**
   - Siga o guia de configuração
   - Coloque credenciais em `credentials/google_credentials.json`
   - Configure `.env` com suas informações

3. **Adicionar dados:**
   - Coloque CSVs do Nubank em `data/raw/`

4. **Executar dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

## 📊 Funcionalidades

- ✅ Análise de receitas vs despesas
- ✅ Identificação automática de custos fixos
- ✅ Tendências e previsões
- ✅ Sincronização com Google Sheets
- ✅ Visualizações interativas
- ✅ Dados seguros (não versionados)

## 🛡️ Segurança

- CSVs bancários não são versionados
- Credenciais protegidas no .gitignore
- Processamento local dos dados

## 📞 Suporte

Consulte o guia de instalação completo para configuração detalhada.
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("  ✅ README.md criado")

def create_sample_data():
    """Cria arquivo de exemplo na pasta data/raw"""
    print("📄 Criando arquivo de exemplo...")
    
    sample_content = """# INSTRUÇÕES
# 
# 1. Baixe seus extratos do Nubank em formato CSV
# 2. Coloque todos os arquivos .csv nesta pasta (data/raw/)
# 3. Execute o dashboard: streamlit run dashboard.py
#
# IMPORTANTE: Esta pasta está no .gitignore por segurança!
# Seus dados bancários não serão versionados no Git.
#
# Formato esperado do CSV:
# ID,Data,Valor,Descrição,Categoria
# 20240101001,2024-01-01,-50.00,SUPERMERCADO XYZ,Alimentação
# 20240101002,2024-01-01,3000.00,SALARIO EMPRESA,Receitas
"""
    
    with open('data/raw/README.txt', 'w') as f:
        f.write(sample_content)
    print("  ✅ Instruções criadas em data/raw/README.txt")

def main():
    """Função principal de configuração"""
    print("🚀 Configurando Dashboard Financeiro Avançado...")
    print("=" * 50)
    
    try:
        create_project_structure()
        print()
        
        create_gitignore()
        print()
        
        create_requirements()
        print()
        
        create_env_template()
        print()
        
        create_readme()
        print()
        
        create_sample_data()
        print()
        
        print("🎯 Instalando dependências...")
        install_dependencies()
        print()
        
        print("✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 50)
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Configure Google Sheets API (veja README.md)")
        print("2. Edite .env com suas credenciais")
        print("3. Coloque CSVs do Nubank em data/raw/")
        print("4. Execute: streamlit run dashboard.py")
        print()
        print("🔒 SEGURANÇA: Seus dados estão protegidos pelo .gitignore")
        print("📖 Consulte README.md para instruções detalhadas")
        
    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# ===== SCRIPT ADICIONAL: verify_setup.py =====
def verify_setup():
    """Verifica se a configuração está correta"""
    print("🔍 Verificando configuração...")
    
    checks = [
        ("📁 Estrutura de pastas", [
            "config", "src", "data/raw", "data/processed", 
            "data/exports", "credentials"
        ]),
        ("📄 Arquivos essenciais", [
            "requirements.txt", ".gitignore", ".env", "README.md"
        ]),
        ("🐍 Arquivos Python", [
            "config/__init__.py", "src/__init__.py"
        ])
    ]
    
    all_good = True
    
    for check_name, items in checks:
        print(f"\n{check_name}:")
        for item in items:
            if os.path.exists(item):
                print(f"  ✅ {item}")
            else:
                print(f"  ❌ {item} - FALTANDO!")
                all_good = False
    
    print(f"\n{'✅ TUDO OK!' if all_good else '❌ CONFIGURAÇÃO INCOMPLETA'}")
    
    # Verificar dependências
    print("\n📦 Verificando dependências:")
    try:
        import streamlit
        import pandas
        import plotly
        print("  ✅ Dependências principais instaladas")
    except ImportError as e:
        print(f"  ❌ Dependência faltando: {e}")
        all_good = False
    
    # Verificar dados
    print("\n📊 Verificando dados:")
    csv_files = list(Path("data/raw").glob("*.csv"))
    if csv_files:
        print(f"  ✅ {len(csv_files)} arquivo(s) CSV encontrado(s)")
    else:
        print("  ⚠️ Nenhum CSV encontrado em data/raw/")
    
    # Verificar credenciais
    print("\n🔑 Verificando credenciais:")
    if os.path.exists("credentials/google_credentials.json"):
        print("  ✅ Credenciais Google encontradas")
    else:
        print("  ⚠️ Credenciais Google não configuradas")
    
    return all_good

# Para verificar configuração, execute:
# python -c "from setup import verify_setup; verify_setup()"