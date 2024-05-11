import streamlit as st
import os
import google.generativeai as genai
import hashlib
import tempfile



# Configurações do modelo Gemini
GOOGLE_API_KEY = "SUA_API_KEY"  # Substitua pela sua API Key
genai.configure(api_key=GOOGLE_API_KEY)

# Configurações de geração e segurança
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Inicia o chat
chat = model.start_chat()


# Função para exibir a Home Page
def home_page():
    st.title("👩🏽‍ Olá! Sou a Chris do RH")
    st.write(
        "Sou uma especialista de recursos humanos, responderei às perguntas sobre carreira, currículos, processos de seleção e normas de triagem de currículos, como o ATS (Applicant Tracking System)."
    )


# Função para exibir a página do Chatbot
def chatbot_page():
    st.title("👩🏽‍ Chat Bot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.empty()

    # Exibe o histórico da conversa no container
    with chat_container.container():
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    if message["type"] == "text":
                        st.markdown(message["content"])
                    else:  # Imagem
                        st.image(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])

    uploaded_file = st.file_uploader(
        "Carregue seu currículo (imagem)", type=["png", "jpg", "jpeg"]
    )
    user_input = st.chat_input("Digite sua mensagem ou carregue seu currículo:")

    if uploaded_file:
        # Crie um nome de arquivo único
        temp_file_name = os.path.join(tempfile.gettempdir(), f"{hashlib.md5(uploaded_file.name.encode()).hexdigest()}.jpg")
    
        # Salve a imagem no arquivo temporário
        with open(temp_file_name, "wb") as temp_file:
            temp_file.write(uploaded_file.read())
    
        # Envie a imagem para o Gemini
        message = genai.upload_file(temp_file_name, mime_type=uploaded_file.type)
        chat.send_message(message)
    
        # Remova o arquivo temporário
        os.remove(temp_file_name)

        st.session_state.messages.append(
            {"role": "user", "content": uploaded_file, "type": "image"}
        )
    elif user_input:
        chat.send_message(user_input)
        st.session_state.messages.append(
            {"role": "user", "content": user_input, "type": "text"}
        )

    # Verifica se o Gemini retornou uma resposta
    if chat.last is not None:
        response = chat.last.text
        st.session_state.messages.append({"role": "assistant", "content": response, "type": "text"})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Olá! Como posso te ajudar hoje?", "type": "text"})

    # Atualiza o container com as mensagens apenas uma vez
    with chat_container.container():
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    if message["type"] == "text":
                        st.markdown(message["content"])
                    else:
                        st.image(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])


# Cria um menu lateral
page = st.sidebar.selectbox("Navegação", ["Home Page", "Chat Bot"])

# Exibe a página selecionada
if page == "Home Page":
    home_page()
else:
    chatbot_page()