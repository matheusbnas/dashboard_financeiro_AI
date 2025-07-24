"""
Google Sheets Sync - Módulo para sincronização com Google Sheets
Atualizado com emails corretos e melhorias v5.0
Execute: python google_sheets_sync.py
"""

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
import glob
import json
try:
    from config.settings import get_secret
except ImportError:
    def get_secret(key, default=None):
        import os
        return os.getenv(key, default)


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
                f"📧 Compartilhamento automático ativo para: {', '.join(self.share_emails)}")
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

                # Compartilhar automaticamente com emails configurados
                self.share_spreadsheet_with_emails()

            return True

        except Exception as e:
            print(f"❌ Erro ao abrir/criar planilha: {e}")
            return False

    def share_spreadsheet_with_emails(self):
        """Compartilha planilha com emails configurados"""
        if not self.spreadsheet:
            return

        try:
            for email in self.share_emails:
                try:
                    self.spreadsheet.share(
                        email, perm_type='user', role='writer')
                    print(f"✅ Planilha compartilhada com {email}")
                except Exception as e:
                    print(f"⚠️ Erro ao compartilhar com {email}: {e}")

        except Exception as e:
            print(f"❌ Erro no compartilhamento: {e}")

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

            # Formatação básica do cabeçalho
            header_range = f"A1:{chr(65 + len(headers) - 1)}1"
            worksheet.format(header_range, {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })

            print(
                f"✅ Dados enviados para aba '{worksheet_name}' ({len(df)} linhas)")
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

            monthly_pivot['Saldo'] = monthly_pivot.get(
                'Receita', 0) - monthly_pivot.get('Despesa', 0)
            monthly_pivot['Taxa_Poupanca_%'] = (
                monthly_pivot['Saldo'] / monthly_pivot.get('Receita', 1) * 100).round(2)

            monthly_pivot_reset = monthly_pivot.reset_index()
            self.upload_dataframe(monthly_pivot_reset, "📅 Resumo_Mensal")

        except Exception as e:
            print(f"❌ Erro no resumo mensal: {e}")

        # 2. Resumo por Categoria
        try:
            category_summary = df[df['Tipo'] == 'Despesa'].groupby('Categoria').agg({
                'Valor_Absoluto': ['sum', 'count', 'mean']
            }).round(2)

            category_summary.columns = ['Total', 'Quantidade', 'Media']
            category_summary = category_summary.sort_values(
                'Total', ascending=False).reset_index()

            self.upload_dataframe(category_summary, "🏷️ Resumo_Categorias")

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

                self.upload_dataframe(
                    fixed_var_pivot, "💡 Custos_Fixos_vs_Variaveis")

            except Exception as e:
                print(f"❌ Erro no resumo fixos vs variáveis: {e}")

        # 4. Top Gastos
        try:
            top_expenses = df[df['Tipo'] == 'Despesa'].nlargest(
                50, 'Valor_Absoluto')
            top_expenses_clean = top_expenses[[
                'Data', 'Descrição', 'Categoria', 'Valor_Absoluto']].copy()
            top_expenses_clean['Data'] = top_expenses_clean['Data'].dt.strftime(
                '%d/%m/%Y')

            self.upload_dataframe(top_expenses_clean, "🔝 Top_50_Gastos")

        except Exception as e:
            print(f"❌ Erro no top gastos: {e}")

        # 5. Estabelecimentos (se for dados Nubank)
        if 'Descrição' in df.columns:
            try:
                establishment_analysis = df.groupby('Descrição').agg({
                    'Valor_Absoluto': ['sum', 'mean', 'count'],
                    'Data': ['min', 'max']
                }).round(2)

                establishment_analysis.columns = [
                    'Total_Gasto', 'Gasto_Medio', 'Frequencia', 'Primeira_Compra', 'Ultima_Compra']
                establishment_analysis = establishment_analysis.sort_values(
                    'Frequencia', ascending=False).reset_index()

                # Formatar datas
                establishment_analysis['Primeira_Compra'] = pd.to_datetime(
                    establishment_analysis['Primeira_Compra']).dt.strftime('%d/%m/%Y')
                establishment_analysis['Ultima_Compra'] = pd.to_datetime(
                    establishment_analysis['Ultima_Compra']).dt.strftime('%d/%m/%Y')

                self.upload_dataframe(
                    establishment_analysis.head(100), "🏪 Estabelecimentos")

            except Exception as e:
                print(f"❌ Erro na análise de estabelecimentos: {e}")

        return True


