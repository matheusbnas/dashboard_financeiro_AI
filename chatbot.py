"""
Chatbot Financeiro Inteligente
Analisa extratos e responde perguntas sobre finanças
Integrado ao Dashboard Principal
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import glob
import json
from typing import Dict, List, Any
import re

# Importações condicionais para LLMs
try:
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class FinancialChatbot:
    """Chatbot especializado em análise financeira"""
    
    def __init__(self):
        self.df = None
        self.llm = None
        self.setup_llm()
        self.conversation_history = []
        
        # Contexto financeiro para o chatbot
        self.financial_context = {
            'categories': [
                'Alimentação', 'Receitas', 'Saúde', 'Mercado', 'Educação',
                'Compras', 'Transporte', 'Investimento', 'Transferências para terceiros',
                'Telefone', 'Moradia', 'Entretenimento', 'Lazer', 'Outros'
            ],
            'nubank_patterns': {
                'Alimentação': ['restaurante', 'lanchonete', 'padaria', 'ifood', 'uber eats'],
                'Mercado': ['supermercado', 'mercado', 'carrefour', 'extra'],
                'Transporte': ['posto', 'combustivel', 'uber', 'taxi'],
                'Saúde': ['farmacia', 'drogaria', 'medico', 'hospital'],
                'Moradia': ['aluguel', 'condominio', 'luz', 'energia', 'agua'],
                'Telefone': ['claro', 'tim', 'vivo', 'oi']
            }
        }
    
    def setup_llm(self):
        """Configura o modelo de linguagem"""
        if not LLM_AVAILABLE:
            return
        
        # Verificar qual provider está disponível
        groq_key = os.getenv('GROQ_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        try:
            if groq_key:
                self.llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    api_key=groq_key
                )
                st.session_state.llm_provider = "Groq (Llama)"
            elif openai_key:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.1,
                    api_key=openai_key
                )
                st.session_state.llm_provider = "OpenAI (GPT)"
            else:
                st.session_state.llm_provider = "Regras Locais"
        except Exception as e:
            st.error(f"Erro ao configurar LLM: {e}")
            st.session_state.llm_provider = "Regras Locais"
    
    def load_financial_data(self):
        """Carrega dados financeiros disponíveis"""
        try:
            # Procurar arquivos CSV
            csv_patterns = [
                "Nubank_*.csv",
                "*.csv",
                "data/raw/*.csv",
                "extratos/*.csv"
            ]
            
            all_files = []
            for pattern in csv_patterns:
                files = glob.glob(pattern)
                all_files.extend(files)
            
            if not all_files:
                return None
            
            # Priorizar arquivos Nubank
            nubank_files = [f for f in all_files if 'Nubank_' in f]
            files_to_use = nubank_files if nubank_files else all_files
            
            dfs = []
            for file in files_to_use:
                try:
                    # Tentar diferentes encodings
                    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                        try:
                            df = pd.read_csv(file, encoding=encoding)
                            df['arquivo_origem'] = os.path.basename(file)
                            dfs.append(df)
                            break
                        except UnicodeDecodeError:
                            continue
                except Exception:
                    continue
            
            if not dfs:
                return None
            
            # Combinar todos os DataFrames
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # Processar dados
            return self.process_data(combined_df)
            
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None
    
    def process_data(self, df):
        """Processa dados financeiros"""
        if df.empty:
            return None
        
        # Detectar formato Nubank
        is_nubank = all(col in df.columns for col in ['date', 'title', 'amount'])
        
        if is_nubank:
            # Processar formato Nubank
            df['Data'] = pd.to_datetime(df['date'], errors='coerce')
            df['Descrição'] = df['title'].fillna('Sem descrição')
            df['Valor'] = pd.to_numeric(df['amount'], errors='coerce')
        else:
            # Processar formato tradicional
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            if 'Descrição' not in df.columns:
                df['Descrição'] = 'Sem descrição'
        
        # Limpar dados inválidos
        df = df.dropna(subset=['Data', 'Valor'])
        
        # Criar colunas auxiliares
        df['Tipo'] = df['Valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
        df['Valor_Absoluto'] = df['Valor'].abs()
        df['Mes'] = df['Data'].dt.to_period('M')
        df['Mes_Str'] = df['Data'].dt.strftime('%Y-%m')
        df['Ano'] = df['Data'].dt.year
        df['Mes_Nome'] = df['Data'].dt.strftime('%B')
        df['Dia_Semana'] = df['Data'].dt.day_name()
        
        # Categorização básica se não existir
        if 'Categoria' not in df.columns:
            df['Categoria'] = df['Descrição'].apply(self.categorize_basic)
        
        return df
    
    def categorize_basic(self, description):
        """Categorização básica por regras"""
        desc_lower = str(description).lower()
        
        for category, patterns in self.financial_context['nubank_patterns'].items():
            if any(pattern in desc_lower for pattern in patterns):
                return category
        
        return 'Outros'
    
    def analyze_data(self, df):
        """Analisa dados financeiros e retorna insights"""
        if df is None or df.empty:
            return {}
        
        insights = {}
        
        # Estatísticas básicas
        insights['total_transacoes'] = len(df)
        insights['periodo'] = {
            'inicio': df['Data'].min(),
            'fim': df['Data'].max(),
            'dias': (df['Data'].max() - df['Data'].min()).days
        }
        
        # Receitas e Despesas
        receitas = df[df['Tipo'] == 'Receita']
        despesas = df[df['Tipo'] == 'Despesa']
        
        insights['receitas'] = {
            'total': receitas['Valor_Absoluto'].sum() if not receitas.empty else 0,
            'quantidade': len(receitas),
            'media': receitas['Valor_Absoluto'].mean() if not receitas.empty else 0
        }
        
        insights['despesas'] = {
            'total': despesas['Valor_Absoluto'].sum() if not despesas.empty else 0,
            'quantidade': len(despesas),
            'media': despesas['Valor_Absoluto'].mean() if not despesas.empty else 0
        }
        
        insights['saldo'] = insights['receitas']['total'] - insights['despesas']['total']
        
        # Análise mensal
        monthly_expenses = despesas.groupby('Mes_Str')['Valor_Absoluto'].sum()
        if not monthly_expenses.empty:
            insights['gastos_mensais'] = {
                'media': monthly_expenses.mean(),
                'maior': monthly_expenses.max(),
                'menor': monthly_expenses.min(),
                'mes_maior_gasto': monthly_expenses.idxmax(),
                'mes_menor_gasto': monthly_expenses.idxmin()
            }
        
        # Top categorias
        if not despesas.empty and 'Categoria' in despesas.columns:
            top_categories = despesas.groupby('Categoria')['Valor_Absoluto'].sum().sort_values(ascending=False)
            insights['top_categorias'] = top_categories.head(5).to_dict()
        
        # Top estabelecimentos (se dados Nubank)
        if not despesas.empty:
            top_establishments = despesas['Descrição'].value_counts().head(10)
            insights['estabelecimentos_frequentes'] = top_establishments.to_dict()
        
        # Padrões de gasto
        insights['padroes'] = {
            'dia_semana_mais_gasto': despesas.groupby('Dia_Semana')['Valor_Absoluto'].sum().idxmax() if not despesas.empty else 'N/A',
            'mes_mais_gasto': despesas.groupby('Mes_Nome')['Valor_Absoluto'].sum().idxmax() if not despesas.empty else 'N/A'
        }
        
        return insights
    
    def generate_response(self, question: str, context: Dict) -> str:
        """Gera resposta usando LLM ou regras"""
        
        if self.llm and LLM_AVAILABLE:
            return self.llm_response(question, context)
        else:
            return self.rule_based_response(question, context)
    
    def llm_response(self, question: str, context: Dict) -> str:
        """Resposta usando LLM"""
        
        # Criar contexto para o LLM
        context_str = self.format_context_for_llm(context)
        
        prompt = PromptTemplate.from_template("""
