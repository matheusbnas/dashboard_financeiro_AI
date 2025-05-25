# 💰 Dashboard Financeiro Completo

Um sistema completo de análise financeira pessoal com dashboard interativo, categorização automática por IA, sincronização com Google Sheets e relatórios avançados.

**🎯 Especializado em extratos do cartão Nubank com estrutura organizacional profissional**

## 🚀 Características Principais

### ✨ Dashboard Interativo
- **Visualizações em tempo real** com Plotly
- **Métricas financeiras** detalhadas
- **Filtros avançados** por período, categoria e tipo
- **Análise de custos fixos vs variáveis**
- **Interface responsiva** para desktop e mobile
- **🏪 Análise de estabelecimentos** (onde você mais gasta vs frequenta)

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

## 📁 Estrutura Organizada do Projeto

```
dashboard_financeiro_AI/
├── 📄 main.py                      # 🚀 Launcher principal
├── 📄 dashboard.py                 # 📊 Dashboard interativo (Streamlit)
├── 📄 requirements.txt             # 📦 Dependências do projeto
├── 📄 README.md                    # 📖 Documentação (este arquivo)
├── 📄 .env                         # 🔑 Variáveis de ambiente
├── 📄 .gitignore                   # 🔒 Arquivos protegidos
├── 📄 config.json                  # ⚙️ Configurações do sistema
│
├── 📁 src/                          # 🏗️ MÓDULOS PRINCIPAIS
│   ├── 📄 __init__.py              # Inicialização do pacote
│   ├── 📄 llm_categorizer.py       # 🤖 Categorização com IA
│   ├── 📄 google_sheets_sync.py    # ☁️ Sincronização Google Sheets
│   ├── 📄 advanced_analytics.py    # 📈 Análise avançada e relatórios
│   ├── 📄 data_processor.py        # 🔄 Processamento de dados
│   └── 📄 expense_analyser.py      # 📊 Análise de gastos
│
├── 📁 config/                       # ⚙️ CONFIGURAÇÕES
│   └── 📄 settings.py              # Configurações centralizadas
│
├── 📁 css/                          # 🎨 ESTILOS VISUAIS
│   └── 📄 dashboard_styles.css     # CSS personalizado
│
├── 📁 data/                         # 📊 DADOS
│   ├── 📁 raw/                     # 📄 CSVs originais (protegido)
│   ├── 📁 processed/               # 🔄 Dados processados
│   └── 📁 exports/                 # 📤 Relatórios exportados
│
└── 📁 credentials/                  # 🔐 SEGURANÇA (protegido)
    └── 📄 google_credentials.json  # Credenciais Google API
```

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

# Instalar dependências
pip install -r requirements.txt

# Executar configuração automática
python main.py
```

### 2. Primeira Execução

1. Execute `python main.py`
2. Escolha "⚙️ Configuração Inicial"
3. Siga as instruções na tela
4. Coloque seus CSVs do Nubank na pasta `data/raw/`

### 3. Usar o Sistema

```bash
# 🎯 RECOMENDADO: Launcher completo
python main.py

# 📊 Dashboard direto
streamlit run dashboard.py

# 🤖 Categorização automática
python src/llm_categorizer.py

# ☁️ Sincronização Google Sheets  
python src/google_sheets_sync.py

