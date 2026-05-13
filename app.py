import html
import json
import re
import unicodedata
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
    return f"<style>{path.read_text(encoding='utf-8')}</style>"

def load_prompt(name: str) -> str:
    path = Path(__file__).parent / "prompts" / name
    return path.read_text(encoding="utf-8").strip()


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


# ── Cliente Llama (instância única por sessão) ───────────────────────────────

def get_client(token: str) -> InferenceClient:
    """
    Reutiliza o cliente entre chamadas dentro da mesma sessão.
    Uma nova instância é criada apenas se o token mudar.
    """
    if "hf_client" not in st.session_state or st.session_state.get("hf_token_used") != token:
        st.session_state.hf_client = InferenceClient(
            model="meta-llama/Llama-3.1-8B-Instruct",
            token=token,
        )
        st.session_state.hf_token_used = token
    return st.session_state.hf_client

def chat_with_llama(messages: list, token: str, temperature: float, max_tokens: int) -> str:
    client = get_client(token)
    system = [{"role": "system", "content": load_prompt("system_prompt.md")}]
    response = client.chat_completion(
        messages=system + messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# ── Configuração da página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="FAQ Acadêmico · UniBot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(load_css(), unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎓 UniBot")
    st.markdown("**FAQ Acadêmico Inteligente**")
    st.markdown("---")

    hf_token = st.secrets.get("HF_TOKEN", "") if hasattr(st, "secrets") else ""
    if not hf_token:
        hf_token = st.text_input(
            "🔑 Token HuggingFace",
            type="password",
            placeholder="hf_...",
            help="Obtenha grátis em huggingface.co/settings/tokens",
        )

    st.markdown("---")
    st.markdown("### ⚙️ Configurações")
    temperature = st.slider("Criatividade", 0.1, 1.0, 0.4, 0.05,
                            help="Valores baixos = respostas mais diretas")
    max_tokens = st.slider("Tamanho da resposta", 100, 512, 256, 50)

    st.markdown("---")
    st.markdown("### 📚 Sobre")
    st.markdown("""
    Modelo: **Llama-3.1-8B-Instruct**
    Parâmetros: **8 bilhões**
    Idioma: 🇧🇷 Português
    API: HuggingFace (gratuita)
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


# ── Header e sugestões ───────────────────────────────────────────────────────

st.markdown(load_template("header.html"), unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(load_template("suggestions.html"), unsafe_allow_html=True)


# ── Histórico de mensagens ───────────────────────────────────────────────────

for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Conteúdo do usuário já foi escapado antes de salvar no histórico
        st.markdown(render_template("message_user.html", content=msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(render_template("message_bot.html", content=msg["content"]), unsafe_allow_html=True)


# ── Input do usuário ─────────────────────────────────────────────────────────

user_input = st.chat_input("Digite sua dúvida acadêmica...")

if user_input:
    if not hf_token:
        st.warning("⚠️ Insira seu token HuggingFace na barra lateral para usar o chatbot.")
        st.stop()

    # 🛡️ HTML injection: escapa tags e javascript do input antes de qualquer uso
    safe_input = html.escape(user_input)

    st.session_state.messages.append({"role": "user", "content": safe_input})
    st.markdown(render_template("message_user.html", content=safe_input), unsafe_allow_html=True)

    with st.empty():
        st.markdown(load_template("typing.html"), unsafe_allow_html=True)

        try:
            # 1️⃣ Consulta o JSON local (instantâneo, sem API)
            # A busca usa o input original (sem escape) para não quebrar acentos
            response = buscar_faq(user_input)

            # 2️⃣ Se não achou, chama a IA com o cliente reutilizado
            if response is None:
                response = chat_with_llama(
                    st.session_state.messages,
                    hf_token,
                    temperature,
                    max_tokens,
                )
            else:
                response = "📋 **Resposta do FAQ:**\n\n" + response

        except Exception as e:
            response = f"❌ Erro ao conectar com a API: {html.escape(str(e))}"

        st.markdown(render_template("message_bot.html", content=response), unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