Você é um assistente financeiro especializado em análise de extratos bancários e dados do Nubank.

CONTEXTO DOS DADOS FINANCEIROS:
{context}

HISTÓRICO DA CONVERSA:
{history}

PERGUNTA DO USUÁRIO: {question}

Instruções:
- Responda de forma clara e direta
- Use os dados fornecidos para fundamentar sua resposta
- Seja específico com números quando relevante
- Se não houver dados suficientes, explique isso
- Mantenha um tom profissional mas amigável
- Ofereça insights práticos quando possível

RESPOSTA:
""")
        
        try:
            # Preparar histórico
            history_str = "\n".join([
                f"Usuário: {msg['user']}\nAssistente: {msg['assistant']}" 
                for msg in self.conversation_history[-3:]  # Últimas 3 interações
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                "context": context_str,
                "history": history_str,
                "question": question
            })
            
            return response.strip()
            
        except Exception as e:
            return f"Desculpe, houve um erro ao processar sua pergunta: {str(e)}. Vou tentar responder com base nas regras básicas.\n\n" + self.rule_based_response(question, context)
    
    def format_context_for_llm(self, context: Dict) -> str:
        """Formata contexto para o LLM"""
        if not context:
            return "Nenhum dado financeiro carregado."
        
        context_parts = []
        
        # Estatísticas básicas
        context_parts.append(f"PERÍODO: {context.get('periodo', {}).get('inicio', 'N/A')} até {context.get('periodo', {}).get('fim', 'N/A')}")
        context_parts.append(f"TOTAL DE TRANSAÇÕES: {context.get('total_transacoes', 0):,}")
        
        # Receitas e despesas
        receitas = context.get('receitas', {})
        despesas = context.get('despesas', {})
        context_parts.append(f"RECEITAS: R$ {receitas.get('total', 0):,.2f} ({receitas.get('quantidade', 0)} transações)")
        context_parts.append(f"DESPESAS: R$ {despesas.get('total', 0):,.2f} ({despesas.get('quantidade', 0)} transações)")
        context_parts.append(f"SALDO: R$ {context.get('saldo', 0):,.2f}")
        
        # Gastos mensais
        gastos_mensais = context.get('gastos_mensais', {})
        if gastos_mensais:
            context_parts.append(f"GASTO MENSAL MÉDIO: R$ {gastos_mensais.get('media', 0):,.2f}")
            context_parts.append(f"MAIOR GASTO MENSAL: R$ {gastos_mensais.get('maior', 0):,.2f} em {gastos_mensais.get('mes_maior_gasto', 'N/A')}")
        
        # Top categorias
        top_categorias = context.get('top_categorias', {})
        if top_categorias:
            context_parts.append("TOP CATEGORIAS DE GASTO:")
            for cat, valor in list(top_categorias.items())[:3]:
                context_parts.append(f"  - {cat}: R$ {valor:,.2f}")
        
        # Estabelecimentos frequentes
        estabelecimentos = context.get('estabelecimentos_frequentes', {})
        if estabelecimentos:
            context_parts.append("ESTABELECIMENTOS MAIS FREQUENTES:")
            for est, freq in list(estabelecimentos.items())[:3]:
                context_parts.append(f"  - {est}: {freq} vezes")
        
        # Padrões
        padroes = context.get('padroes', {})
        if padroes:
            context_parts.append(f"DIA DA SEMANA COM MAIS GASTOS: {padroes.get('dia_semana_mais_gasto', 'N/A')}")
            context_parts.append(f"MÊS COM MAIS GASTOS: {padroes.get('mes_mais_gasto', 'N/A')}")
        
        return "\n".join(context_parts)
    
    def rule_based_response(self, question: str, context: Dict) -> str:
        """Resposta baseada em regras quando LLM não está disponível"""
        
        question_lower = question.lower()
        
        if not context:
            return "📊 Ainda não foram carregados dados financeiros. Use o botão 'Carregar Dados' no sidebar para começar a análise."
        
        # Perguntas sobre gastos totais
        if any(word in question_lower for word in ['quanto gastei', 'total gasto', 'despesas totais']):
            total_despesas = context.get('despesas', {}).get('total', 0)
            quantidade = context.get('despesas', {}).get('quantidade', 0)
            return f"💸 **Total de Despesas:** R$ {total_despesas:,.2f} em {quantidade} transações.\n\n📊 Isso representa uma média de R$ {total_despesas/quantidade:.2f} por transação." if quantidade > 0 else "Nenhuma despesa encontrada."
        
        # Perguntas sobre receitas
        elif any(word in question_lower for word in ['receitas', 'ganhos', 'entradas']):
            total_receitas = context.get('receitas', {}).get('total', 0)
            quantidade = context.get('receitas', {}).get('quantidade', 0)
            saldo = context.get('saldo', 0)
            response = f"💰 **Total de Receitas:** R$ {total_receitas:,.2f} em {quantidade} transações."
            if saldo > 0:
                response += f"\n\n✅ **Saldo Positivo:** R$ {saldo:,.2f}"
            elif saldo < 0:
                response += f"\n\n⚠️ **Déficit:** R$ {abs(saldo):,.2f}"
            return response
        
        # Perguntas sobre saldo
        elif any(word in question_lower for word in ['saldo', 'sobrou', 'restou']):
            saldo = context.get('saldo', 0)
            if saldo > 0:
                return f"✅ **Saldo Positivo:** R$ {saldo:,.2f}\n\nParabéns! Você conseguiu economizar este mês."
            elif saldo < 0:
                return f"⚠️ **Déficit:** R$ {abs(saldo):,.2f}\n\nAtenção: Suas despesas superaram as receitas."
            else:
                return "⚖️ **Saldo Neutro:** Receitas e despesas se equilibraram."
        
        # Perguntas sobre categorias
        elif any(word in question_lower for word in ['categoria', 'onde gasto mais', 'maior gasto']):
            top_categorias = context.get('top_categorias', {})
            if top_categorias:
                response = "🏷️ **Suas principais categorias de gasto:**\n\n"
                for i, (categoria, valor) in enumerate(list(top_categorias.items())[:5], 1):
                    response += f"{i}. **{categoria}:** R$ {valor:,.2f}\n"
                return response
            return "Não foi possível identificar as categorias de gasto."
        
        # Perguntas sobre estabelecimentos
        elif any(word in question_lower for word in ['estabelecimento', 'loja', 'onde compro']):
            estabelecimentos = context.get('estabelecimentos_frequentes', {})
            if estabelecimentos:
                response = "🏪 **Estabelecimentos onde você mais compra:**\n\n"
                for i, (estabelecimento, freq) in enumerate(list(estabelecimentos.items())[:5], 1):
                    response += f"{i}. **{estabelecimento}:** {freq} compras\n"
                return response
            return "Não foi possível identificar os estabelecimentos mais frequentes."
        
        # Perguntas sobre gastos mensais
        elif any(word in question_lower for word in ['mensal', 'por mês', 'média mensal']):
            gastos_mensais = context.get('gastos_mensais', {})
            if gastos_mensais:
                response = f"📅 **Análise de Gastos Mensais:**\n\n"
                response += f"• **Média mensal:** R$ {gastos_mensais.get('media', 0):,.2f}\n"
                response += f"• **Maior gasto:** R$ {gastos_mensais.get('maior', 0):,.2f} em {gastos_mensais.get('mes_maior_gasto', 'N/A')}\n"
                response += f"• **Menor gasto:** R$ {gastos_mensais.get('menor', 0):,.2f} em {gastos_mensais.get('mes_menor_gasto', 'N/A')}\n"
                return response
            return "Não foi possível calcular a média mensal de gastos."
        
        # Perguntas sobre padrões
        elif any(word in question_lower for word in ['padrão', 'quando gasto', 'dia da semana']):
            padroes = context.get('padroes', {})
            if padroes:
                response = f"📊 **Padrões de Gastos:**\n\n"
                response += f"• **Dia da semana com mais gastos:** {padroes.get('dia_semana_mais_gasto', 'N/A')}\n"
                response += f"• **Mês com mais gastos:** {padroes.get('mes_mais_gasto', 'N/A')}\n"
                return response
            return "Não foi possível identificar padrões nos seus gastos."
        
        # Pergunta geral sobre dados
        elif any(word in question_lower for word in ['resumo', 'overview', 'geral']):
            total_transacoes = context.get('total_transacoes', 0)
            periodo = context.get('periodo', {})
            total_despesas = context.get('despesas', {}).get('total', 0)
            total_receitas = context.get('receitas', {}).get('total', 0)
            saldo = context.get('saldo', 0)
            
            response = f"📊 **Resumo Financeiro:**\n\n"
            response += f"• **Período:** {periodo.get('inicio', 'N/A')} até {periodo.get('fim', 'N/A')}\n"
            response += f"• **Total de transações:** {total_transacoes:,}\n"
            response += f"• **Receitas:** R$ {total_receitas:,.2f}\n"
            response += f"• **Despesas:** R$ {total_despesas:,.2f}\n"
            
            if saldo > 0:
                response += f"• **Saldo:** ✅ R$ {saldo:,.2f} (positivo)\n"
            elif saldo < 0:
                response += f"• **Saldo:** ⚠️ R$ {abs(saldo):,.2f} (déficit)\n"
            else:
                response += f"• **Saldo:** ⚖️ Equilibrado\n"
            
            return response
        
        # Resposta padrão
        else:
            return f"""🤖 **Posso te ajudar com várias análises financeiras!**

