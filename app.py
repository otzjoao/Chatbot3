import html
import json
import re
import unicodedata
import markdown as md_lib
from pathlib import Path

import streamlit as st
from huggingface_hub import InferenceClient

# ── Helpers de template ──────────────────────────────────────────────────────

def load_template(name: str) -> str:
    path = Path(__file__).parent / "templates" / name
    return path.read_text(encoding="utf-8")

def render_template(name: str, **kwargs) -> str:
    markup = load_template(name)
    for key, value in kwargs.items():
        markup = markup.replace(f"{{{{ {key} }}}}", str(value)) 
    return markup

def load_css() -> str:
    path = Path(__file__).parent / "styles" / "main.css"
    return path.read_text(encoding="utf-8")

def load_prompt(name: str) -> str:
    path = Path(__file__).parent / "prompts" / name
    return path.read_text(encoding="utf-8").strip()


def md_para_html(texto: str) -> str:
    """Converte Markdown para HTML seguro para injetar nos templates."""
    return md_lib.markdown(texto, extensions=["tables", "nl2br"])


# ── FAQ ──────────────────────────────────────────────────────────────────────

@st.cache_data
def carregar_faq() -> list[dict]:
    path = Path(__file__).parent / "faq_data.json"
    return json.loads(path.read_text(encoding="utf-8"))

def normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return re.sub(r"[^\w\s]", "", "".join(c for c in nfkd if not unicodedata.combining(c)))

def buscar_faq(pergunta: str) -> str | None:
    pergunta_norm = normalizar(pergunta)
    for entrada in carregar_faq():
        for palavra in entrada["palavras_chave"]:
            if normalizar(palavra) in pergunta_norm:
                return entrada["resposta"]
    return None


# ── Cliente Llama ────────────────────────────────────────────────────────────

def get_client(token: str) -> InferenceClient:
    if "hf_client" not in st.session_state or st.session_state.get("hf_token_used") != token:
        st.session_state.hf_client = InferenceClient(
            model="meta-llama/Llama-3.1-8B-Instruct",
            token=token,
        )
        st.session_state.hf_token_used = token
    return st.session_state.hf_client

