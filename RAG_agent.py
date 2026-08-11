import streamlit as st

from openai import OpenAI

st.set_page_config(page_title="ThinkRook Chatbot", page_icon="🚀", layout = "centered")

st.logo("https://dme2wmiz2suov.cloudfront.net/Institution(8663)/Logo/4216689-ThinkRook_Logo.png", size="large")

st.title("🤖 ThinkRook Chatbot")
st.subheader("Your smart Agent for fast and reliable answers.")

st.logo("https://dme2wmiz2suov.cloudfront.net/Institution(8663)/Logo/4216689-ThinkRook_Logo.png", size="large")
st.sidebar.title("Bot Settings")


with st.sidebar:

    model_name = st.selectbox(
        "Select Your Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        key="groq_model"
    )
    groq_api_key = st.text_input("Groq API Key", key="groq_api_key", type="password")


st.title("📝 File Q&A with ThinkRook")
st.caption("Chat with your uploaded article or file.")

uploaded_file = st.file_uploader("Upload your article/file here.", type=("txt", "md"))


if not groq_api_key:
    st.info("Please add your Groq API key to continue.")
    st.stop()

client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

# Initializing the session state for chat
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.article_text = ""

# If a new file is uploaded, read and store the article/file
if uploaded_file:
    article = uploaded_file.read().decode()
    st.session_state.article_text = article

    if not any(msg["role"]=="assistant" for msg in st.session_state.messages):
        st.session_state.messages.append({
            "role": "assistant",
            "content": "File Uploaded! You can now ask me questions about it."
        })

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask me something about the article/file."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if st.session_state.article_text:
        chat_prompt = f"""
                        You are an AI Agent helping summarize and explain and article/file.
                        Here is your article or file.
                        <article>{st.session_state.article_text}</article>
                        Now my question is: {prompt}
                        """

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": chat_prompt}],
        )
        answer = response.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)

    else:
        st.error("Please upload a file or article first.")