📊 **Perguntas que posso responder:**
• Quanto gastei este mês?
• Qual meu saldo atual?
• Onde gasto mais dinheiro?
• Quais são meus estabelecimentos favoritos?
• Como estão meus gastos mensais?
• Quais são meus padrões de gasto?
• Me dê um resumo geral

💡 **Dica:** Seja específico em suas perguntas para respostas mais detalhadas!"""
    
    def add_to_history(self, user_msg: str, assistant_msg: str):
        """Adiciona interação ao histórico"""
        self.conversation_history.append({
            'user': user_msg,
            'assistant': assistant_msg,
            'timestamp': datetime.now()
        })
        
        # Manter apenas últimas 10 interações
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

def render_chatbot():
    """Renderiza interface do chatbot"""
    st.title("🤖 Assistente Financeiro Inteligente")
    
    # Inicializar chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = FinancialChatbot()
    
    chatbot = st.session_state.chatbot
    
    # Carregar dados se não estiverem carregados
    if chatbot.df is None:
        with st.spinner("🔄 Carregando dados financeiros..."):
            chatbot.df = chatbot.load_financial_data()
        
        if chatbot.df is not None:
            st.success(f"✅ Dados carregados: {len(chatbot.df):,} transações")
            st.session_state.financial_context = chatbot.analyze_data(chatbot.df)
        else:
            st.warning("⚠️ Nenhum dado financeiro encontrado. Coloque seus extratos CSV na pasta atual ou data/raw/")
            st.session_state.financial_context = {}
    
    # Status do sistema
    col1, col2 = st.columns(2)
    with col1:
        if chatbot.df is not None:
            st.success(f"📊 {len(chatbot.df):,} transações carregadas")
        else:
            st.error("❌ Nenhum dado carregado")
    
    with col2:
        if hasattr(st.session_state, 'llm_provider'):
            st.info(f"🤖 IA: {st.session_state.llm_provider}")
        else:
            st.info("🤖 IA: Não configurada")
    
    # Botão para recarregar dados
    if st.button("🔄 Recarregar Dados"):
        st.session_state.chatbot.df = None
        st.session_state.chatbot = FinancialChatbot()
        st.rerun()
    
    st.markdown("---")
    
    # Interface do chat
    st.subheader("💬 Converse sobre suas finanças")
    
    # Inicializar histórico de mensagens
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": """👋 **Olá! Sou seu assistente financeiro.**