def chat_with_llama(messages: list, token: str, temperature: float, max_tokens: int) -> tuple[str, bool]:
    client = get_client(token)
    system = [{"role": "system", "content": load_prompt("system_prompt.md")}]
    response = client.chat_completion(
        messages=system + messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    choice = response.choices[0]
    foi_cortado = choice.finish_reason == "length"
    return choice.message.content, foi_cortado


# ── Configuração da página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="UniBot · FAQ Acadêmico",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Tema: dark/light ─────────────────────────────────────────────────────────

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme_attr = "light" if st.session_state.theme == "light" else ""
theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"

if st.session_state.theme == "light":
    st.markdown("""
    <style>
        /* Altera o app completo e os inputs nativos /
        .stApp, [data-testid="stChatMessageContainer"], [data-testid="stChatInput"] {
            background-color: #f4f5fb !important;
            color: #0d1020 !important;
        }
        / Altera especificamente a caixa de texto do input do chat /
        [data-testid="stChatInput"] textarea {
            background-color: #ffffff !important;
            color: #0d1020 !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
        }
        / Variáveis customizadas para os seus templates HTML (header, balões) /
        .stApp {
            --bg-base: #f4f5fb !important;
            --bg-surface: #ffffff !important;
            --bg-glass: rgba(255,255,255,0.7) !important;
            --text-primary: #0d1020 !important;
            --text-secondary: #5a6080 !important;
            --text-muted: #aab0c4 !important;
            --bot-bg: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Garante que se voltar para o Dark, o input e o fundo voltem ao padrão escuro correto
    st.markdown("""
    <style>
        .stApp, [data-testid="stChatMessageContainer"], [data-testid="stChatInput"] {
            background-color: #0e1117 !important; / Cor padrão dark do streamlit */
            color: #fafafa !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Inject CSS + tema no <html>
css = load_css()
st.markdown(f"""
<style>{css}</style>
<script>
    // Aplica o atributo de tema ao elemento raiz
    document.documentElement.setAttribute('data-theme', '{st.session_state.theme}');
</script>
""", unsafe_allow_html=True)

# Fallback via classe no body (para o Streamlit)
if st.session_state.theme == "light":
    st.markdown("""
    <style>
      .stApp {
        --bg-base: #f4f5fb !important;
        --bg-surface: #ffffff !important;
        --bg-glass: rgba(255,255,255,0.7) !important;
        --bg-glass-hover: rgba(255,255,255,0.9) !important;
        --border: rgba(0,0,0,0.07) !important;
        --border-accent: rgba(79,142,247,0.3) !important;
        --text-primary: #0d1020 !important;
        --text-secondary: #5a6080 !important;
        --text-muted: #aab0c4 !important;
        --accent-glow: rgba(79,142,247,0.1) !important;
        --accent-glow-2: rgba(123,94,167,0.08) !important;
        --bot-bg: #ffffff !important;
        --bot-border: rgba(0,0,0,0.06) !important;
        --sidebar-bg: #fafbff !important;
        --sidebar-border: rgba(0,0,0,0.06) !important;
        --shadow-card: 0 4px 24px rgba(0,0,0,0.08) !important;
        --shadow-msg: 0 2px 12px rgba(0,0,0,0.06) !important;
      }
    </style>
    """, unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    col_logo, col_theme = st.columns([3, 1])
    with col_logo:
        st.markdown("## 🎓 UniBot")
        st.markdown("**FAQ Acadêmico Inteligente**")
    with col_theme:
        st.markdown("<div style='padding-top:0.6rem'></div>", unsafe_allow_html=True)
        if st.button(theme_icon, key="theme_toggle", help="Alternar tema"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    # st.markdown("---")

    hf_token = st.secrets.get("HF_TOKEN", "") if hasattr(st, "secrets") else ""
    if not hf_token:
        hf_token = st.text_input(
            "🔑 Token HuggingFace",
            type="password",
            placeholder="hf_...",
            help="Obtenha grátis em huggingface.co/settings/tokens",
        )

    temperature = 0.1
    max_tokens = 512

    st.markdown("---")
    st.markdown("### 📚 Sobre")
    st.markdown("""
    Modelo: **Llama-3.1-8B-Instruct**  
    Parâmetros: **8 bilhões**  
    Idioma: 🇧🇷 **Português**  
    API: **HuggingFace (gratuita)**  
    **Base: dez/2023**
    """)

    try:
        st.caption(f"📋 FAQ carregado: **{len(carregar_faq())} tópicos**")
    except Exception:
        st.caption("⚠️ faq_data.json não encontrado")

    st.markdown("---")
    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.rerun()


# ── Estado da sessão ─────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chip_selecionado" not in st.session_state:
    st.session_state.chip_selecionado = None

if "resposta_cortada" not in st.session_state:
    st.session_state.resposta_cortada = False


# ── Header e sugestões ───────────────────────────────────────────────────────

st.markdown(load_template("header.html"), unsafe_allow_html=True)

CHIPS = [
    ("📅", "Calendário acadêmico"),
    ("📝", "Como fazer matrícula?"),
    ("💰", "Bolsas e auxílios"),
    ("📄", "TCC e monografia"),
    ("🔄", "Trancamento de curso"),
]

if not st.session_state.messages:
    st.markdown(
        "<div style='text-align:center; color:var(--text-secondary,#7a8099); margin-bottom:1.2rem; font-size:0.88rem;'>"
        "👋 Olá! Sou o UniBot da Unigran Capital. Como posso te ajudar hoje?<br>"
        "<span style='font-size:0.82rem; opacity:0.7'>Experimente perguntar sobre:</span></div>",
        unsafe_allow_html=True,
    )
    _, c1, c2, c3, _ = st.columns([0.5, 2, 2, 2, 0.5])
    for col, (emoji, texto) in zip([c1, c2, c3], CHIPS[:3]):
        with col:
            if st.button(f"{emoji} {texto}", key=f"chip_{texto}", use_container_width=True):
                st.session_state.chip_selecionado = texto
                st.rerun()
    _, c4, c5, _ = st.columns([1.5, 2, 2, 1.5])
    for col, (emoji, texto) in zip([c4, c5], CHIPS[3:]):
        with col:
            if st.button(f"{emoji} {texto}", key=f"chip_{texto}", use_container_width=True):
                st.session_state.chip_selecionado = texto
                st.rerun()


# ── Histórico de mensagens ───────────────────────────────────────────────────

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(render_template("message_user.html", content=msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(render_template("message_bot.html", content=md_para_html(msg["content"])), unsafe_allow_html=True)


# ── Botão de continuar resposta ─────────────────────────────────────────────

if st.session_state.resposta_cortada:
    st.markdown(
        "<div style='text-align:center; color:var(--text-muted,#44485a); font-size:0.82rem; margin:0.5rem 0;'>"
        "⚠️ A resposta foi cortada por ser muito longa.</div>",
        unsafe_allow_html=True,
    )
    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        if st.button("➕ Continuar resposta", use_container_width=True):
            st.session_state.resposta_cortada = False
            if not hf_token:
                st.warning("⚠️ Insira seu token HuggingFace na barra lateral.")
                st.stop()
            with st.empty():
                st.markdown(load_template("typing.html"), unsafe_allow_html=True)
                try:
                    continuacao, foi_cortado = chat_with_llama(
                        st.session_state.messages + [{"role": "user", "content": "Continue a resposta do ponto onde parou."}],
                        hf_token,
                        temperature,
                        max_tokens,
                    )
                except Exception as e:
                    continuacao = f"❌ Erro ao continuar: {html.escape(str(e))}"
                    foi_cortado = False
                st.markdown(render_template("message_bot.html", content=md_para_html(continuacao)), unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": continuacao})
            st.session_state.resposta_cortada = foi_cortado
            # st.rerun()


# ── Input do usuário ─────────────────────────────────────────────────────────

user_input = st.chat_input("Digite sua dúvida acadêmica...") or st.session_state.chip_selecionado
st.session_state.chip_selecionado = None

if user_input:
    if not hf_token:
        st.warning("⚠️ Insira seu token HuggingFace na barra lateral para usar o chatbot.")
        st.stop()

    safe_input = html.escape(user_input)

    st.session_state.messages.append({"role": "user", "content": safe_input})
    st.markdown(render_template("message_user.html", content=safe_input), unsafe_allow_html=True)

    typing_placeholder = st.empty()
    typing_placeholder.markdown(load_template("typing.html"), unsafe_allow_html=True)

    try:
        response = buscar_faq(user_input)
        foi_cortado = False

        if response is None:
            response, foi_cortado = chat_with_llama(
                st.session_state.messages,
                hf_token,
                temperature,
                max_tokens,
            )
        else:
            response = "📋 **Resposta do FAQ:\n\n" + response

    except Exception as e:
        response = f"❌ Erro ao conectar com a API: {html.escape(str(e))}"
        foi_cortado = False

    typing_placeholder.empty()
    st.markdown(render_template("message_bot.html", content=md_para_html(response)), unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.resposta_cortada = foi_cortado
    if foi_cortado:
        st.rerun()
