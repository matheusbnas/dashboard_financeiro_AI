import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config.settings import Config

class GoogleSheetsConnector:
    def __init__(self):
        self.config = Config()
        self.client = None
        self.connect()
    
    def connect(self):
        """Conecta com Google Sheets"""
        try:
            scopes = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                filename=self.config.GOOGLE_CREDENTIALS_PATH,
                scopes=scopes
            )
            
            self.client = gspread.authorize(creds)
            print("Conectado ao Google Sheets com sucesso!")
            
        except Exception as e:
            print(f"Erro ao conectar com Google Sheets: {e}")
            self.client = None
    
    def upload_data(self, df, sheet_name="Dashboard_Dados"):
        """Upload dados para Google Sheets"""
        if not self.client:
            print("Não conectado ao Google Sheets")
            return False
        
        try:
            # Abrir ou criar planilha
            try:
                spreadsheet = self.client.open(self.config.SPREADSHEET_NAME)
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(self.config.SPREADSHEET_NAME)
                if self.config.FOLDER_ID:
                    # Mover para pasta específica
                    drive_service = self.client.session
                    file_id = spreadsheet.id
                    drive_service.files().update(
                        fileId=file_id,
                        addParents=self.config.FOLDER_ID,
                        removeParents='root'
                    ).execute()
            
            # Criar ou atualizar worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, 
                    rows=len(df)+10, 
                    cols=len(df.columns)+5
                )
            
            # Upload dados
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            print(f"Dados enviados para: {sheet_name}")
            return True
            
        except Exception as e:
            print(f"Erro ao fazer upload: {e}")
            return False
    
    def create_summary_sheet(self, df):
        """Cria planilha de resumo"""
        summary_data = []
        
        # Resumo por mês
        monthly_summary = df.groupby(['Mes', 'Tipo']).agg({
            'Valor_Absoluto': 'sum'
        }).reset_index()
        
        monthly_pivot = monthly_summary.pivot(
            index='Mes', 
            columns='Tipo', 
            values='Valor_Absoluto'
        ).fillna(0)
        
        monthly_pivot['Saldo'] = monthly_pivot.get('Receita', 0) - monthly_pivot.get('Despesa', 0)
        
        # Resumo por categoria
        category_summary = df[df['Tipo'] == 'Despesa'].groupby('Categoria').agg({
            'Valor_Absoluto': 'sum'
        }).reset_index().sort_values('Valor_Absoluto', ascending=False)
        
        # Upload resumos
        self.upload_data(monthly_pivot.reset_index(), "Resumo_Mensal")
        self.upload_data(category_summary, "Resumo_Categorias")