# 📈 Análise avançada
python src/advanced_analytics.py
```

## 📊 Funcionamento de Cada Módulo

### 🚀 `main.py` - Centro de Controle
**Função:** Launcher principal com menu interativo
- Interface ASCII atrativa
- Verificação automática de módulos em `src/`
- Configuração inicial do ambiente
- Gerenciamento de configurações
- Status em tempo real do sistema

### 📊 `dashboard.py` - Interface Principal  
**Função:** Dashboard interativo especializado em cartão Nubank
- **6 abas organizadas:** Visão Geral, Custos Fixos, Tendências, Estabelecimentos, Dados, Relatórios
- **Análise única de estabelecimentos:** Onde você mais gasta vs frequenta
- **Modo Nubank:** Entende que só aparecem gastos (não receitas)
- **Visual otimizado:** CSS responsivo para modo claro/escuro

### 🤖 `src/llm_categorizer.py` - IA para Categorização
**Função:** Categorização automática inteligente
- **3 providers:** Groq (gratuito), OpenAI (pago), Regras locais
- **Sistema de cache:** Evita recategorizar transações similares
- **14 categorias:** Otimizadas para gastos brasileiros
- **Processamento em lote:** Performance otimizada

### ☁️ `src/google_sheets_sync.py` - Integração Cloud
**Função:** Sincronização com Google Sheets
- **5 planilhas automáticas:** Dados completos, Resumo mensal, Por categoria, Custos fixos, Top gastos
- **Service Account:** Autenticação segura
- **Modo rápido:** `quick_sync()` sem interação

### 📈 `src/advanced_analytics.py` - Análise Profunda
**Função:** Sistema completo de análise e alertas
- **Score de saúde financeira:** 0-100 com 4 componentes
- **5 tipos de alertas:** Gastos elevados, transações incomuns, déficit, etc.
- **Previsões:** Próximo mês baseado em tendências
- **Relatórios:** JSON completo, TXT resumido

## 📊 Formato dos Dados

### CSV do Nubank (obrigatório)
```csv
ID,Data,Valor,Descrição
20240101001,2024-01-01,-50.00,SUPERMERCADO XYZ LTDA
20240101002,2024-01-01,-25.30,POSTO DE COMBUSTIVEL ABC
20240101003,2024-01-02,-15.90,FARMACIA DROGASIL
```

### Campos obrigatórios:
- **ID**: Identificador único da transação
- **Data**: Data no formato YYYY-MM-DD ou DD/MM/YYYY
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

## 📱 Como Usar - Guia Completo

### 🚀 Fluxo Recomendado (Primeira Vez)

1. **Configuração inicial:**
   ```bash
   python main.py
   # Escolher: "5. Configuração Inicial"
   ```

2. **Adicionar dados:**
   - Baixe extratos do Nubank em CSV
   - Coloque na pasta `data/raw/`

3. **Categorização (opcional):**
   ```bash
   python main.py
   # Escolher: "2. Categorizar Transações"
   ```

4. **Dashboard principal:**
   ```bash
   python main.py  
   # Escolher: "1. Dashboard Interativo"
   ```

### 📊 Navegação no Dashboard

#### 📈 **Aba "Visão Geral"**
- **Cards de métricas:** Total gasto, transações, gasto médio
- **Gráfico de evolução:** Gastos mensais com tendência
- **Pizza de categorias:** Distribuição dos gastos
- **Gauge de economia:** Comparação mês anterior

#### 💡 **Aba "Custos Fixos vs Variáveis"**
- **Gráfico de barras:** Evolução mensal por tipo
- **Tabelas de análise:** Custos fixos identificados automaticamente
- **Distribuição:** Percentual fixo vs variável

#### 📈 **Aba "Tendências"**
- **Gráfico de linhas:** Top 6 categorias ao longo do tempo
- **Top gastos:** 15 maiores transações do período
- **Análise temporal:** Padrões de gasto

#### 🏪 **Aba "Estabelecimentos"** (Exclusiva!)
- **Mais usados no cartão:** Frequência de compras por local
- **Maiores gastos:** Estabelecimentos que mais custam
- **Busca avançada:** Encontrar estabelecimento específico
- **Estatísticas detalhadas:** Gasto médio, primeira/última compra

#### 📋 **Aba "Dados Brutos"**
- **Tabela completa:** Todas as transações
- **Filtros avançados:** Ordenação, quantidade de linhas
- **Download CSV:** Exportar dados filtrados

#### 📊 **Aba "Relatórios"**
- **4 tipos de relatório:** Mensal, Por categoria, Estabelecimentos, Custos fixos
- **Export:** Download em TXT

### 🤖 Categorização Automática

```bash
# Via launcher (recomendado)
python main.py → "2. Categorizar Transações"

# Direto
python src/llm_categorizer.py
```

**Funcionalidades:**
- Detecta transações não categorizadas
- Usa IA (Groq/OpenAI) ou regras inteligentes
- Mantém cache para eficiência
- Mostra progresso em tempo real
- Exporta dados categorizados

**Categorias disponíveis:**
`Alimentação`, `Receitas`, `Saúde`, `Mercado`, `Educação`, `Compras`, `Transporte`, `Investimento`, `Transferências para terceiros`, `Telefone`, `Moradia`, `Entretenimento`, `Lazer`, `Outros`

### ☁️ Sincronização Google Sheets

```bash
# Via launcher
python main.py → "3. Sincronizar Google Sheets"

# Direto
python src/google_sheets_sync.py
```

**Planilhas criadas automaticamente:**
- **`Dados_Completos`**: Todas as transações
- **`Resumo_Mensal`**: Receitas, despesas, saldo por mês
- **`Resumo_Categorias`**: Total, quantidade, média por categoria
- **`Custos_Fixos_vs_Variaveis`**: Análise temporal de custos
- **`Top_50_Gastos`**: Maiores transações

### 📈 Análise Avançada

```bash
# Via launcher  
python main.py → "4. Análise Avançada"

