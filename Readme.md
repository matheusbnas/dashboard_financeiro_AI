# 💰 Dashboard Financeiro Completo

Um sistema completo de análise financeira pessoal com dashboard interativo, categorização automática por IA, sincronização com Google Sheets e relatórios avançados.

## 🚀 Características Principais

### ✨ Dashboard Interativo
- **Visualizações em tempo real** com Plotly
- **Métricas financeiras** detalhadas
- **Filtros avançados** por período, categoria e tipo
- **Análise de custos fixos vs variáveis**
- **Interface responsiva** para desktop e mobile

### 🤖 Categorização Inteligente
- **IA com LLM** (Groq/OpenAI) para categorização automática
- **Regras inteligentes** como fallback
- **Cache** para evitar recategorizações
- **Aprendizado** com base em padrões históricos

### ☁️ Sincronização Google Sheets
- **Upload automático** de dados e resumos
- **Planilhas organizadas** por tipo de análise
- **Acesso em qualquer lugar** via Google Sheets
- **Backup seguro** na nuvem

### 📈 Análise Avançada
- **Score de saúde financeira** (0-100)
- **Detecção de anomalias** e alertas
- **Previsões** baseadas em tendências
- **Relatórios em PDF/JSON** exportáveis

### 🔒 Segurança e Privacidade
- **Processamento local** dos dados
- **Arquivos sensíveis** protegidos por .gitignore
- **Credenciais criptografadas** Google API
- **Sem compartilhamento** de dados pessoais

## 📋 Pré-requisitos

- **Python 3.8+**
- **Conta Google** (para Google Sheets - opcional)
- **Extratos do Nubank** em formato CSV

## 🛠️ Instalação Rápida

### 1. Download e Configuração

```bash
# Clonar ou baixar o projeto
git clone <repositorio> ou baixar ZIP

# Navegar para a pasta
cd dashboard_financeiro_AI

# Executar configuração automática
python main.py
```

### 2. Primeira Execução

1. Execute `python main.py`
2. Escolha "⚙️ Configuração Inicial"
3. Siga as instruções na tela
4. Coloque seus CSVs do Nubank na pasta indicada

### 3. Usar o Sistema

```bash
# Launcher completo (recomendado)
python main.py

# Ou executar módulos diretamente
streamlit run dashboard.py          # Dashboard
python llm_categorizer.py          # Categorização  
python google_sheets_sync.py       # Sincronização
python advanced_analytics.py       # Análise avançada
```

## 📁 Estrutura do Projeto

```
dashboard_financeiro_AI/
├── main.py                      # 🚀 Launcher principal
├── dashboard.py                 # 📊 Dashboard interativo
├── llm_categorizer.py          # 🤖 Categorização IA
├── google_sheets_sync.py       # ☁️ Sincronização Google
├── advanced_analytics.py       # 📈 Análise avançada
├── config.json                 # ⚙️ Configurações
├── .env                        # 🔑 Variáveis ambiente
├── .gitignore                  # 🔒 Arquivos protegidos
├── requirements.txt            # 📦 Dependências
├── data/
│   ├── raw/                   # 📄 CSVs do Nubank (protegido)
│   ├── processed/             # 🔄 Dados processados
│   └── exports/               # 📤 Exportações
├── credentials/               # 🔐 Credenciais Google (protegido)
└── README.md                  # 📖 Este arquivo
```

## 📊 Formato dos Dados

### CSV do Nubank (obrigatório)
```csv
ID,Data,Valor,Descrição
20240101001,2024-01-01,-50.00,SUPERMERCADO XYZ
20240101002,2024-01-01,3000.00,SALARIO EMPRESA
```

### Campos obrigatórios:
- **ID**: Identificador único da transação
- **Data**: Data no formato YYYY-MM-DD
- **Valor**: Numérico (negativo = despesa, positivo = receita)
- **Descrição**: Descrição da transação

### Campos opcionais:
- **Categoria**: Se já categorizado (senão será feito automaticamente)

## 🔧 Configuração Detalhada

### Google Sheets API

