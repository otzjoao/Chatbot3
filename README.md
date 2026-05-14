# 🎓 UniBot — FAQ Acadêmico · Unigran Capital

Chatbot de FAQ acadêmico para a Unigran Capital, usando o modelo **Llama-3.1-8B-Instruct** (gratuito via HuggingFace Inference API) e interface em **Streamlit**.

---

## 📁 Estrutura do projeto

```
├── app.py                      # Aplicação principal
├── faq_data.json               # Perguntas e respostas do FAQ (editável sem código)
├── requirements.txt            # Dependências Python
├── prompts/
│   └── system_prompt.md        # Prompt do bot (editável sem código)
├── styles/
│   └── main.css                # Estilos da interface
└── templates/
    ├── header.html             # Cabeçalho da página
    ├── message_user.html       # Balão de mensagem do usuário
    ├── message_bot.html        # Balão de mensagem do bot
    ├── typing.html             # Indicador de digitando...
    └── suggestions.html        # Chips de sugestão iniciais
```

---

## 🚀 Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/otzjoao/Chatbot3.git
cd Chatbot3
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

#adiciona a venv no .gitignore

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
3. Escolha tipo **"Read"**
4. Copie o token gerado (começa com `hf_...`)

### 5. Execute o app

```bash
streamlit run app.py
```

O browser abrirá automaticamente em `http://localhost:8501`.  
Cole seu token no campo **🔑 Token HuggingFace** na barra lateral.

---

## 🌐 Deploy gratuito no Streamlit Cloud

1. Acesse https://share.streamlit.io e conecte seu repositório GitHub
2. Selecione `app.py` como arquivo principal
3. Em **"Secrets"**, adicione:
   ```toml
   HF_TOKEN = "hf_seu_token_aqui"
   ```
4. Clique em **Deploy** — o token será lido automaticamente pelo app

---

## ✏️ Como personalizar sem mexer no código

### Adicionar ou editar perguntas do FAQ → `faq_data.json`

Cada entrada segue este formato:

```json
{
  "palavras_chave": ["biblioteca", "livro", "empréstimo"],
  "resposta": "📚 **Biblioteca**\n\nHorário: 7h–22h..."
}
```

- **`palavras_chave`:** termos que ativam a resposta (acentos e maiúsculas são ignorados automaticamente)
- **`resposta`:** texto exibido, suporta Markdown (`**negrito**`, `- listas`, tabelas)

O arquivo pode ser editado diretamente pelo GitHub (clique no arquivo → ✏️ editar → salvar), sem precisar de editor de código.

### Alterar o comportamento do bot → `prompts/system_prompt.md`

Edite o texto para mudar o contexto, tom ou lista de assuntos que o bot responde.

### Alterar a aparência → `styles/main.css`

Edite cores, fontes e espaçamentos sem tocar no Python.

---

## 🤖 Modelo usado

| Propriedade | Valor |
|-------------|-------|
| Modelo | meta-llama/Llama-3.1-8B-Instruct |
| Parâmetros | 8 bilhões |
| Custo | Gratuito (HF Inference API) |
| Idioma | Português / Multilíngue |

---

## 🛡️ Segurança

- Input do usuário é sanitizado com `html.escape()` antes de ser renderizado, prevenindo HTML injection
- O token HuggingFace nunca é exposto no código — use sempre `st.secrets` no deploy

---

## 📌 Tecnologias

- [Streamlit](https://streamlit.io) — Interface web
- [HuggingFace Hub](https://huggingface.co) — API de inferência gratuita
- [Llama 3.1](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) — Modelo de linguagem
