import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas do Dashboard Financeiro"""
    
    # ============= INFORMAÇÕES DO PROJETO =============
    PROJECT_NAME = "Dashboard Financeiro Completo"
    VERSION = "3.1.0"
    AUTHOR = "Dashboard Financeiro Team"
    DESCRIPTION = "Sistema completo de análise financeira pessoal especializado em Nubank"
    
    # ============= ESTRUTURA DE PASTAS =============
    BASE_DIR = Path(__file__).parent.parent
    
    # Pastas principais
    SRC_DIR = BASE_DIR / "src"
    CONFIG_DIR = BASE_DIR / "config"  
    CSS_DIR = BASE_DIR / "css"
    DATA_DIR = BASE_DIR / "data"
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    
    # Subpastas de dados
    RAW_DATA_PATH = DATA_DIR / "raw"
    PROCESSED_DATA_PATH = DATA_DIR / "processed"
    EXPORTS_PATH = DATA_DIR / "exports"
    UPLOADS_PATH = BASE_DIR / "uploads"
    
    # Logs e backups
    LOGS_DIR = BASE_DIR / "logs"
    BACKUPS_DIR = BASE_DIR / "backups"
    
    # ============= ARQUIVOS PRINCIPAIS =============
    
    # Módulos src/
    LLM_CATEGORIZER_PATH = SRC_DIR / "llm_categorizer.py"
    GOOGLE_SHEETS_SYNC_PATH = SRC_DIR / "google_sheets_sync.py"
    ADVANCED_ANALYTICS_PATH = SRC_DIR / "advanced_analytics.py"
    DATA_PROCESSOR_PATH = SRC_DIR / "data_processor.py"
    
    # Arquivos de configuração
    ENV_FILE = BASE_DIR / ".env"
    CONFIG_JSON = BASE_DIR / "config.json"
    GITIGNORE_FILE = BASE_DIR / ".gitignore"
    
    # Arquivos CSS
    MAIN_CSS_FILE = CSS_DIR / "dashboard_styles.css"
    
    # Cache e dados temporários
    CATEGORIZATION_CACHE = BASE_DIR / "categorization_cache.json"
    
    # ============= GOOGLE SHEETS =============
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', str(CREDENTIALS_DIR / 'google_credentials.json'))
    SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Dashboard Financeiro Pessoal')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    
    # ============= APIs EXTERNAS =============
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
    
    # Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    GROQ_TEMPERATURE = float(os.getenv('GROQ_TEMPERATURE', '0.1'))
    
    # ============= CATEGORIAS FINANCEIRAS =============
    
    # Categorias padrão (otimizadas para Brasil/Nubank)
    EXPENSE_CATEGORIES = [
        'Alimentação',
        'Receitas', 
        'Saúde',
        'Mercado',
        'Educação',
        'Compras',
        'Transporte',
        'Investimento',
        'Transferências para terceiros',
        'Telefone',
        'Moradia',
        'Entretenimento',
        'Lazer',
        'Serviços',
        'Outros'
    ]
    
    # Mapeamento de categorias (aliases)
    CATEGORY_ALIASES = {
        'Supermercado': 'Mercado',
        'Restaurante': 'Alimentação',
        'Posto': 'Transporte',
        'Farmácia': 'Saúde',
        'Shopping': 'Compras',
        'Cinema': 'Entretenimento',
        'Academia': 'Saúde',
        'Uber': 'Transporte',
        'iFood': 'Alimentação'
    }
    
    # ============= PADRÕES DE CUSTOS FIXOS =============
    
    FIXED_COSTS_PATTERNS = {
        'Moradia': [
            'FERREIRA IMOVEIS', 'ALUGUEL', 'CONDOMINIO', 'IPTU',
            'COPEL', 'CEMIG', 'LIGHT', 'ELETROPAULO', 
            'SABESP', 'SANEPAR', 'COMGAS', 'CEG',
            'LUZ', 'ENERGIA', 'ÁGUA', 'AGUA', 'GAS', 'ESGOTO'
        ],
        'Educação': [
            'ESCOLA DE EDUCACAO', 'GREMIO NAUTICO UNIAO',
            'UNIVERSIDADE', 'FACULDADE', 'COLEGIO', 
            'CURSO', 'MENSALIDADE', 'MATERIAL ESCOLAR'
        ],
        'Telefone': [
            'CLARO', 'TIM SA', 'VIVO', 'OI', 'NET', 'SKY',
            'TELEFONICA', 'NEXTEL', 'TELEFONE', 'CELULAR',
            'INTERNET', 'BANDA LARGA'
        ],
        'Transferências para terceiros': [
            'COPE SERVICOS CONTABEIS', 'PIX PROGRAMADO',
            'TRANSFERENCIA PROGRAMADA', 'DEBITO AUTOMATICO'
        ],
        'Saúde': [
            'PLANO DE SAUDE', 'UNIMED', 'BRADESCO SAUDE',
            'PLANO SAUDE', 'CONVENIO MEDICO', 'SEGURO SAUDE'
        ],
        'Transporte': [
            'SEGURO AUTO', 'IPVA', 'LICENCIAMENTO',
            'SEGURO VEICULO', 'FINANCIAMENTO AUTO'
        ],
        'Entretenimento': [
            'NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'DISNEY',
            'GLOBOPLAY', 'YOUTUBE PREMIUM', 'HBO MAX'
        ]
    }
    
    # ============= PADRÕES NUBANK =============
    
    NUBANK_PATTERNS = {
        'Alimentação': [
            'RESTAURANTE', 'LANCHONETE', 'PADARIA', 'PIZZARIA', 
            'HAMBURGUER', 'SUBWAY', 'MCDONALDS', 'BURGER KING', 
            'KFC', 'PIZZA', 'IFOOD', 'UBER EATS', 'RAPPI',
            'BAR ', 'CAFE', 'CAFETERIA', 'AÇOUGUE', 'SORVETERIA'
        ],
        'Mercado': [
            'SUPERMERCADO', 'MERCADO', 'ATACADAO', 'CARREFOUR', 
            'EXTRA', 'WALMART', 'BISTEK', 'ZAFFARI', 'COMERCIAL',
            'MERCEARIA', 'HIPERMERCADO', 'BIG', 'NACIONAL', 'ANGELONI'
        ],
        'Transporte': [
            'POSTO', 'COMBUSTIVEL', 'SHELL', 'PETROBRAS', 'IPIRANGA',
            'BR DISTRIBUIDORA', 'UBER', 'TAXI', '99', 'ONIBUS',
            'METRO', 'ESTACIONAMENTO', 'PEDÁGIO', 'AUTOPASS'
        ],
        'Saúde': [
            'FARMACIA', 'DROGARIA', 'PANVEL', 'DROGASIL', 'PACHECO',
            'UNIMED', 'MEDICO', 'HOSPITAL', 'CLINICA', 'LABORATORIO',
            'DENTISTA', 'PAGUE MENOS', 'ULTRAFARMA'
        ],
        'Compras': [
            'MAGAZINE', 'SHOPPING', 'LOJA', 'AMERICANAS', 'SUBMARINO',
            'MERCADOLIVRE', 'AMAZON', 'ALIEXPRESS', 'SHOPEE',
            'RENNER', 'C&A', 'ZARA', 'H&M'
        ],
        'Entretenimento': [
            'CINEMA', 'TEATRO', 'SHOW', 'INGRESSO', 'BALADA',
            'CLUBE', 'PARQUE', 'MUSEU'
        ],
        'Serviços': [
            'BANCO', 'CAIXA', 'BRADESCO', 'ITAU', 'SANTANDER',
            'CARTORIO', 'DESPACHANTE', 'ADVOCACIA', 'CONTABILIDADE'
        ]
    }
    
    # ============= CONFIGURAÇÕES DE ANÁLISE =============
    
    # Thresholds para alertas
    ALERT_THRESHOLDS = {
        'expense_spike': 1.5,           # 50% acima da média
        'low_savings_rate': 10,         # Menos de 10% de poupança
        'category_limit': 0.3,          # Mais de 30% em uma categoria
        'unusual_transaction': 3,       # 3 desvios padrão
        'recurring_anomaly': 0.2        # 20% de variação em custos fixos
    }
    
    # Configurações do score de saúde financeira
    HEALTH_SCORE_WEIGHTS = {
        'taxa_poupanca': 30,        # Taxa de poupança (30 pontos)
        'diversificacao': 20,       # Diversificação de gastos (20 pontos)
        'estabilidade': 25,         # Estabilidade mensal (25 pontos)
        'controle_gastos': 25       # Controle de gastos grandes (25 pontos)
    }
    
    # Classificação da saúde financeira
    HEALTH_SCORE_CLASSIFICATION = {
        (80, 100): 'Excelente',
        (65, 79): 'Boa', 
        (50, 64): 'Regular',
        (35, 49): 'Ruim',
        (0, 34): 'Crítica'
    }
    
    # ============= CONFIGURAÇÕES DE PROCESSAMENTO =============
    
    # Formatos de arquivo suportados
    SUPPORTED_FILE_FORMATS = ['.csv', '.xlsx', '.xls']
    
    # Encodings para tentar ao carregar CSVs
    CSV_ENCODINGS = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    # Separadores para tentar ao carregar CSVs
    CSV_SEPARATORS = [',', ';', '\t', '|']
    
    # Padrões de detecção de colunas
    COLUMN_DETECTION_PATTERNS = {
        'Data': ['data', 'date', 'dt', 'timestamp', 'time'],
        'Valor': ['valor', 'value', 'amount', 'montante', 'quantia'],
        'Descrição': ['descricao', 'descrição', 'description', 'memo', 'observacao', 'historic'],
        'Categoria': ['categoria', 'category', 'tipo', 'class'],
        'ID': ['id', 'codigo', 'código', 'reference', 'ref']
    }
    
    # ============= CONFIGURAÇÕES DE INTERFACE =============
    
    # Configuração do Streamlit
    STREAMLIT_CONFIG = {
        'page_title': '💰 Dashboard Financeiro Avançado',
        'page_icon': '💰',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }
    
    # Cores do tema
    THEME_COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent_blue': '#3498db',
        'accent_green': '#27ae60',
        'accent_red': '#e74c3c',
        'accent_purple': '#8b2fff',
        'nubank_purple': '#8b2fff'
    }
    
    # ============= CONFIGURAÇÕES DE CACHE =============
    
    # TTL para cache do Streamlit (em segundos)
    CACHE_TTL = 300  # 5 minutos
    
    # Tamanho máximo do cache de categorização
    MAX_CACHE_SIZE = 10000
    
    # ============= CONFIGURAÇÕES DE LOGGING =============
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # ============= CONFIGURAÇÕES DE BACKUP =============
    
    # Manter backups por quantos dias
    BACKUP_RETENTION_DAYS = 30
    
    # Tamanho máximo de backup (MB)
    MAX_BACKUP_SIZE_MB = 100
    
    # ============= CONFIGURAÇÕES DE PERFORMANCE =============
    
    # Limite de transações para processamento rápido
    FAST_PROCESSING_LIMIT = 10000
    
    # Tamanho do batch para processamento em lote
    BATCH_SIZE = 1000
    
    # ============= MÉTODOS UTILITÁRIOS =============
    
    @classmethod
    def ensure_directories(cls):
        """Cria todas as pastas necessárias se não existirem"""
        directories = [
            cls.SRC_DIR,
            cls.CONFIG_DIR,
            cls.CSS_DIR,
            cls.DATA_DIR,
            cls.RAW_DATA_PATH,
            cls.PROCESSED_DATA_PATH,
            cls.EXPORTS_PATH,
            cls.UPLOADS_PATH,
            cls.CREDENTIALS_DIR,
            cls.LOGS_DIR,
            cls.BACKUPS_DIR
        ]
        
        created_dirs = []
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(directory))
        
        return created_dirs
    
    @classmethod
    def check_required_files(cls):
        """Verifica se arquivos obrigatórios existem"""
        required_files = {
            'main.py': cls.BASE_DIR / 'main.py',
            'dashboard.py': cls.BASE_DIR / 'dashboard.py',
            'requirements.txt': cls.BASE_DIR / 'requirements.txt',
            '.env': cls.ENV_FILE,
            'src/__init__.py': cls.SRC_DIR / '__init__.py'
        }
        
        status = {}
        for name, path in required_files.items():
            status[name] = path.exists()
        
        return status
    
    @classmethod
    def check_src_modules(cls):
        """Verifica status dos módulos em src/"""
        modules = {
            'llm_categorizer': cls.LLM_CATEGORIZER_PATH,
            'google_sheets_sync': cls.GOOGLE_SHEETS_SYNC_PATH,
            'advanced_analytics': cls.ADVANCED_ANALYTICS_PATH,
            'data_processor': cls.DATA_PROCESSOR_PATH
        }
        
        status = {}
        for name, path in modules.items():
            status[name] = path.exists()
        
        return status
    
    @classmethod
    def get_health_classification(cls, score):
        """Retorna classificação baseada no score de saúde"""
        for (min_score, max_score), classification in cls.HEALTH_SCORE_CLASSIFICATION.items():
            if min_score <= score <= max_score:
                return classification
        return 'Indefinida'
    
    @classmethod
    def is_fixed_cost(cls, description, category=None):
        """Verifica se uma transação é custo fixo baseado na descrição"""
        if not description:
            return False
        
        description_upper = description.upper()
        
        # Verificar por categoria específica
        if category and category in cls.FIXED_COSTS_PATTERNS:
            patterns = cls.FIXED_COSTS_PATTERNS[category]
            return any(pattern in description_upper for pattern in patterns)
        
        # Verificar em todos os padrões
        for patterns in cls.FIXED_COSTS_PATTERNS.values():
            if any(pattern in description_upper for pattern in patterns):
                return True
        
        return False
    
    @classmethod
    def categorize_by_patterns(cls, description):
        """Categoriza baseado nos padrões do Nubank"""
        if not description:
            return 'Outros'
        
        description_upper = description.upper()
        
        for category, patterns in cls.NUBANK_PATTERNS.items():
            if any(pattern in description_upper for pattern in patterns):
                return category
        
        return 'Outros'
    
    @classmethod
    def get_project_info(cls):
        """Retorna informações do projeto"""
        return {
            'name': cls.PROJECT_NAME,
            'version': cls.VERSION,
            'author': cls.AUTHOR,
            'description': cls.DESCRIPTION,
            'base_dir': str(cls.BASE_DIR),
            'structure_type': 'src_organized'
        }
    
    @classmethod
    def diagnose_system(cls):
        """Diagnóstico completo do sistema"""
        print("🔍 DIAGNÓSTICO DO SISTEMA")
        print("=" * 50)
        
        # Informações do projeto
        info = cls.get_project_info()
        print(f"\n📋 Projeto: {info['name']} v{info['version']}")
        print(f"📁 Base: {info['base_dir']}")
        print(f"🏗️ Estrutura: {info['structure_type']}")
        
        # Verificar pastas
        print(f"\n📁 ESTRUTURA DE PASTAS:")
        created_dirs = cls.ensure_directories()
        if created_dirs:
            print(f"   ✅ Criadas: {len(created_dirs)} pastas")
            for dir in created_dirs:
                print(f"      📁 {dir}")
        else:
            print(f"   ✅ Todas as pastas existem")
        
        # Verificar arquivos obrigatórios
        print(f"\n📄 ARQUIVOS OBRIGATÓRIOS:")
        required_status = cls.check_required_files()
        for file, exists in required_status.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {file}")
        
        # Verificar módulos src/
        print(f"\n🔧 MÓDULOS src/:")
        modules_status = cls.check_src_modules()
        for module, exists in modules_status.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {module}.py")
        
        # Verificar APIs
        print(f"\n🔑 CONFIGURAÇÃO DE APIs:")
        print(f"   {'✅' if cls.OPENAI_API_KEY else '❌'} OpenAI API Key")
        print(f"   {'✅' if cls.GROQ_API_KEY else '❌'} Groq API Key") 
        print(f"   {'✅' if Path(cls.GOOGLE_CREDENTIALS_PATH).exists() else '❌'} Google Credentials")
        
        # Estatísticas
        total_required = len(required_status)
        total_modules = len(modules_status)
        required_ok = sum(required_status.values())
        modules_ok = sum(modules_status.values())
        
        print(f"\n📊 RESUMO:")
        print(f"   • Arquivos obrigatórios: {required_ok}/{total_required}")
        print(f"   • Módulos src/: {modules_ok}/{total_modules}")
        print(f"   • Integridade: {((required_ok + modules_ok) / (total_required + total_modules) * 100):.1f}%")
        
        return {
            'required_files': required_status,
            'src_modules': modules_status,
            'created_directories': created_dirs,
            'integrity_score': (required_ok + modules_ok) / (total_required + total_modules) * 100
        }

# ============= CONFIGURAÇÕES ESPECÍFICAS POR AMBIENTE =============

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CACHE_TTL = 60  # Cache mais curto em desenvolvimento

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    CACHE_TTL = 600  # Cache mais longo em produção

class TestingConfig(Config):
    """Configurações para testes"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    # Usar pastas temporárias para testes
    DATA_DIR = Config.BASE_DIR / "test_data"
    RAW_DATA_PATH = DATA_DIR / "raw"
    PROCESSED_DATA_PATH = DATA_DIR / "processed"

# ============= SELEÇÃO DE CONFIGURAÇÃO =============

def get_config():
    """Retorna a configuração baseada na variável de ambiente"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

# Instância padrão
current_config = get_config()

# ============= FUNÇÕES DE CONVENIÊNCIA =============

def diagnose():
    """Função de conveniência para diagnóstico"""
    return current_config.diagnose_system()

def ensure_setup():
    """Garante que a estrutura básica está configurada"""
    current_config.ensure_directories()
    return True

def get_src_modules_status():
    """Retorna status dos módulos src/"""
    return current_config.check_src_modules()

if __name__ == "__main__":
    # Executar diagnóstico se chamado diretamente
    diagnose()