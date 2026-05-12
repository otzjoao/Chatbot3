# 🎓 UniBot — FAQ Acadêmico com HuggingFace + Streamlit

Chatbot temático para dúvidas universitárias, usando o modelo **Qwen2.5-1.5B-Instruct** (gratuito via HuggingFace Inference API) e interface em **Streamlit**.

---

## 📁 Estrutura do projeto

```
chatbot_faq/
├── app.py            # Aplicação principal
├── requirements.txt  # Dependências Python
└── README.md         # Este arquivo
```

---

## 🚀 Como rodar localmente

### 1. Clone / baixe os arquivos

Coloque os arquivos numa pasta, ex: `chatbot_faq/`

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Obtenha seu token HuggingFace (gratuito)

1. Acesse: https://huggingface.co/settings/tokens
2. Clique em **"New token"**
3. Escolha tipo **"Read"** (gratuito)
4. Copie o token gerado (começa com `hf_...`)

### 5. Execute o app

```bash
streamlit run app.py
```

O browser abrirá automaticamente em `http://localhost:8501`

### 6. Insira o token na interface

Na barra lateral esquerda, cole seu token HuggingFace no campo **"🔑 Token HuggingFace"**.

---

## 🌐 Deploy gratuito no Streamlit Cloud

1. Faça upload do projeto num repositório GitHub
2. Acesse https://share.streamlit.io
3. Conecte seu repositório e selecione `app.py`
4. Em **"Secrets"**, adicione:
   ```toml
   HF_TOKEN = "hf_seu_token_aqui"
   ```
5. No `app.py`, substitua a linha do `text_input` por:
   ```python
   hf_token = st.secrets.get("HF_TOKEN", "")
   ```

---

## 🤖 Modelo usado

| Propriedade | Valor |
|-------------|-------|
| Modelo | Qwen/Qwen2.5-1.5B-Instruct |
| Parâmetros | 1.5 bilhões |
| Custo | Gratuito (HF Inference API) |
| Idioma | Português / Multilíngue |
| Limite gratuito | ~1.000 req/dia |

---

## ✏️ Personalizar o tema do chatbot

No arquivo `app.py`, edite a variável `SYSTEM_PROMPT` para adaptar o chatbot ao seu contexto:

```python
SYSTEM_PROMPT = """Você é o UniBot, assistente de...
Responda sobre:
- Tópico 1
- Tópico 2
..."""
```

---

## 📌 Tecnologias

- [Streamlit](https://streamlit.io) — Interface web
- [HuggingFace Hub](https://huggingface.co) — API de inferência gratuita
- [Qwen2.5](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) — Modelo de linguagem
