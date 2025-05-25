"""
Google Sheets Sync - Módulo para sincronização com Google Sheets
Execute: python google_sheets_sync.py
"""

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
import glob

class GoogleSheetsSync:
    def __init__(self, credentials_path="credentials/google_credentials.json"):
        """
        Inicializa conexão com Google Sheets
        
        Args:
            credentials_path: Caminho para arquivo de credenciais JSON
        """
        self.credentials_path = credentials_path
        self.client = None
        self.spreadsheet = None
        self.connect()
    
    def connect(self):
        """Conecta com Google Sheets API"""
        try:
            # Verificar se arquivo de credenciais existe
            if not os.path.exists(self.credentials_path):
                print(f"❌ Arquivo de credenciais não encontrado: {self.credentials_path}")
                print("\n📋 Como configurar:")
                print("1. Acesse: https://console.cloud.google.com/")
                print("2. Crie um projeto ou selecione existente")
                print("3. Habilite Google Sheets API e Google Drive API")
                print("4. Crie credenciais de Service Account")
                print("5. Baixe o JSON e coloque em 'credentials/google_credentials.json'")
                return False
            
            # Configurar escopos
            scopes = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            
            # Criar credenciais
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                filename=self.credentials_path,
                scopes=scopes
            )
            
            # Autorizar cliente
            self.client = gspread.authorize(creds)
            print("✅ Conectado ao Google Sheets com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar com Google Sheets: {e}")
            return False
    
    def create_or_open_spreadsheet(self, spreadsheet_name="Dashboard Financeiro"):
        """
        Cria ou abre planilha no Google Sheets
        
        Args:
            spreadsheet_name: Nome da planilha
        """
        if not self.client:
            print("❌ Cliente não conectado")
            return False
        
        try:
            # Tentar abrir planilha existente
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
                print(f"📊 Planilha '{spreadsheet_name}' encontrada!")
            except gspread.SpreadsheetNotFound:
                # Criar nova planilha
                self.spreadsheet = self.client.create(spreadsheet_name)
                print(f"📊 Nova planilha '{spreadsheet_name}' criada!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao abrir/criar planilha: {e}")
            return False
    
    def upload_dataframe(self, df, worksheet_name, clear_first=True):
        """
        Faz upload de DataFrame para worksheet específico
        
        Args:
            df: DataFrame do pandas
            worksheet_name: Nome da aba
            clear_first: Limpar dados existentes antes do upload
        """
        if not self.spreadsheet:
            print("❌ Planilha não inicializada")
            return False
        
        try:
            # Criar ou obter worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                if clear_first:
                    worksheet.clear()
            except gspread.WorksheetNotFound:
                # Criar nova aba
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=len(df) + 10,
                    cols=len(df.columns) + 5
                )
            
            # Preparar dados para upload
            # Cabeçalhos
            headers = df.columns.tolist()
            
            # Converter dados para lista de listas
            data = []
            data.append(headers)  # Adicionar cabeçalhos
            
            for index, row in df.iterrows():
                row_data = []
                for col in df.columns:
                    value = row[col]
                    
                    # Tratar diferentes tipos de dados
                    if pd.isna(value):
                        row_data.append("")
                    elif isinstance(value, datetime):
                        row_data.append(value.strftime("%d/%m/%Y"))
                    elif hasattr(value, 'strftime'):  # Period, Date, etc.
                        try:
                            row_data.append(str(value))
                        except:
                            row_data.append("")
                    else:
                        row_data.append(str(value))
                
                data.append(row_data)
            
            # Upload dados
            worksheet.update(data, value_input_option='USER_ENTERED')
            
            print(f"✅ Dados enviados para aba '{worksheet_name}' ({len(df)} linhas)")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao fazer upload: {e}")
            return False
    
    def create_summary_sheets(self, df):
        """Cria planilhas de resumo a partir do DataFrame"""
        
        if df.empty:
            print("❌ DataFrame vazio")
            return False
        
        print("📊 Criando planilhas de resumo...")
        
        # 1. Resumo Mensal
        try:
            monthly_summary = df.groupby(['Mes_Str', 'Tipo']).agg({
                'Valor_Absoluto': 'sum'
            }).reset_index()
            
            monthly_pivot = monthly_summary.pivot(
                index='Mes_Str', 
                columns='Tipo', 
                values='Valor_Absoluto'
            ).fillna(0)
            
            monthly_pivot['Saldo'] = monthly_pivot.get('Receita', 0) - monthly_pivot.get('Despesa', 0)
            monthly_pivot['Taxa_Poupanca_%'] = (monthly_pivot['Saldo'] / monthly_pivot.get('Receita', 1) * 100).round(2)
            
            monthly_pivot_reset = monthly_pivot.reset_index()
            self.upload_dataframe(monthly_pivot_reset, "Resumo_Mensal")
            
        except Exception as e:
            print(f"❌ Erro no resumo mensal: {e}")
        
        # 2. Resumo por Categoria
        try:
            category_summary = df[df['Tipo'] == 'Despesa'].groupby('Categoria').agg({
                'Valor_Absoluto': ['sum', 'count', 'mean']
            }).round(2)
            
            category_summary.columns = ['Total', 'Quantidade', 'Media']
            category_summary = category_summary.sort_values('Total', ascending=False).reset_index()
            
            self.upload_dataframe(category_summary, "Resumo_Categorias")
            
        except Exception as e:
            print(f"❌ Erro no resumo por categoria: {e}")
        
        # 3. Custos Fixos vs Variáveis (se disponível)
        if 'Custo_Tipo' in df.columns:
            try:
                fixed_var_summary = df[df['Tipo'] == 'Despesa'].groupby(['Mes_Str', 'Custo_Tipo']).agg({
                    'Valor_Absoluto': 'sum'
                }).reset_index()
                
                fixed_var_pivot = fixed_var_summary.pivot(
                    index='Mes_Str',
                    columns='Custo_Tipo',
                    values='Valor_Absoluto'
                ).fillna(0).reset_index()
                
                self.upload_dataframe(fixed_var_pivot, "Custos_Fixos_vs_Variaveis")
                
            except Exception as e:
                print(f"❌ Erro no resumo fixos vs variáveis: {e}")
        
        # 4. Top Gastos
        try:
            top_expenses = df[df['Tipo'] == 'Despesa'].nlargest(50, 'Valor_Absoluto')
            top_expenses_clean = top_expenses[['Data', 'Descrição', 'Categoria', 'Valor_Absoluto']].copy()
            top_expenses_clean['Data'] = top_expenses_clean['Data'].dt.strftime('%d/%m/%Y')
            
            self.upload_dataframe(top_expenses_clean, "Top_50_Gastos")
            
        except Exception as e:
            print(f"❌ Erro no top gastos: {e}")
        
        return True