1. **Acesse [Google Cloud Console](https://console.cloud.google.com/)**
2. **Crie um projeto** ou selecione existente
3. **Habilite APIs**:
   - Google Sheets API
   - Google Drive API
4. **Crie Service Account**:
   - APIs & Services → Credentials
   - Create Credentials → Service Account
   - Baixe o arquivo JSON
5. **Configure credenciais**:
   - Renomeie para `google_credentials.json`
   - Coloque em `credentials/`

### LLM para Categorização

#### Groq (Gratuito - Recomendado)
1. Acesse [Groq Console](https://console.groq.com/)
2. Crie conta e obtenha API key
3. Configure no `.env`:
```env
GROQ_API_KEY=sua_chave_aqui
```

#### OpenAI (Pago)
1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Obtenha API key
3. Configure no `.env`:
```env
OPENAI_API_KEY=sua_chave_aqui
```

### Arquivo .env Completo
```env
# Google Sheets
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
SPREADSHEET_NAME=Dashboard Financeiro Pessoal
GOOGLE_DRIVE_FOLDER_ID=

# APIs para categorização
OPENAI_API_KEY=
GROQ_API_KEY=

# Configurações
DEFAULT_CURRENCY=BRL
```

## 📱 Como Usar

### 🚀 Dashboard Interativo

1. Execute `python main.py`
2. Escolha "Dashboard Interativo"
3. Use os filtros para análise
4. Navegue pelas abas:
   - **Visão Geral**: Métricas principais
   - **Custos Fixos**: Análise de gastos recorrentes
   - **Tendências**: Evolução temporal
   - **Detalhada**: Dados completos
   - **Google Sheets**: Sincronização

### 🤖 Categorização Automática

```bash
python llm_categorizer.py
```

**Funcionalidades:**
- Categoriza transações não categorizadas
- Usa IA (Groq/OpenAI) ou regras inteligentes
- Mantém cache para eficiência
- Exporta dados categorizados

### ☁️ Sincronização Google Sheets

```bash
python google_sheets_sync.py
```

**Planilhas criadas:**
- `Dados_Completos`: Todas as transações
- `Resumo_Mensal`: Análise por mês
- `Resumo_Categorias`: Gastos por categoria
- `Custos_Fixos_vs_Variaveis`: Análise de custos
- `Top_50_Gastos`: Maiores gastos

### 📈 Análise Avançada

```bash
python advanced_analytics.py
```

**Relatórios gerados:**
- Score de saúde financeira (0-100)
- Detecção de anomalias e alertas
- Padrões de gasto por dia/categoria
- Previsões para próximos meses
- Exportação em JSON/TXT

## 📊 Exemplos de Análises

### Score de Saúde Financeira
- **80-100**: Excelente
- **65-79**: Boa
- **50-64**: Regular
- **35-49**: Ruim
- **0-34**: Crítica

### Alertas Automáticos
- 🚨 **Gastos elevados**: Detecta meses com gastos anômalos
- ⚠️ **Taxa de poupança baixa**: <10% ou déficit
- 📊 **Categorias excessivas**: >30% em uma categoria
- 💸 **Transações incomuns**: Valores muito acima da média

### Padrões Identificados
- **Dia da semana**: Quando você gasta mais
- **Sazonalidade**: Meses mais caros/baratos
- **Categorias**: Distribuição e variabilidade
- **Custos fixos**: Identificação automática

## 🔧 Comandos Úteis

```bash
# Launcher completo
python main.py

# Início rápido (sem menu)
python main.py quick

# Verificar sistema
python main.py check

# Executar dashboard diretamente
python main.py dashboard

# Executar análise diretamente
python main.py analyze
```

## 🐛 Solução de Problemas

### Erro: "Nenhum CSV encontrado"
**Solução:**
```bash
# Verificar se CSVs estão nas pastas corretas
ls data/raw/*.csv
ls extratos/*.csv
ls *.csv

# Ou use o launcher para configurar pasta
python main.py → Configuração Inicial
```

### Erro: "Dependência não encontrada"
**Solução:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar individualmente
pip install streamlit pandas plotly gspread numpy
```

### Erro: "Google Sheets não conecta"
**Solução:**
1. Verificar se arquivo `credentials/google_credentials.json` existe
2. Verificar se APIs estão habilitadas no Google Cloud
3. Testar conexão: `python main.py → Configurações → Testar Google Sheets`

### Erro: "LLM não funciona"
**Solução:**
1. Verificar se chave API está no `.env`
2. Testar conexão com internet
3. Usar modo "apenas regras" como alternativa

### Erro: "CSV com encoding errado"
**Solução:**
```bash
# Converter encoding (Linux/Mac)
iconv -f iso-8859-1 -t utf-8 arquivo.csv > arquivo_utf8.csv

# Ou salvar CSV como UTF-8 no Excel
```

### Erro: "Streamlit não abre"
**Solução:**
```bash
# Verificar se Streamlit está instalado
pip install streamlit

# Executar manualmente
streamlit run dashboard.py

# Verificar porta
streamlit run dashboard.py --server.port 8502
```

## 📈 Personalização

### Adicionar Novas Categorias

Edite `llm_categorizer.py`:
```python
self.categories = [
    'Alimentação', 'Receitas', 'Saúde', 'Mercado',
    'Sua_Nova_Categoria'  # Adicionar aqui
]
```

### Configurar Custos Fixos

Edite padrões em `advanced_analytics.py`:
```python
fixed_patterns = {
    'Moradia': ['ALUGUEL', 'CONDOMINIO'],
    'Sua_Categoria': ['PALAVRA_CHAVE']
}
```

### Alterar Thresholds de Alertas

```python
self.alert_thresholds = {
    'expense_spike': 1.5,      # 50% acima da média
    'low_savings_rate': 10,    # Menos de 10%
    'category_limit': 0.3      # Mais de 30% em categoria
}
```

## 🎯 Casos de Uso

### 👤 Uso Pessoal
- Controle de gastos mensais
- Identificação de padrões de consumo
- Planejamento financeiro
- Acompanhamento de metas de poupança

### 👨‍👩‍👧‍👦 Uso Familiar
- Análise de gastos familiares
- Identificação de custos fixos
- Planejamento de orçamento
- Relatórios para tomada de decisão

### 📊 Análise Avançada
- Detecção de anomalias
- Previsões financeiras
- Score de saúde financeira
- Relatórios executivos

## 🔄 Atualizações e Manutenção

### Backup dos Dados
```bash
# Backup automático no Google Sheets
python google_sheets_sync.py

# Backup local
cp -r data/ backup_$(date +%Y%m%d)/
```

### Limpeza de Cache
```bash
# Limpar cache de categorização
rm categorization_cache.json

# Limpar dados processados
rm -rf data/processed/*
```

### Atualização do Sistema
```bash
# Baixar nova versão
git pull  # Se usando Git

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Verificar compatibilidade
python main.py check
```

## 📞 Suporte

### 🔍 Debugging
1. Execute `python main.py check` para diagnóstico
2. Verifique logs no terminal
3. Teste módulos individualmente

### 📚 Recursos Úteis
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Plotly Documentation](https://plotly.com/python/)

### 🐛 Reportar Problemas
1. Execute diagnóstico completo
2. Documente passos para reproduzir
3. Inclua mensagens de erro completas
4. Especifique sistema operacional e versão Python

## 🚀 Roadmap Futuro

### Próximas Funcionalidades
- [ ] **Dashboard mobile** responsivo
- [ ] **Importação automática** via API bancária
- [ ] **Metas financeiras** e acompanhamento
- [ ] **Análise comparativa** com benchmarks
- [ ] **Notificações** por email/WhatsApp
- [ ] **Machine Learning** para previsões avançadas

### Integrações Planejadas
- [ ] **Mais bancos**: Itaú, Bradesco, Santander
- [ ] **Cartões de crédito**: Nubank, outros
- [ ] **Investimentos**: B3, corretoras
- [ ] **Planilhas**: Excel, LibreOffice

## 📜 Licença

Este projeto é open source e pode ser usado livremente para fins pessoais e educacionais.

## 🙏 Agradecimentos

- **Streamlit** pela plataforma de dashboard
- **Plotly** pelas visualizações interativas
- **Pandas** pelo processamento de dados
- **Google** pelas APIs de integração
- **Comunidade Python** pelo ecossistema

---

**💡 Dica:** Comece com o launcher principal (`python main.py`) e siga o fluxo de configuração inicial para uma experiência mais suave!

**🔒 Lembrete:** Seus dados financeiros são processados localmente e nunca compartilhados. O Google Sheets é opcional e controlado por você.