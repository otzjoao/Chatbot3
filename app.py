import streamlit as st
from huggingface_hub import InferenceClient
import unicodedata
import re
import time

from faq_data import FAQ


# ── Busca no dicionário FAQ ──────────────────────────────────────────────────
def normalizar(texto: str) -> str:
    """Remove acentos e coloca em minúsculo para comparação robusta."""
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return re.sub(r"[^\w\s]", "", "".join(c for c in nfkd if not unicodedata.combining(c)))


def buscar_faq(pergunta: str) -> str | None:
    """
    Verifica se alguma palavra-chave do dicionário está na pergunta.
    Retorna a resposta fixa se encontrar, ou None para chamar a API.
    """
    pergunta_norm = normalizar(pergunta)
    for entrada in FAQ:
        for palavra in entrada["palavras_chave"]:
            if normalizar(palavra) in pergunta_norm:
                return entrada["resposta"]
    return None

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="FAQ Acadêmico · UniBot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS Customizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Reset e base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fundo geral */
.stApp {
    background: #f5f0e8;
    background-image:
        radial-gradient(ellipse at 20% 0%, #d4e4f7 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, #e8d5f0 0%, transparent 50%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a1a2e !important;
    border-right: 2px solid #e8d5a3;
}
[data-testid="stSidebar"] * {
    color: #f0e6d3 !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e8d5a3 !important;
    font-family: 'DM Serif Display', serif !important;
}
[data-testid="stSidebar"] hr {
    border-color: #333355 !important;
}

/* Header principal */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-bottom: 2px solid #1a1a2e;
    margin-bottom: 1.5rem;
}
.main-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #1a1a2e;
    margin: 0;
    letter-spacing: -1px;
}
.main-header p {
    color: #5a5a7a;
    font-size: 0.95rem;
    font-weight: 300;
    margin: 0.3rem 0 0 0;
}

/* Balões de chat */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 0.5rem 0;
}

.msg-user {
    display: flex;
    justify-content: flex-end;
}
.msg-user .bubble {
    background: #1a1a2e;
    color: #f5f0e8;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem;
    max-width: 75%;
    font-size: 0.92rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(26,26,46,0.15);
}

.msg-bot {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 0.6rem;
}
.msg-bot .avatar {
    background: #e8d5a3;
    color: #1a1a2e;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    margin-top: 2px;
    border: 2px solid #1a1a2e;
}
.msg-bot .bubble {
    background: #ffffff;
    color: #1a1a2e;
    border-radius: 4px 18px 18px 18px;
    padding: 0.75rem 1.1rem;
    max-width: 75%;
    font-size: 0.92rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e0ddd5;
}

/* Digitando */
.typing-indicator {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 0.4rem 0;
}
.typing-indicator span {
    width: 8px; height: 8px;
    background: #5a5a7a;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); }
    30%            { transform: translateY(-6px); }
}

/* Input customizado */
.stChatInput {
    border-top: 2px solid #1a1a2e !important;
    padding-top: 0.8rem !important;
}
.stChatInput textarea {
    background: #fff !important;
    border: 1.5px solid #1a1a2e !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #1a1a2e !important;
}

/* Botão limpar */
.stButton button {
    background: transparent;
    border: 1.5px solid #e8d5a3;
    color: #e8d5a3 !important;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    transition: all 0.2s;
}
.stButton button:hover {
    background: #e8d5a3;
    color: #1a1a2e !important;
}