def load_financial_data():
    """Carrega dados financeiros dos CSVs"""
    print("📁 Procurando arquivos CSV...")
    
    # Padrões de busca
    csv_patterns = [
        "*.csv",
        "data/*.csv", 
        "data/raw/*.csv",
        "extratos/*.csv"
    ]
    
    all_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
    
    if not all_files:
        print("❌ Nenhum arquivo CSV encontrado!")
        print("📋 Coloque seus CSVs do Nubank em uma das pastas:")
        print("   - Pasta atual")
        print("   - data/ ou data/raw/")
        print("   - extratos/")
        return pd.DataFrame()
    
    print(f"📄 Encontrados {len(all_files)} arquivo(s) CSV")
    
    # Carregar e combinar CSVs
    dfs = []
    for file in all_files:
        try:
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is not None:
                df['arquivo_origem'] = os.path.basename(file)
                dfs.append(df)
                print(f"  ✅ {os.path.basename(file)}")
            else:
                print(f"  ❌ {os.path.basename(file)} - erro de encoding")
                
        except Exception as e:
            print(f"  ❌ {os.path.basename(file)}: {str(e)}")
    
    if not dfs:
        return pd.DataFrame()
    
    # Combinar DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Processar dados
    print("🔧 Processando dados...")
    
    # Converter data
    combined_df['Data'] = pd.to_datetime(combined_df['Data'], errors='coerce')
    combined_df = combined_df.dropna(subset=['Data'])
    
    # Criar colunas auxiliares
    combined_df['Mes_Str'] = combined_df['Data'].dt.strftime('%Y-%m')
    combined_df['Ano'] = combined_df['Data'].dt.year
    
    # Processar valores
    combined_df['Valor'] = pd.to_numeric(combined_df['Valor'], errors='coerce')
    combined_df = combined_df.dropna(subset=['Valor'])
    
    # Classificar receitas e despesas
    combined_df['Tipo'] = combined_df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
    combined_df['Valor_Absoluto'] = combined_df['Valor'].abs()
    
    # Limpar dados
    if 'Descrição' in combined_df.columns:
        combined_df['Descrição'] = combined_df['Descrição'].fillna('Sem descrição')
    
    if 'Categoria' in combined_df.columns:
        combined_df['Categoria'] = combined_df['Categoria'].fillna('Outros')
    else:
        combined_df['Categoria'] = 'Outros'
    
    # Identificar custos fixos (básico)
    combined_df['Custo_Tipo'] = 'Variável'
    
    # Padrões de custos fixos
    fixed_patterns = ['FERREIRA IMOVEIS', 'ESCOLA', 'CLARO', 'TIM', 'MENSALIDADE']
    
    if 'Descrição' in combined_df.columns:
        for pattern in fixed_patterns:
            mask = combined_df['Descrição'].str.contains(pattern, case=False, na=False)
            combined_df.loc[mask, 'Custo_Tipo'] = 'Fixo'
    
    # Remover duplicatas
    if 'ID' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=['ID'], keep='first')
    
    print(f"✅ {len(combined_df)} transações processadas")
    print(f"📅 Período: {combined_df['Data'].min().date()} até {combined_df['Data'].max().date()}")
    
    return combined_df

