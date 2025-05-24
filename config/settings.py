import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Sheets
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google_credentials.json')
    SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Dashboard Financeiro')
    FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    # Caminhos
    RAW_DATA_PATH = 'data/raw'
    PROCESSED_DATA_PATH = 'data/processed'
    EXPORTS_PATH = 'data/exports'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Categorias
    EXPENSE_CATEGORIES = [
        'Alimentação', 'Receitas', 'Saúde', 'Mercado', 'Educação',
        'Compras', 'Transporte', 'Investimento', 'Transferências para terceiros',
        'Telefone', 'Moradia', 'Entretenimento', 'Lazer'
    ]
    
    # Custos Fixos (padrões reconhecidos)
    FIXED_COSTS_PATTERNS = {
        'Moradia': ['FERREIRA IMOVEIS', 'ALUGUEL', 'CONDOMINIO'],
        'Educação': ['ESCOLA DE EDUCACAO', 'GREMIO NAUTICO UNIAO'],
        'Telefone': ['CLARO', 'TIM SA', 'VIVO'],
        'Transferências para terceiros': ['COPE SERVICOS CONTABEIS'],
        'Saúde': ['PLANO DE SAUDE', 'UNIMED']
    }
