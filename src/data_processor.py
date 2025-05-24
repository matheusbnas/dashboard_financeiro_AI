import pandas as pd
import os
from datetime import datetime, timedelta
import glob
from config.settings import Config

class DataProcessor:
    def __init__(self):
        self.config = Config()
        
    def load_csv_files(self):
        """Carrega todos os CSVs da pasta raw"""
        csv_files = glob.glob(f"{self.config.RAW_DATA_PATH}/*.csv")
        
        if not csv_files:
            print("Nenhum arquivo CSV encontrado na pasta data/raw/")
            return pd.DataFrame()
        
        dfs = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                df['arquivo_origem'] = os.path.basename(file)
                dfs.append(df)
                print(f"Arquivo carregado: {file}")
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")
        
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            return self.process_data(combined_df)
        return pd.DataFrame()
    
    def process_data(self, df):
        """Processa e limpa os dados"""
        # Converter data
        df['Data'] = pd.to_datetime(df['Data'])
        df['Mes'] = df['Data'].dt.to_period('M')
        df['Ano'] = df['Data'].dt.year
        df['Mes_Nome'] = df['Data'].dt.strftime('%B')
        
        # Limpar valores
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        
        # Separar receitas e despesas
        df['Tipo'] = df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
        df['Valor_Absoluto'] = df['Valor'].abs()
        
        # Remover duplicatas
        df = df.drop_duplicates(subset=['ID'], keep='first')
        
        return df
    
    def identify_fixed_costs(self, df):
        """Identifica custos fixos vs variáveis"""
        df['Custo_Tipo'] = 'Variável'
        
        for categoria, patterns in self.config.FIXED_COSTS_PATTERNS.items():
            for pattern in patterns:
                mask = (df['Categoria'] == categoria) & \
                       (df['Descrição'].str.contains(pattern, case=False, na=False))
                df.loc[mask, 'Custo_Tipo'] = 'Fixo'
        
        # Identificar custos que se repetem mensalmente
        monthly_expenses = df[df['Tipo'] == 'Despesa'].groupby(['Descrição', 'Mes']).size().reset_index(name='count')
        recurring_descriptions = monthly_expenses.groupby('Descrição')['count'].count()
        fixed_descriptions = recurring_descriptions[recurring_descriptions >= 3].index
        
        df.loc[df['Descrição'].isin(fixed_descriptions), 'Custo_Tipo'] = 'Fixo'
        
        return df
    
    def save_processed_data(self, df):
        """Salva dados processados"""
        os.makedirs(self.config.PROCESSED_DATA_PATH, exist_ok=True)
        filepath = f"{self.config.PROCESSED_DATA_PATH}/dados_processados.csv"
        df.to_csv(filepath, index=False)
        print(f"Dados salvos em: {filepath}")
        return filepath