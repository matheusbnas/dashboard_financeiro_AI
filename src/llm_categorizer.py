"""
Categorizador Automático usando LLM
Categoriza automaticamente transações financeiras usando IA
Execute: python llm_categorizer.py
"""

import pandas as pd
import os
import glob
from datetime import datetime
import json
from typing import List, Dict
import time

# Importações condicionais para LLMs
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class FinancialCategorizer:
    """Categorizador automático de transações financeiras"""
    
    def __init__(self, provider="groq"):
        """
        Inicializa o categorizador
        
        Args:
            provider: 'openai', 'groq' ou 'local'
        """
        self.provider = provider
        self.llm = None
        self.chain = None
        
        # Categorias padrão
        self.categories = [
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
            'Outros'
        ]
        
        # Inicializar LLM
        self._setup_llm()
        
        # Cache para evitar recategorizar
        self.cache = {}
        self.cache_file = "categorization_cache.json"
        self._load_cache()
    
    def _setup_llm(self):
        """Configura o modelo de linguagem"""
        print(f"🤖 Configurando LLM ({self.provider})...")
        
        # Template do prompt
        template = """
Você é um analista de dados especializado em categorização de transações financeiras.
Sua tarefa é categorizar cada transação bancária de uma pessoa física.

Categorias disponíveis:
{categories}

Regras:
- Analise a descrição da transação
- Escolha APENAS UMA categoria da lista acima
- Seja consistente nas categorizações
- Se não tiver certeza, use "Outros"
- Responda APENAS com o nome da categoria, sem explicações

Transação para categorizar:
Descrição: {description}
Valor: {value}

Categoria:"""

        self.prompt = PromptTemplate.from_template(template)
        
        try:
            if self.provider == "openai" and OPENAI_AVAILABLE:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    print("⚠️ OPENAI_API_KEY não encontrada no .env")
                    return False
                
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    api_key=api_key
                )
                
            elif self.provider == "groq" and GROQ_AVAILABLE:
                api_key = os.getenv('GROQ_API_KEY')
                if not api_key:
                    print("⚠️ GROQ_API_KEY não encontrada no .env")
                    print("📋 Obtenha sua chave em: https://console.groq.com/")
                    return False
                
                self.llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    api_key=api_key
                )
            
            else:
                print(f"❌ Provider '{self.provider}' não disponível ou dependências não instaladas")
                return False
            
            # Criar chain
            self.chain = self.prompt | self.llm | StrOutputParser()
            print("✅ LLM configurado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar LLM: {e}")
            return False
    
    def _load_cache(self):
        """Carrega cache de categorizações anteriores"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"📋 Cache carregado: {len(self.cache)} categorizações")
            except Exception as e:
                print(f"⚠️ Erro ao carregar cache: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def _save_cache(self):
        """Salva cache de categorizações"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
    
    def _create_cache_key(self, description: str, value: float) -> str:
        """Cria chave única para o cache"""
        # Normalizar descrição
        desc_normalized = description.lower().strip()
        # Criar chave baseada na descrição e valor aproximado
        return f"{desc_normalized}_{abs(value):.0f}"
    
    def categorize_single(self, description: str, value: float) -> str:
        """
        Categoriza uma única transação
        
        Args:
            description: Descrição da transação
            value: Valor da transação
            
        Returns:
            Categoria identificada
        """
        # Verificar cache primeiro
        cache_key = self._create_cache_key(description, value)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Se não tiver LLM configurado, usar regras básicas
        if not self.chain:
            category = self._rule_based_categorization(description, value)
        else:
            try:
                # Usar LLM
                result = self.chain.invoke({
                    "categories": "\n".join([f"- {cat}" for cat in self.categories]),
                    "description": description,
                    "value": f"R$ {value:.2f}"
                })
                
                # Limpar resultado
                category = result.strip()
                
                # Validar se a categoria está na lista
                if category not in self.categories:
                    print(f"⚠️ Categoria inválida '{category}' para '{description[:50]}', usando regras")
                    category = self._rule_based_categorization(description, value)
                
            except Exception as e:
                print(f"❌ Erro na categorização LLM: {e}")
                category = self._rule_based_categorization(description, value)
        
        # Salvar no cache
        self.cache[cache_key] = category
        return category
    
    def _rule_based_categorization(self, description: str, value: float) -> str:
        """Categorização baseada em regras quando LLM não está disponível"""
        desc_lower = description.lower()
        
        # Regras baseadas em palavras-chave
        rules = {
            'Receitas': ['salario', 'pix - recebido', 'transferencia recebida', 'receita'],
            'Moradia': ['ferreira imoveis', 'aluguel', 'condominio', 'iptu', 'luz', 'energia'],
            'Alimentação': ['restaurante', 'lanchonete', 'padaria', 'açougue', 'parrilla', 'burguer', 'pizza'],
            'Mercado': ['supermercado', 'mercado', 'atacadao', 'bistek', 'zaffari'],
            'Transporte': ['posto', 'combustivel', 'uber', 'taxi', 'onibus', 'metro', 'estacionamento'],
            'Saúde': ['farmacia', 'drogaria', 'panvel', 'unimed', 'medico', 'hospital'],
            'Educação': ['escola', 'universidade', 'curso', 'mensalidade', 'livro', 'material'],
            'Telefone': ['claro', 'tim', 'vivo', 'oi', 'telefone', 'celular'],
            'Compras': ['loja', 'magazine', 'shopping', 'renner', 'mercadolivre'],
            'Entretenimento': ['cinema', 'teatro', 'show', 'netflix', 'spotify'],
            'Transferências para terceiros': ['pix - enviado', 'ted', 'transferencia']
        }
        
        # Verificar cada regra
        for category, keywords in rules.items():
            if any(keyword in desc_lower for keyword in keywords):
                return category
        
        # Categoria padrão
        return 'Outros'
    
    def categorize_dataframe(self, df: pd.DataFrame, batch_size: int = 50) -> pd.DataFrame:
        """
        Categoriza todas as transações de um DataFrame
        
        Args:
            df: DataFrame com as transações
            batch_size: Tamanho do lote para processamento
            
        Returns:
            DataFrame com categorias atualizadas
        """
        if df.empty:
            return df
        
        print(f"🏷️ Categorizando {len(df)} transações...")
        
        # Verificar se já existe coluna de categoria
        if 'Categoria' not in df.columns:
            df['Categoria'] = None
        
        # Contar transações que precisam de categorização
        uncategorized = df['Categoria'].isna() | (df['Categoria'] == '') | (df['Categoria'] == 'Outros')
        total_to_categorize = uncategorized.sum()
        
        if total_to_categorize == 0:
            print("✅ Todas as transações já estão categorizadas!")
            return df
        
        print(f"📝 {total_to_categorize} transações precisam de categorização")
        
        # Processar em lotes
        categorized_count = 0
        start_time = time.time()
        
        for idx, row in df[uncategorized].iterrows():
            try:
                description = str(row.get('Descrição', ''))
                value = float(row.get('Valor', 0))
                
                category = self.categorize_single(description, value)
                df.at[idx, 'Categoria'] = category
                
                categorized_count += 1
                
                # Mostrar progresso
                if categorized_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = categorized_count / elapsed if elapsed > 0 else 0
                    remaining = (total_to_categorize - categorized_count) / rate if rate > 0 else 0
                    
                    print(f"   📊 {categorized_count}/{total_to_categorize} "
                          f"({categorized_count/total_to_categorize*100:.1f}%) "
                          f"- {rate:.1f}/s - ETA: {remaining:.0f}s")
                
                # Delay pequeno para evitar rate limiting
                if self.chain and categorized_count % batch_size == 0:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Erro ao categorizar linha {idx}: {e}")
                df.at[idx, 'Categoria'] = 'Outros'
        
        # Salvar cache
        self._save_cache()
        
        print(f"✅ Categorização concluída! {categorized_count} transações categorizadas")
        
        return df
    
    def get_categorization_stats(self, df: pd.DataFrame) -> Dict:
        """Retorna estatísticas da categorização"""
        if 'Categoria' not in df.columns:
            return {}
        
        stats = df['Categoria'].value_counts().to_dict()
        
        # Estatísticas por tipo
        receitas = df[df['Valor'] > 0]['Categoria'].value_counts().to_dict()
        despesas = df[df['Valor'] < 0]['Categoria'].value_counts().to_dict()
        
        return {
            'geral': stats,
            'receitas': receitas,
            'despesas': despesas,
            'total_categorias': len(stats),
            'total_transacoes': len(df)
        }