def main():
    """Função principal"""
    print("🚀 Sincronização com Google Sheets")
    print("=" * 40)
    
    # Carregar dados
    df = load_financial_data()
    
    if df.empty:
        print("❌ Nenhum dado para sincronizar!")
        return
    
    # Conectar com Google Sheets
    print("\n☁️ Conectando com Google Sheets...")
    sync = GoogleSheetsSync()
    
    if not sync.client:
        print("❌ Falha na conexão com Google Sheets")
        return
    
    # Criar/abrir planilha
    spreadsheet_name = input("\n📊 Nome da planilha (Enter para 'Dashboard Financeiro'): ").strip()
    if not spreadsheet_name:
        spreadsheet_name = "Dashboard Financeiro"
    
    if not sync.create_or_open_spreadsheet(spreadsheet_name):
        print("❌ Falha ao criar/abrir planilha")
        return
    
    # Upload dos dados principais
    print("\n📤 Enviando dados principais...")
    success = sync.upload_dataframe(df, "Dados_Completos")
    
    if success:
        # Criar planilhas de resumo
        print("\n📊 Criando resumos...")
        sync.create_summary_sheets(df)
        
        print("\n✅ SINCRONIZAÇÃO CONCLUÍDA!")
        print(f"🔗 Acesse sua planilha em: https://docs.google.com/spreadsheets/")
        print(f"📊 Nome da planilha: {spreadsheet_name}")
        
        # Estatísticas finais
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   • {len(df):,} transações sincronizadas")
        print(f"   • Período: {df['Data'].min().strftime('%d/%m/%Y')} até {df['Data'].max().strftime('%d/%m/%Y')}")
        
        total_receitas = df[df['Tipo'] == 'Receita']['Valor_Absoluto'].sum()
        total_despesas = df[df['Tipo'] == 'Despesa']['Valor_Absoluto'].sum()
        saldo_total = total_receitas - total_despesas
        
        print(f"   • Total Receitas: R$ {total_receitas:,.2f}")
        print(f"   • Total Despesas: R$ {total_despesas:,.2f}")
        print(f"   • Saldo Total: R$ {saldo_total:,.2f}")
        
    else:
        print("❌ Falha na sincronização")

if __name__ == "__main__":
    main()

# ===== SCRIPT SIMPLIFICADO PARA EXECUÇÃO RÁPIDA =====

def quick_sync():
    """Sincronização rápida sem interação do usuário"""
    print("⚡ Sincronização Rápida")
    
    # Carregar dados
    df = load_financial_data()
    if df.empty:
        return
    
    # Conectar e sincronizar
    sync = GoogleSheetsSync()
    if sync.client:
        sync.create_or_open_spreadsheet("Dashboard Financeiro")
        sync.upload_dataframe(df, "Dados_Completos")
        sync.create_summary_sheets(df)
        print("✅ Sincronização rápida concluída!")

# Para execução rápida, descomente a linha abaixo:
# quick_sync()