# Direto
python src/advanced_analytics.py
```

**Relatórios gerados:**

#### 🏥 **Score de Saúde Financeira (0-100)**
- **80-100**: Excelente 
- **65-79**: Boa
- **50-64**: Regular  
- **35-49**: Ruim
- **0-34**: Crítica

**Componentes do score:**
- Taxa de Poupança (30 pts)
- Diversificação de Gastos (20 pts)
- Estabilidade Mensal (25 pts)
- Controle de Gastos Grandes (25 pts)

#### 🚨 **Sistema de Alertas**
- **Gastos elevados:** 50% acima da média mensal
- **Transações incomuns:** 3 desvios padrão acima da média
- **Categorias excessivas:** Mais de 30% em uma categoria
- **Taxa de poupança baixa:** Menos de 10% ou déficit
- **Anomalias em custos fixos:** Variação de 20%+ em gastos recorrentes

#### 🔮 **Previsões Financeiras**
- **Próximo mês:** Baseado em média móvel de 3 meses
- **Tendência linear:** Projeção baseada em regressão
- **Sazonalidade:** Mesmo mês do ano anterior
- **Por categoria:** Previsão individual por tipo de gasto

## 🔧 Comandos Úteis

```bash
# 🎯 Menu principal (recomendado)
python main.py

# ⚡ Início rápido  
python main.py quick

# 🔍 Verificar sistema
python main.py check

# 📊 Dashboard direto
python main.py dashboard
# ou: streamlit run dashboard.py

# 📈 Análise direto
python main.py analyze  
# ou: python src/advanced_analytics.py

# 🔄 Verificar estrutura do projeto
python main.py → "7. Verificar Estrutura"
```

## 🐛 Solução de Problemas

### ❌ Erro: "Módulo não encontrado em src/"
```bash
# Verificar se arquivos estão na pasta correta
ls src/
# Deve conter: llm_categorizer.py, google_sheets_sync.py, advanced_analytics.py