def load_financial_data():
    """Carrega dados financeiros dos CSVs"""
    print("📁 Carregando dados financeiros...")
    
    csv_patterns = ["*.csv", "data/*.csv", "data/raw/*.csv", "extratos/*.csv"]
    all_files = []
    
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
    
    if not all_files:
        print("❌ Nenhum arquivo CSV encontrado!")
        return pd.DataFrame()
    
    dfs = []
    for file in all_files:
        try:
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is not None:
                dfs.append(df)
                print(f"  ✅ {os.path.basename(file)}")
        except Exception as e:
            print(f"  ❌ {os.path.basename(file)}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Processamento básico
    combined_df['Data'] = pd.to_datetime(combined_df['Data'], errors='coerce')
    combined_df['Valor'] = pd.to_numeric(combined_df['Valor'], errors='coerce')
    combined_df = combined_df.dropna(subset=['Data', 'Valor'])
    
    if 'Descrição' in combined_df.columns:
        combined_df['Descrição'] = combined_df['Descrição'].fillna('Sem descrição')
    
    print(f"✅ {len(combined_df)} transações carregadas")
    return combined_df

def main():
    """Função principal"""
    print("🤖 Categorizador Automático de Transações Financeiras")
    print("=" * 60)
    
    # Carregar dados
    df = load_financial_data()
    if df.empty:
        print("❌ Nenhum dado encontrado!")
        return
    
    # Escolher provider
    print("\n🔧 Configuração do LLM:")
    print("1. Groq (Llama - Gratuito)")
    print("2. OpenAI (GPT - Pago)")
    print("3. Apenas regras (Sem IA)")
    
    choice = input("Escolha (1-3): ").strip()
    
    if choice == "1":
        provider = "groq"
    elif choice == "2":
        provider = "openai"
    else:
        provider = "local"
    
    # Inicializar categorizador
    categorizer = FinancialCategorizer(provider=provider)
    
    # Categorizar
    print(f"\n🚀 Iniciando categorização...")
    df_categorized = categorizer.categorize_dataframe(df)
    
    # Estatísticas
    stats = categorizer.get_categorization_stats(df_categorized)
    
    print(f"\n📊 ESTATÍSTICAS DA CATEGORIZAÇÃO:")
    print(f"   • Total de transações: {stats.get('total_transacoes', 0):,}")
    print(f"   • Categorias identificadas: {stats.get('total_categorias', 0)}")
    
    print(f"\n🏷️ DISTRIBUIÇÃO POR CATEGORIA:")
    for cat, count in sorted(stats.get('geral', {}).items(), key=lambda x: x[1], reverse=True):
        percentage = count / stats.get('total_transacoes', 1) * 100
        print(f"   • {cat}: {count:,} ({percentage:.1f}%)")
    
    # Salvar resultado
    output_file = f"dados_categorizados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_categorized.to_csv(output_file, index=False)
    
    print(f"\n✅ CATEGORIZAÇÃO CONCLUÍDA!")
    print(f"💾 Dados salvos em: {output_file}")
    print(f"🔄 Cache salvo para próximas execuções")
    
    # Opção de executar dashboard
    run_dashboard = input(f"\n🚀 Executar dashboard com dados categorizados? (s/N): ").strip().lower()
    if run_dashboard == 's':
        try:
            import subprocess
            subprocess.run(["streamlit", "run", "dashboard.py"])
        except Exception as e:
            print(f"❌ Erro ao executar dashboard: {e}")
            print("Execute manualmente: streamlit run dashboard.py")

if __name__ == "__main__":
    main()

# ===== UTILITÁRIOS ADICIONAIS =====

def batch_categorize_files(folder_path: str, provider: str = "groq"):
    """Categoriza todos os CSVs de uma pasta"""
    print(f"📁 Categorizando arquivos na pasta: {folder_path}")
    
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        print("❌ Nenhum CSV encontrado na pasta")
        return
    
    categorizer = FinancialCategorizer(provider=provider)
    
    for file in csv_files:
        print(f"\n📄 Processando: {os.path.basename(file)}")
        
        try:
            df = pd.read_csv(file)
            df_categorized = categorizer.categorize_dataframe(df)
            
            # Salvar com sufixo
            output_file = file.replace('.csv', '_categorizado.csv')
            df_categorized.to_csv(output_file, index=False)
            
            print(f"✅ Salvo: {os.path.basename(output_file)}")
            
        except Exception as e:
            print(f"❌ Erro ao processar {file}: {e}")

def update_categories(new_categories: List[str], cache_file: str = "categorization_cache.json"):
    """Atualiza lista de categorias e limpa cache se necessário"""
    print(f"🔄 Atualizando categorias...")
    
    # Salvar backup do cache
    if os.path.exists(cache_file):
        backup_file = f"{cache_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(cache_file, backup_file)
        print(f"💾 Backup do cache salvo: {backup_file}")
    
    print(f"✅ Categorias atualizadas. Cache limpo.")
    print(f"📋 Novas categorias: {', '.join(new_categories)}")

# Exemplo de uso programático:
"""
# Para usar em outros scripts:
from llm_categorizer import FinancialCategorizer

categorizer = FinancialCategorizer(provider="groq")
df = pd.read_csv("meus_dados.csv")
df_categorized = categorizer.categorize_dataframe(df)
df_categorized.to_csv("dados_categorizados.csv", index=False)
"""