/* Chips de sugestão */
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0;
}
.chip {
    background: #fff;
    border: 1.5px solid #1a1a2e;
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.82rem;
    color: #1a1a2e;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'DM Sans', sans-serif;
}
.chip:hover {
    background: #1a1a2e;
    color: #f5f0e8;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #c5b99a; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 UniBot")
    st.markdown("**FAQ Acadêmico Inteligente**")
    st.markdown("---")

    hf_token = st.secrets.get("HF_TOKEN", "")

    st.markdown("---")
    st.markdown("### ⚙️ Configurações")

    temperature = st.slider("Criatividade", 0.1, 1.0, 0.4, 0.05,
                            help="Valores baixos = respostas mais diretas")
    max_tokens = st.slider("Tamanho da resposta", 100, 512, 256, 50)

    st.markdown("---")
    st.markdown("### 📚 Sobre")
    st.markdown("""
    Modelo: **Qwen2.5-1.5B-Instruct**  
    Parâmetros: **1.5 bilhões**  
    Idioma: 🇧🇷 Português  
    API: HuggingFace (gratuita)
    """)

    st.markdown("---")
    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.rerun()


# ── System prompt temático ───────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é o UniBot, assistente virtual acadêmico de uma universidade brasileira.
Responda SEMPRE em português do Brasil, de forma clara, organizada e amigável.
Você ajuda com dúvidas sobre:
- Matrícula, trancamento e rematrícula
- Calendário acadêmico e datas importantes
- Documentos e requerimentos
- Estágios, TCC e monografias
- Bolsas, auxílios e financiamento estudantil (FIES, ProUni)
- Biblioteca e acesso a materiais
- Aproveitamento de estudos e transferências
- Vida universitária em geral

Seja sempre prestativo. Se não souber algo específico da instituição, oriente o aluno onde buscar a informação correta."""


# ── Estado da sessão ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Função de chamada à API ──────────────────────────────────────────────────
def chat_with_qwen(messages: list, token: str, temperature: float, max_tokens: int) -> str:
    client = InferenceClient(
        model="Qwen/Qwen2.5-1.5B-Instruct",
        token=token,
    )

    hf_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    response = client.chat_completion(
        messages=hf_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎓 UniBot</h1>
    <p>Assistente de FAQ Acadêmico · Tire suas dúvidas universitárias</p>
</div>
""", unsafe_allow_html=True)


# ── Sugestões iniciais ────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; color:#5a5a7a; margin-bottom:1rem; font-size:0.9rem;">
        👋 Olá! Sou o UniBot. Como posso te ajudar hoje?<br>
        <small>Experimente perguntar sobre:</small>
    </div>
    <div class="chip-row" style="justify-content:center;">
        <span class="chip">📅 Calendário acadêmico</span>
        <span class="chip">📝 Como fazer matrícula?</span>
        <span class="chip">💰 Bolsas e auxílios</span>
        <span class="chip">📄 TCC e monografia</span>
        <span class="chip">🔄 Trancamento de curso</span>
    </div>
    """, unsafe_allow_html=True)


# ── Histórico de mensagens ───────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-wrapper">
            <div class="msg-user"><div class="bubble">{msg["content"]}</div></div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-wrapper">
            <div class="msg-bot">
                <div class="avatar">🎓</div>
                <div class="bubble">{msg["content"]}</div>
            </div>
        </div>""", unsafe_allow_html=True)


# ── Input do usuário ─────────────────────────────────────────────────────────
user_input = st.chat_input("Digite sua dúvida acadêmica...")

if user_input:
    if not hf_token:
        st.warning("⚠️ Insira seu token HuggingFace na barra lateral para usar o chatbot.")
        st.stop()

    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})

    st.markdown(f"""
    <div class="chat-wrapper">
        <div class="msg-user"><div class="bubble">{user_input}</div></div>
    </div>""", unsafe_allow_html=True)

    # Indicador de digitação
    with st.empty():
        st.markdown("""
        <div class="chat-wrapper">
            <div class="msg-bot">
                <div class="avatar">🎓</div>
                <div class="bubble">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        try:
            # 1️⃣ Primeiro consulta o dicionário local (instantâneo, sem API)
            response = buscar_faq(user_input)

            # 2️⃣ Se não achou no dicionário, chama a IA
            if response is None:
                response = chat_with_qwen(
                    st.session_state.messages,
                    hf_token,
                    temperature,
                    max_tokens
                )
            else:
                response = "📋 **Resposta do FAQ:**\n\n" + response

        except Exception as e:
            response = f"❌ Erro ao conectar com a API: {str(e)}\n\nVerifique se o token está correto e tente novamente."

        st.markdown(f"""
        <div class="chat-wrapper">
            <div class="msg-bot">
                <div class="avatar">🎓</div>
                <div class="bubble">{response}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