# Verificar estrutura
python main.py check
```

### ❌ Erro: "Nenhum CSV encontrado"
```bash
# Verificar se CSVs estão nas pastas corretas  
ls data/raw/*.csv
ls extratos/*.csv
ls *.csv

# Configurar pasta personalizada
python main.py → "5. Configuração Inicial"
```

### ❌ Erro: "Dependência não encontrada"
```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar individualmente
pip install streamlit pandas plotly gspread numpy python-dotenv
pip install langchain-openai langchain-groq langchain-core
```

### ❌ Erro: "Google Sheets não conecta"
1. Verificar se `credentials/google_credentials.json` existe
2. Verificar se APIs estão habilitadas no Google Cloud
3. Testar conexão: `python main.py → 6. Configurações → Testar Google Sheets`

### ❌ Erro: "LLM não funciona"
1. Verificar se chave API está no `.env`
2. Testar conexão com internet
3. Usar modo "apenas regras" como alternativa

### ❌ Erro: "Import Error from src"
```bash
# Criar __init__.py se não existir
touch src/__init__.py

# Verificar se Python encontra a pasta
python -c "import sys; print('src' in sys.path)"
```

## 📈 Personalização

### Adicionar Novas Categorias

Edite `src/llm_categorizer.py`:
```python
self.categories = [
    'Alimentação', 'Receitas', 'Saúde', 'Mercado',
    'Sua_Nova_Categoria'  # Adicionar aqui
]
```

### Configurar Custos Fixos

Edite `src/advanced_analytics.py`:
```python
fixed_patterns = {
    'Moradia': ['ALUGUEL', 'CONDOMINIO'],
    'Sua_Categoria': ['PALAVRA_CHAVE']
}
```

### Personalizar Visual

Edite `css/dashboard_styles.css`:
```css
:root {
    --primary-color: #sua_cor;
    --accent-color: #sua_cor_secundaria;
}
```

## 🎯 Casos de Uso Específicos

### 👤 **Análise Pessoal do Cartão Nubank**
- Controle de gastos mensais no cartão
- Identificação de estabelecimentos mais frequentados
- Padrões de uso: onde, quando e quanto gasta
- Detecção de gastos anômalos ou fora do padrão

### 👨‍👩‍👧‍👦 **Controle Familiar**
- Análise consolidada de múltiplos cartões
- Identificação de custos fixos vs variáveis
- Planejamento de orçamento familiar
- Relatórios para decisões financeiras

### 📊 **Análise Avançada e Relatórios**
- Score de saúde financeira
- Detecção automática de anomalias
- Previsões baseadas em tendências históricas
- Relatórios executivos para planejamento

### 🏪 **Análise de Estabelecimentos** (Exclusivo!)
- Descobrir onde você **mais gasta** vs onde **mais frequenta**
- Otimizar cartão com base em estabelecimentos frequentes
- Identificar estabelecimentos caros vs baratos
- Histórico completo de compras por local

## 🔄 Manutenção do Sistema

### 💾 **Backup dos Dados**
```bash
# Backup automático no Google Sheets
python src/google_sheets_sync.py

# Backup local
cp -r data/ backup_$(date +%Y%m%d)/

# Backup de configurações
cp config.json config_backup.json
```

### 🧹 **Limpeza e Organização**
```bash
# Limpar cache de categorização
rm categorization_cache.json

# Limpar dados processados
rm -rf data/processed/*

# Verificar estrutura
python main.py → "7. Verificar Estrutura"
```

### 🔄 **Atualização do Sistema**
```bash
# Baixar nova versão (se usando Git)
git pull

# Atualizar dependências  
pip install -r requirements.txt --upgrade

# Verificar compatibilidade
python main.py check

# Migrar para estrutura src/ (se necessário)
python main.py → "5. Configuração Inicial"
```

## 🚀 Vantagens da Estrutura src/

### ✅ **Organização Profissional**
- **Separação clara:** Interface (raiz) vs Lógica (src/)
- **Imports limpos:** Módulos bem organizados
- **Manutenção fácil:** Código estruturado
- **Escalabilidade:** Fácil adicionar novos módulos

### ✅ **Melhor Performance**
- **Imports otimizados:** Python encontra módulos mais rápido
- **Cache eficiente:** Menos conflitos de namespace
- **Modularidade:** Carrega apenas o que precisa

### ✅ **Segurança Aprimorada**
- **Dados protegidos:** `data/` e `credentials/` isolados
- **Configurações centralizadas:** `config/` separado
- **Logs organizados:** Fácil auditoria

## 📞 Suporte e Recursos

### 🔍 **Debugging Avançado**
```bash
# Diagnóstico completo
python main.py check

# Verificar módulos src/
python main.py → "7. Verificar Estrutura"

# Testar módulos individualmente
python -c "from src import llm_categorizer; print('OK')"
```

### 📚 **Recursos Úteis**
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Plotly Documentation](https://plotly.com/python/)
- [Python Package Structure](https://docs.python.org/3/tutorial/modules.html)

### 🐛 **Reportar Problemas**
1. Execute `python main.py check` para diagnóstico
2. Verifique se módulos estão em `src/`
3. Documente passos para reproduzir o erro
4. Inclua mensagens de erro completas
5. Especifique SO e versão Python

## 🚀 Roadmap e Futuras Melhorias

### 📱 **Próximas Funcionalidades**
- [ ] **PWA (Progressive Web App)** para uso mobile
- [ ] **API REST** para integração com outros sistemas
- [ ] **Dashboards comparativos** entre períodos
- [ ] **Metas financeiras** com acompanhamento
- [ ] **Notificações inteligentes** por email/WhatsApp

### 🏦 **Mais Integrações**
- [ ] **Outros bancos:** Itaú, Bradesco, Santander
- [ ] **Cartões adicionais:** Diferentes bandeiras
- [ ] **Investimentos:** B3, corretoras
- [ ] **Open Banking:** APIs bancárias oficiais

### 🤖 **IA Avançada**
- [ ] **Machine Learning:** Previsões mais precisas
- [ ] **Detecção de fraudes:** Transações suspeitas
- [ ] **Recomendações personalizadas:** Baseado no perfil
- [ ] **Chatbot financeiro:** Assistente conversacional

## 📜 Licença e Créditos

Este projeto é **open source** e pode ser usado livremente para fins pessoais e educacionais.

### 🙏 **Agradecimentos**
- **Streamlit** pela plataforma de dashboard
- **Plotly** pelas visualizações interativas  
- **Pandas** pelo processamento de dados eficiente
- **Google** pelas APIs de integração robustas
- **Groq/OpenAI** pelos modelos de linguagem
- **Comunidade Python** pelo ecossistema incrível

---

## 🎯 **Começar Agora**

**Para iniciantes:**
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar launcher
python main.py

# 3. Seguir configuração inicial
# 4. Colocar CSVs em data/raw/
# 5. Usar o dashboard!
```

**Para usuários experientes:**
```bash
# Início rápido
python main.py quick

# Dashboard direto  
streamlit run dashboard.py

# Verificar tudo
python main.py check
```

---

**💡 Dica Final:** A estrutura `src/` mantém seu projeto organizado e profissional. Use sempre o launcher `python main.py` para melhor experiência!

**🔒 Lembrete de Segurança:** Todos os dados são processados localmente. Suas informações financeiras nunca saem do seu computador, exceto quando você escolhe sincronizar com seu próprio Google Sheets.