def load_financial_data():
    """Carrega dados financeiros dos CSVs"""
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
        print("📋 Coloque seus extratos do Nubank em uma das pastas:")
        print("   - Pasta atual")
        print("   - data/ ou data/raw/")
        print("   - extratos/")
        return pd.DataFrame()

    # Priorizar arquivos Nubank se existirem
    files_to_process = nubank_files if nubank_files else all_files
    is_nubank_data = len(nubank_files) > 0

    print(f"📄 Encontrados {len(all_files)} arquivo(s) CSV")
    if is_nubank_data:
        print(f"💳 {len(nubank_files)} arquivo(s) Nubank detectado(s)")

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

    # Processar dados baseado no formato detectado
    print("🔧 Processando dados...")

    # Detectar formato Nubank
    is_nubank_format = all(col in combined_df.columns for col in [
                           'date', 'title', 'amount'])

    if is_nubank_format:
        # Formato Nubank: date, title, amount
        combined_df['Data'] = pd.to_datetime(
            combined_df['date'], errors='coerce')
        combined_df['Descrição'] = combined_df['title'].fillna('Sem descrição')
        combined_df['Valor'] = pd.to_numeric(
            combined_df['amount'], errors='coerce')

        # No Nubank: negativos = despesas, positivos = receitas/estornos
        combined_df['Tipo'] = combined_df['Valor'].apply(
            lambda x: 'Receita' if x > 0 else 'Despesa')

        print("💳 Formato Nubank processado")
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
    combined_df['Mes_Str'] = combined_df['Data'].dt.strftime('%Y-%m')
    combined_df['Ano'] = combined_df['Data'].dt.year
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

    # Identificar custos fixos (básico)
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
    print("🚀 Sincronização com Google Sheets v5.0")
    print("📧 Emails configurados: matheusbnas@gmail.com")
    print("🤖 Service Account: dashboard-financeiro@api-financeiro-460817.iam.gserviceaccount.com")
    print("=" * 70)

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
    spreadsheet_name = input(
        "\n📊 Nome da planilha (Enter para 'Dashboard Financeiro'): ").strip()
    if not spreadsheet_name:
        spreadsheet_name = "Dashboard Financeiro"

    if not sync.create_or_open_spreadsheet(spreadsheet_name):
        print("❌ Falha ao criar/abrir planilha")
        return

    # Upload dos dados principais
    print("\n📤 Enviando dados principais...")
    success = sync.upload_dataframe(df, "📊 Dados_Completos")

    if success:
        # Criar planilhas de resumo
        print("\n📊 Criando resumos...")
        sync.create_summary_sheets(df)

        print("\n✅ SINCRONIZAÇÃO CONCLUÍDA!")
        print(f"🔗 Acesse sua planilha em: {sync.spreadsheet.url}")
        print(f"📊 Nome da planilha: {spreadsheet_name}")

        # Estatísticas finais
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   • {len(df):,} transações sincronizadas")
        print(
            f"   • Período: {df['Data'].min().strftime('%d/%m/%Y')} até {df['Data'].max().strftime('%d/%m/%Y')}")

        total_receitas = df[df['Tipo'] == 'Receita']['Valor_Absoluto'].sum()
        total_despesas = df[df['Tipo'] == 'Despesa']['Valor_Absoluto'].sum()
        saldo_total = total_receitas - total_despesas

        print(f"   • Total Receitas: R$ {total_receitas:,.2f}")
        print(f"   • Total Despesas: R$ {total_despesas:,.2f}")
        print(f"   • Saldo Total: R$ {saldo_total:,.2f}")

        # Detectar formato
        is_nubank = 'amount' in df.columns or any(
            'Nubank' in str(f) for f in df.get('arquivo_origem', []))
        if is_nubank:
            print(f"   • Formato: Nubank (otimizado)")
            print(f"   • Estabelecimentos únicos: {df['Descrição'].nunique()}")
        else:
            print(f"   • Formato: Bancário tradicional")

        print(f"\n📧 Planilha compartilhada automaticamente com:")
        for email in sync.share_emails:
            print(f"   • {email}")

    else:
        print("❌ Falha na sincronização")


if __name__ == "__main__":
    main()

# ===== SCRIPT SIMPLIFICADO PARA EXECUÇÃO RÁPIDA =====


def quick_sync():
    """Sincronização rápida sem interação do usuário"""
    print("⚡ Sincronização Rápida v5.0")

    # Carregar dados
    df = load_financial_data()
    if df.empty:
        return False

    # Conectar e sincronizar
    sync = GoogleSheetsSync()
    if sync.client:
        spreadsheet_name = f"Dashboard Financeiro {datetime.now().strftime('%Y')}"
        sync.create_or_open_spreadsheet(spreadsheet_name)
        sync.upload_dataframe(df, "📊 Dados_Completos")
        sync.create_summary_sheets(df)
        print(f"✅ Sincronização rápida concluída!")
        print(f"🔗 Link: {sync.spreadsheet.url}")
        return True
    else:
        print("❌ Falha na conexão")
        return False

# Para execução rápida, descomente a linha abaixo:
# quick_sync()
