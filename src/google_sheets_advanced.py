"""
Google Sheets Avançado - Organização Automática por Ano/Mês
Cria planilhas organizadas com índice master e compartilhamento automático
Execute: python src/google_sheets_advanced.py
"""

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime, timedelta
import glob
from typing import Dict, List, Optional
import time
import json
try:
    from config.settings import get_secret
except ImportError:
    def get_secret(key, default=None):
        import os
        return os.getenv(key, default)


class GoogleSheetsAdvanced:
    """Sistema avançado de Google Sheets com organização automática"""

    def __init__(self, credentials_path="credentials/google_credentials.json"):
        """
        Inicializa conexão avançada com Google Sheets

        Args:
            credentials_path: Caminho para arquivo de credenciais JSON
        """
        self.credentials_path = credentials_path
        self.client = None
        self.spreadsheets = {}
        self.master_spreadsheet = None

        # Emails configurados para compartilhamento automático
        self.share_emails = [
            'matheusbnas@gmail.com',
            'dashboard-financeiro@api-financeiro-460817.iam.gserviceaccount.com'
        ]

        self.connect()

    def connect(self):
        """Conecta com Google Sheets API"""
        try:
            # Verificar se arquivo de credenciais existe
            scopes = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file"
            ]
            creds_json = get_secret("GOOGLE_CREDENTIALS_JSON")
            if creds_json:
                creds_dict = json.loads(creds_json)
                from oauth2client.service_account import ServiceAccountCredentials
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict, scopes=scopes)
            elif os.path.exists(self.credentials_path):
                from oauth2client.service_account import ServiceAccountCredentials
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    filename=self.credentials_path,
                    scopes=scopes
                )
            else:
                print(
                    f"❌ Credenciais do Google não encontradas nem no secrets.toml nem no arquivo físico: {self.credentials_path}")
                return False
            import gspread
            self.client = gspread.authorize(creds)
            print("✅ Conectado ao Google Sheets com sucesso!")
            print(
                f"📧 Compartilhamento automático configurado para: {', '.join(self.share_emails)}")
            return True

        except Exception as e:
            print(f"❌ Erro ao conectar com Google Sheets: {e}")
            return False

    def create_master_index(self, year: int):
        """
        Cria planilha master com índice de todas as planilhas do ano

        Args:
            year: Ano para criar o índice
        """
        if not self.client:
            print("❌ Cliente não conectado")
            return None

        try:
            master_name = f"Dashboard Financeiro {year} - ÍNDICE MASTER"

            # Tentar abrir planilha master existente
            try:
                self.master_spreadsheet = self.client.open(master_name)
                print(f"📊 Planilha master '{master_name}' encontrada!")
            except gspread.SpreadsheetNotFound:
                # Criar nova planilha master
                self.master_spreadsheet = self.client.create(master_name)
                print(f"📊 Nova planilha master '{master_name}' criada!")

                # Compartilhar automaticamente
                self.share_spreadsheet(self.master_spreadsheet)

            # Criar ou atualizar aba de índice
            try:
                index_sheet = self.master_spreadsheet.worksheet("ÍNDICE")
                index_sheet.clear()
            except gspread.WorksheetNotFound:
                index_sheet = self.master_spreadsheet.add_worksheet(
                    title="ÍNDICE",
                    rows=50,
                    cols=10
                )

            # Cabeçalhos do índice
            headers = [
                "📅 Período",
                "📊 Planilha",
                "🔗 Link Direto",
                "📈 Total Despesas",
                "💰 Total Receitas",
                "💵 Saldo",
                "🔢 Transações",
                "📅 Última Atualização"
            ]

            index_sheet.update('A1:H1', [headers])

            # Formatação do cabeçalho
            index_sheet.format('A1:H1', {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })

            print("✅ Planilha master configurada!")
            return self.master_spreadsheet

        except Exception as e:
            print(f"❌ Erro ao criar planilha master: {e}")
            return None

    def share_spreadsheet(self, spreadsheet):
        """
        Compartilha planilha com emails configurados

        Args:
            spreadsheet: Objeto da planilha do gspread
        """
        try:
            for email in self.share_emails:
                try:
                    spreadsheet.share(email, perm_type='user', role='writer')
                    print(f"✅ Planilha compartilhada com {email}")
                except Exception as e:
                    print(f"⚠️ Erro ao compartilhar com {email}: {e}")

        except Exception as e:
            print(f"❌ Erro no compartilhamento: {e}")

    def create_monthly_spreadsheet(self, df: pd.DataFrame, year: int, month: int):
        """
        Cria planilha específica para um mês

        Args:
            df: DataFrame com dados do mês
            year: Ano
            month: Mês (1-12)
        """
        if not self.client or df.empty:
            return None

        try:
            # Nome da planilha mensal
            month_name = datetime(year, month, 1).strftime('%B')
            spreadsheet_name = f"Dashboard Financeiro {year} - {month:02d} {month_name}"

            print(f"📊 Criando planilha: {spreadsheet_name}")

            # Criar ou abrir planilha
            try:
                spreadsheet = self.client.open(spreadsheet_name)
                print(f"   📄 Planilha existente encontrada")
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(spreadsheet_name)
                print(f"   📄 Nova planilha criada")

                # Compartilhar automaticamente
                self.share_spreadsheet(spreadsheet)

            # Armazenar referência
            period_key = f"{year}-{month:02d}"
            self.spreadsheets[period_key] = spreadsheet

            # Criar abas organizadas
            self.create_organized_worksheets(spreadsheet, df, year, month)

            # Atualizar índice master
            self.update_master_index(df, year, month, spreadsheet)

            return spreadsheet

        except Exception as e:
            print(f"❌ Erro ao criar planilha mensal: {e}")
            return None

    def create_organized_worksheets(self, spreadsheet, df: pd.DataFrame, year: int, month: int):
        """
        Cria abas organizadas dentro da planilha mensal

        Args:
            spreadsheet: Planilha do gspread
            df: DataFrame com dados
            year: Ano
            month: Mês
        """
        month_name = datetime(year, month, 1).strftime('%B')

        # Abas a serem criadas
        worksheets_config = [
            {
                'name': f"📊 Resumo {month_name}",
                'function': self.create_summary_worksheet,
                'data': df
            },
            {
                'name': f"📋 Dados Completos",
                'function': self.create_complete_data_worksheet,
                'data': df
            },
            {
                'name': f"🏷️ Por Categoria",
                'function': self.create_category_worksheet,
                'data': df
            },
            {
                'name': f"🏪 Estabelecimentos",
                'function': self.create_establishments_worksheet,
                'data': df
            },
            {
                'name': f"💡 Fixos vs Variáveis",
                'function': self.create_fixed_var_worksheet,
                'data': df
            }
        ]

        # Remover aba padrão se existir
        try:
            default_sheet = spreadsheet.worksheet("Sheet1")
            spreadsheet.del_worksheet(default_sheet)
        except:
            pass

        # Criar cada aba
        for config in worksheets_config:
            try:
                print(f"   📄 Criando aba: {config['name']}")

                # Criar ou limpar aba
                try:
                    worksheet = spreadsheet.worksheet(config['name'])
                    worksheet.clear()
                except gspread.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(
                        title=config['name'],
                        rows=max(len(config['data']) + 50, 100),
                        cols=20
                    )

                # Chamar função específica para criar conteúdo
                config['function'](worksheet, config['data'], year, month)

                # Pequena pausa para evitar rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"   ❌ Erro ao criar aba {config['name']}: {e}")

    def create_summary_worksheet(self, worksheet, df: pd.DataFrame, year: int, month: int):
        """Cria aba de resumo do mês"""
        month_name = datetime(year, month, 1).strftime('%B')

        # Calcular estatísticas
        total_transactions = len(df)
        total_income = df[df['Valor'] > 0]['Valor'].sum(
        ) if not df[df['Valor'] > 0].empty else 0
        total_expenses = abs(df[df['Valor'] < 0]['Valor'].sum(
        )) if not df[df['Valor'] < 0].empty else 0
        balance = total_income - total_expenses

        # Cabeçalho
        header_data = [
            [f"📊 RESUMO FINANCEIRO - {month_name.upper()} {year}"],
            [f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"],
            [""],
            ["📈 ESTATÍSTICAS PRINCIPAIS"],
            [""],
            ["Métrica", "Valor", "Detalhes"],
            ["💰 Total Receitas",
                f"R$ {total_income:,.2f}", f"Entradas de dinheiro"],
            ["💸 Total Despesas",
                f"R$ {total_expenses:,.2f}", f"Saídas de dinheiro"],
            ["💵 Saldo Líquido", f"R$ {balance:,.2f}",
                "Positivo" if balance > 0 else "Negativo"],
            ["🔢 Transações", f"{total_transactions:,}",
                "Número total de operações"],
            [""],
        ]

        # Adicionar análise por categoria se disponível
        if 'Categoria' in df.columns:
            expenses_by_category = df[df['Valor'] < 0].groupby(
                'Categoria')['Valor'].sum().abs().sort_values(ascending=False)

            header_data.extend([
                ["🏷️ TOP 5 CATEGORIAS DE GASTO"],
                [""],
                ["Posição", "Categoria", "Valor", "% do Total"]
            ])

            for i, (category, value) in enumerate(expenses_by_category.head(5).items(), 1):
                percentage = (value / total_expenses *
                              100) if total_expenses > 0 else 0
                header_data.append(
                    [f"{i}º", category, f"R$ {value:,.2f}", f"{percentage:.1f}%"])

        # Adicionar análise de estabelecimentos se for Nubank
        if 'Descrição' in df.columns:
            frequent_establishments = df['Descrição'].value_counts().head(5)

            header_data.extend([
                [""],
                ["🏪 TOP 5 ESTABELECIMENTOS MAIS FREQUENTES"],
                [""],
                ["Posição", "Estabelecimento", "Frequência", "% das Transações"]
            ])

            for i, (establishment, freq) in enumerate(frequent_establishments.items(), 1):
                percentage = (freq / total_transactions *
                              100) if total_transactions > 0 else 0
                header_data.append(
                    [f"{i}º", establishment[:40], f"{freq}x", f"{percentage:.1f}%"])

        # Upload dos dados
        worksheet.update(f'A1:D{len(header_data)}', header_data)

        # Formatação
        worksheet.format('A1:D1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'fontSize': 14},
            'horizontalAlignment': 'CENTER'
        })

        worksheet.format('A4:D4', {
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
            'textFormat': {'bold': True},
            'horizontalAlignment': 'CENTER'
        })

    def create_complete_data_worksheet(self, worksheet, df: pd.DataFrame, year: int, month: int):
        """Cria aba com dados completos"""
        if df.empty:
            return

        # Preparar dados para upload
        display_df = df.copy()

        # Selecionar colunas relevantes
        columns_to_show = ['Data', 'Descrição', 'Categoria', 'Valor', 'Tipo']
        if 'Custo_Tipo' in display_df.columns:
            columns_to_show.append('Custo_Tipo')

        # Filtrar colunas existentes
        available_columns = [
            col for col in columns_to_show if col in display_df.columns]
        display_df = display_df[available_columns]

        # Formatar data
        if 'Data' in display_df.columns:
            display_df['Data'] = display_df['Data'].dt.strftime('%d/%m/%Y')

        # Formatar valores
        if 'Valor' in display_df.columns:
            display_df['Valor'] = display_df['Valor'].apply(
                lambda x: f"R$ {x:,.2f}")

        # Preparar dados para upload
        headers = list(display_df.columns)
        data = [headers] + display_df.values.tolist()

        # Upload
        worksheet.update(f'A1:{chr(65 + len(headers) - 1)}{len(data)}', data)

        # Formatação do cabeçalho
        worksheet.format(f'A1:{chr(65 + len(headers) - 1)}1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })

        # Formatação zebrada
        if len(data) > 2:
            for i in range(2, len(data), 2):
                worksheet.format(f'A{i + 1}:{chr(65 + len(headers) - 1)}{i + 1}', {
                    'backgroundColor': {'red': 0.97, 'green': 0.97, 'blue': 0.97}
                })

    def create_category_worksheet(self, worksheet, df: pd.DataFrame, year: int, month: int):
        """Cria aba de análise por categoria"""
        if df.empty or 'Categoria' not in df.columns:
            return

        # Análise por categoria
        category_analysis = df.groupby('Categoria').agg({
            'Valor': ['sum', 'count', 'mean'],
            'Data': ['min', 'max']
        }).round(2)

        category_analysis.columns = [
            'Total', 'Quantidade', 'Média', 'Primeira_Data', 'Última_Data']
        category_analysis = category_analysis.sort_values(
            'Total', key=abs, ascending=False)

        # Preparar dados
        headers = [
            "🏷️ Categoria",
            "💰 Total (R$)",
            "🔢 Quantidade",
            "📊 Média (R$)",
            "📅 Primeira",
            "📅 Última",
            "📈 % do Total"
        ]

        data = [headers]
        total_abs = abs(df['Valor']).sum()

        for category, row in category_analysis.iterrows():
            percentage = (abs(row['Total']) / total_abs *
                          100) if total_abs > 0 else 0
            data.append([
                category,
                f"R$ {row['Total']:,.2f}",
                int(row['Quantidade']),
                f"R$ {row['Média']:,.2f}",
                row['Primeira_Data'].strftime('%d/%m/%Y'),
                row['Última_Data'].strftime('%d/%m/%Y'),
                f"{percentage:.1f}%"
            ])

        # Upload
        worksheet.update(f'A1:G{len(data)}', data)

        # Formatação
        worksheet.format('A1:G1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })

    def create_establishments_worksheet(self, worksheet, df: pd.DataFrame, year: int, month: int):
        """Cria aba de análise de estabelecimentos"""
        if df.empty or 'Descrição' not in df.columns:
            return

        # Análise por estabelecimento
        establishment_analysis = df.groupby('Descrição').agg({
            'Valor': ['sum', 'count', 'mean'],
            'Data': ['min', 'max']
        }).round(2)

        establishment_analysis.columns = [
            'Total_Gasto', 'Frequência', 'Gasto_Médio', 'Primeira_Compra', 'Última_Compra']
        establishment_analysis = establishment_analysis.sort_values(
            'Frequência', ascending=False)

        # Preparar dados
        headers = [
            "🏪 Estabelecimento",
            "💰 Total Gasto (R$)",
            "🔄 Frequência",
            "📊 Gasto Médio (R$)",
            "📅 Primeira Compra",
            "📅 Última Compra",
            "📈 % das Transações"
        ]

        data = [headers]
        total_transactions = len(df)

        for establishment, row in establishment_analysis.iterrows():
            frequency_percentage = (
                row['Frequência'] / total_transactions * 100) if total_transactions > 0 else 0
            data.append([
                establishment,
                f"R$ {abs(row['Total_Gasto']):,.2f}",
                int(row['Frequência']),
                f"R$ {abs(row['Gasto_Médio']):,.2f}",
                row['Primeira_Compra'].strftime('%d/%m/%Y'),
                row['Última_Compra'].strftime('%d/%m/%Y'),
                f"{frequency_percentage:.1f}%"
            ])

        # Upload
        worksheet.update(f'A1:G{len(data)}', data)

        # Formatação
        worksheet.format('A1:G1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })

    def create_fixed_var_worksheet(self, worksheet, df: pd.DataFrame, year: int, month: int):
        """Cria aba de análise custos fixos vs variáveis"""
        if df.empty or 'Custo_Tipo' not in df.columns:
            return

        # Análise custos fixos vs variáveis
        fixed_var_analysis = df[df['Valor'] < 0].groupby('Custo_Tipo').agg({
            'Valor': ['sum', 'count', 'mean']
        }).round(2)

        fixed_var_analysis.columns = ['Total', 'Quantidade', 'Média']

        # Preparar dados
        headers = [
            "💡 Tipo de Custo",
            "💰 Total (R$)",
            "🔢 Quantidade",
            "📊 Média (R$)",
            "📈 % do Total"
        ]

        data = [headers]
        total_expenses = abs(df[df['Valor'] < 0]['Valor'].sum())

        for cost_type, row in fixed_var_analysis.iterrows():
            percentage = (abs(row['Total']) / total_expenses *
                          100) if total_expenses > 0 else 0
            data.append([
                cost_type,
                f"R$ {abs(row['Total']):,.2f}",
                int(row['Quantidade']),
                f"R$ {abs(row['Média']):,.2f}",
                f"{percentage:.1f}%"
            ])

        # Upload
        worksheet.update(f'A1:E{len(data)}', data)

        # Formatação
        worksheet.format('A1:E1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })

    def update_master_index(self, df: pd.DataFrame, year: int, month: int, spreadsheet):
        """Atualiza índice master com informações da planilha mensal"""
        if not self.master_spreadsheet:
            return

        try:
            index_sheet = self.master_spreadsheet.worksheet("ÍNDICE")

            # Calcular estatísticas
            total_income = df[df['Valor'] > 0]['Valor'].sum(
            ) if not df[df['Valor'] > 0].empty else 0
            total_expenses = abs(df[df['Valor'] < 0]['Valor'].sum(
            )) if not df[df['Valor'] < 0].empty else 0
            balance = total_income - total_expenses
            total_transactions = len(df)

            # Dados da linha
            month_name = datetime(year, month, 1).strftime('%B')
            period = f"{month_name} {year}"
            spreadsheet_name = spreadsheet.title
            spreadsheet_url = spreadsheet.url
            last_updated = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

            row_data = [
                period,
                spreadsheet_name,
                spreadsheet_url,
                f"R$ {total_expenses:,.2f}",
                f"R$ {total_income:,.2f}",
                f"R$ {balance:,.2f}",
                total_transactions,
                last_updated
            ]

            # Encontrar próxima linha vazia
            all_values = index_sheet.get_all_values()
            next_row = len(all_values) + 1

            # Adicionar dados
            index_sheet.update(f'A{next_row}:H{next_row}', [row_data])

            # Formatação condicional para saldo
            if balance > 0:
                color = {'red': 0.8, 'green': 1, 'blue': 0.8}  # Verde claro
            elif balance < 0:
                color = {'red': 1, 'green': 0.8, 'blue': 0.8}  # Vermelho claro
            else:
                color = {'red': 1, 'green': 1, 'blue': 0.8}  # Amarelo claro

            index_sheet.format(f'F{next_row}', {'backgroundColor': color})

            print(f"✅ Índice master atualizado para {period}")

        except Exception as e:
            print(f"❌ Erro ao atualizar índice master: {e}")

    def process_all_data(self, df: pd.DataFrame):
        """
        Processa todos os dados e organiza por ano/mês

        Args:
            df: DataFrame com todos os dados financeiros
        """
        if df.empty or 'Data' not in df.columns:
            print("❌ DataFrame vazio ou sem coluna Data")
            return

        print("🚀 Iniciando processamento avançado de dados...")

        # Converter data se necessário
        if not pd.api.types.is_datetime64_any_dtype(df['Data']):
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

        # Remover dados inválidos
        df = df.dropna(subset=['Data'])

        if df.empty:
            print("❌ Nenhum dado válido após limpeza")
            return

        # Agrupar por ano e mês
        df['Ano'] = df['Data'].dt.year
        df['Mês'] = df['Data'].dt.month

        # Obter períodos únicos
        periods = df.groupby(['Ano', 'Mês']).size().reset_index(name='count')
        periods = periods.sort_values(['Ano', 'Mês'])

        print(f"📅 Encontrados {len(periods)} períodos para processar:")
        for _, period in periods.iterrows():
            year, month, count = period['Ano'], period['Mês'], period['count']
            month_name = datetime(year, month, 1).strftime('%B')
            print(f"   • {month_name} {year}: {count} transações")

        # Criar planilha master para cada ano
        years = periods['Ano'].unique()
        for year in years:
            print(f"\n📊 Processando ano {year}...")
            self.create_master_index(year)

            # Processar cada mês do ano
            year_periods = periods[periods['Ano'] == year]
            for _, period in year_periods.iterrows():
                year, month, count = period['Ano'], period['Mês'], period['count']

                # Filtrar dados do mês
                month_data = df[(df['Ano'] == year) &
                                (df['Mês'] == month)].copy()

                if not month_data.empty:
                    print(
                        f"   📅 Processando {datetime(year, month, 1).strftime('%B')} {year}...")
                    self.create_monthly_spreadsheet(month_data, year, month)

                    # Pausa para evitar rate limiting
                    time.sleep(1)

        print(f"\n✅ Processamento concluído!")
        print(f"📊 {len(self.spreadsheets)} planilhas mensais criadas")
        print(f"📋 {len(years)} planilhas master criadas")
        print(
            f"📧 Todas as planilhas compartilhadas com: {', '.join(self.share_emails)}")

        # Mostrar links das planilhas master
        if years:
            print(f"\n🔗 LINKS DAS PLANILHAS MASTER:")
            for year in years:
                try:
                    master_name = f"Dashboard Financeiro {year} - ÍNDICE MASTER"
                    master_sheet = self.client.open(master_name)
                    print(f"   📊 {year}: {master_sheet.url}")
                except:
                    pass


def load_financial_data():
    """Carrega dados financeiros dos CSVs com detecção automática de formato"""
    print("📁 Procurando arquivos CSV...")

    # Padrões de busca priorizando Nubank
    csv_patterns = [
        "Nubank_*.csv",  # Prioritário
        "*.csv",
        "data/*.csv",
        "data/raw/*.csv",
        "extratos/*.csv"
    ]

    all_files = []
    nubank_files = []

    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
        if "Nubank_" in pattern:
            nubank_files.extend(files)

    # Remover duplicatas
    all_files = list(dict.fromkeys(all_files))

    if not all_files:
        print("❌ Nenhum arquivo CSV encontrado!")
        print("📋 Coloque seus extratos em uma das pastas:")
        print("   - Pasta atual")
        print("   - data/ ou data/raw/")
        print("   - extratos/")
        return pd.DataFrame()

    # Priorizar arquivos Nubank se existirem
    files_to_process = nubank_files if nubank_files else all_files
    is_nubank_data = len(nubank_files) > 0

    print(f"📄 Encontrados {len(all_files)} arquivo(s) CSV")
    if is_nubank_data:
        print(
            f"💳 {len(nubank_files)} arquivo(s) Nubank detectado(s) - processamento otimizado")

    # Carregar e combinar CSVs
    dfs = []
    for file in files_to_process:
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

    # Processar dados baseado no formato
    print("🔧 Processando dados...")

    if is_nubank_data:
        # Formato Nubank: date, title, amount
        if all(col in combined_df.columns for col in ['date', 'title', 'amount']):
            combined_df['Data'] = pd.to_datetime(
                combined_df['date'], errors='coerce')
            combined_df['Descrição'] = combined_df['title'].fillna(
                'Sem descrição')
            combined_df['Valor'] = pd.to_numeric(
                combined_df['amount'], errors='coerce')

            # No Nubank: negativos = despesas, positivos = receitas/estornos
            combined_df['Tipo'] = combined_df['Valor'].apply(
                lambda x: 'Receita' if x > 0 else 'Despesa')

            print("💳 Formato Nubank processado")
        else:
            print("⚠️ Esperado formato Nubank mas colunas não encontradas")
    else:
        # Formato tradicional
        combined_df['Data'] = pd.to_datetime(
            combined_df['Data'], errors='coerce')
        combined_df['Valor'] = pd.to_numeric(
            combined_df['Valor'], errors='coerce')
        combined_df['Tipo'] = combined_df['Valor'].apply(
            lambda x: 'Receita' if x > 0 else 'Despesa')

        print("🏦 Formato bancário tradicional processado")

    # Limpar dados inválidos
    combined_df = combined_df.dropna(subset=['Data', 'Valor'])

    # Criar colunas auxiliares
    combined_df['Valor_Absoluto'] = combined_df['Valor'].abs()

    # Limpar e preencher campos
    if 'Descrição' not in combined_df.columns:
        combined_df['Descrição'] = 'Sem descrição'
    else:
        combined_df['Descrição'] = combined_df['Descrição'].fillna(
            'Sem descrição')

    if 'Categoria' not in combined_df.columns:
        combined_df['Categoria'] = 'Outros'
    else:
        combined_df['Categoria'] = combined_df['Categoria'].fillna('Outros')

    # Identificar custos fixos básicos
    combined_df['Custo_Tipo'] = 'Variável'

    # Padrões de custos fixos
    fixed_patterns = [
        'FERREIRA IMOVEIS', 'ESCOLA', 'CLARO', 'TIM', 'MENSALIDADE',
        'ALUGUEL', 'CONDOMINIO', 'NETFLIX', 'SPOTIFY', 'INTERNET'
    ]

    if 'Descrição' in combined_df.columns:
        for pattern in fixed_patterns:
            mask = combined_df['Descrição'].str.contains(
                pattern, case=False, na=False)
            combined_df.loc[mask, 'Custo_Tipo'] = 'Fixo'

    # Remover duplicatas
    if 'ID' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=['ID'], keep='first')

    print(f"✅ {len(combined_df)} transações processadas")
    print(
        f"📅 Período: {combined_df['Data'].min().date()} até {combined_df['Data'].max().date()}")

    return combined_df


def main():
    """Função principal"""
    print("🚀 Google Sheets Avançado - Organização Automática por Ano/Mês")
    print("=" * 70)
    print("📧 Emails configurados para compartilhamento automático:")
    print("   • matheusbnas@gmail.com")
    print("   • dashboard-financeiro@api-financeiro-460817.iam.gserviceaccount.com")
    print("=" * 70)

    # Carregar dados
    df = load_financial_data()

    if df.empty:
        print("❌ Nenhum dado para processar!")
        return

    # Conectar com Google Sheets
    print("\n☁️ Conectando com Google Sheets...")
    sheets_advanced = GoogleSheetsAdvanced()

    if not sheets_advanced.client:
        print("❌ Falha na conexão com Google Sheets")
        return

    # Processar todos os dados
    print("\n📊 Iniciando processamento avançado...")
    sheets_advanced.process_all_data(df)

    print(f"\n🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"📊 Planilhas organizadas por ano e mês criadas automaticamente")
    print(f"📧 Todas as planilhas foram compartilhadas com os emails configurados")
    print(f"🔗 Acesse: https://docs.google.com/spreadsheets/")

    # Estatísticas finais
    total_income = df[df['Valor'] > 0]['Valor'].sum(
    ) if not df[df['Valor'] > 0].empty else 0
    total_expenses = abs(df[df['Valor'] < 0]['Valor'].sum()
                         ) if not df[df['Valor'] < 0].empty else 0
    balance = total_income - total_expenses

    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    print(f"   • Total de transações: {len(df):,}")
    print(
        f"   • Período completo: {df['Data'].min().date()} até {df['Data'].max().date()}")
    print(f"   • Total receitas: R$ {total_income:,.2f}")
    print(f"   • Total despesas: R$ {total_expenses:,.2f}")
    print(f"   • Saldo total: R$ {balance:,.2f}")

    # Detectar formato
    is_nubank = 'amount' in df.columns or any(
        'Nubank' in str(f) for f in df.get('arquivo_origem', []))
    if is_nubank:
        print(f"   • Formato: Nubank (otimizado)")
    else:
        print(f"   • Formato: Bancário tradicional")


if __name__ == "__main__":
    main()

# ===== FUNÇÃO PARA INTEGRAÇÃO COM DASHBOARD =====


def quick_advanced_sync():
    """Sincronização rápida avançada para uso em outros módulos"""
    print("⚡ Sincronização Avançada Rápida")

    # Carregar dados
    df = load_financial_data()
    if df.empty:
        print("❌ Nenhum dado encontrado")
        return False

    # Conectar e processar
    sheets_advanced = GoogleSheetsAdvanced()
    if sheets_advanced.client:
        sheets_advanced.process_all_data(df)
        print("✅ Sincronização avançada concluída!")
        return True
    else:
        print("❌ Falha na conexão")
        return False


# Para uso em outros módulos:
"""
from src.google_sheets_advanced import quick_advanced_sync

# Executar sincronização avançada
success = quick_advanced_sync()
if success:
    print("Planilhas organizadas criadas com sucesso!")
"""