🎯 **Posso te ajudar com:**
• Análise de gastos e receitas
• Identificação de padrões de consumo
• Insights sobre estabelecimentos favoritos
• Comparações mensais
• Dicas de economia

💬 **Como posso te ajudar hoje?**"""
            }
        ]
    
    # Exibir mensagens do chat
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input do usuário
    if prompt := st.chat_input("Digite sua pergunta sobre finanças..."):
        # Adicionar mensagem do usuário
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Exibir mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gerar resposta
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando seus dados..."):
                context = st.session_state.get('financial_context', {})
                response = chatbot.generate_response(prompt, context)
                
                st.markdown(response)
                
                # Adicionar ao histórico
                chatbot.add_to_history(prompt, response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Sidebar com estatísticas rápidas
    with st.sidebar:
        st.markdown("### 📊 Estatísticas Rápidas")
        
        context = st.session_state.get('financial_context', {})
        if context:
            # Período
            periodo = context.get('periodo', {})
            if periodo.get('inicio'):
                st.metric("📅 Período", f"{periodo['dias']} dias")
            
            # Transações
            st.metric("🔢 Transações", f"{context.get('total_transacoes', 0):,}")
            
            # Saldo
            saldo = context.get('saldo', 0)
            if saldo != 0:
                st.metric(
                    "💰 Saldo", 
                    f"R$ {saldo:,.2f}",
                    delta="Positivo" if saldo > 0 else "Déficit"
                )
            
            # Top categoria
            top_categorias = context.get('top_categorias', {})
            if top_categorias:
                top_cat = list(top_categorias.keys())[0]
                top_val = list(top_categorias.values())[0]
                st.metric("🏆 Top Categoria", top_cat, f"R$ {top_val:,.2f}")
            
        st.markdown("---")
        
        # Perguntas sugeridas
        st.markdown("### 💡 Perguntas Sugeridas")
        
        suggested_questions = [
            "Quanto gastei este mês?",
            "Qual meu estabelecimento favorito?",
            "Como está meu saldo?",
            "Onde gasto mais dinheiro?",
            "Me dê um resumo geral"
        ]
        
        for question in suggested_questions:
            if st.button(f"❓ {question}", key=f"suggested_{hash(question)}"):
                # Simular click no input
                st.session_state.suggested_question = question
                st.rerun()
        
        # Processar pergunta sugerida
        if hasattr(st.session_state, 'suggested_question'):
            question = st.session_state.suggested_question
            del st.session_state.suggested_question
            
            # Adicionar ao chat
            st.session_state.chat_messages.append({"role": "user", "content": question})
            
            # Gerar resposta
            context = st.session_state.get('financial_context', {})
            response = chatbot.generate_response(question, context)
            
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            chatbot.add_to_history(question, response)
            
            st.rerun()

if __name__ == "__main__":
    render_chatbot()