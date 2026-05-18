import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


if "messages" not in st.session_state:
    st.session_state.messages = []


def test_prompt(messages):
    """Send all chat messages to the LLM and return its response"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        return f"❌ Error: {str(e)}"


def log_result(messages, response):
    """Save chat results in a log file with timestamp"""
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60)
        f.write(f"\n🕒 {datetime.now()}")
        for msg in messages:
            f.write(f"\n{msg['role'].upper()}: {msg['content']}")
        f.write(f"\nAI RESPONSE: {response}\n")


st.set_page_config(page_title="Prompt Tester by Riti", page_icon="💬", layout="centered")

st.title("💬 Riti - Prompt Testing Chat")
st.markdown("A simple **prompt testing dashboard** with conversational memory and logging.")


with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Make sure your `.env` file contains a valid `OPENAI_API_KEY`.")
    st.write("Each conversation is saved to `logs.txt` automatically.")


if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = ""

st.subheader("🧠 System Prompt")
st.session_state.system_prompt = st.text_area(
    "Define the AI's role or behavior:",
    st.session_state.system_prompt or "You are a helpful assistant.",
    height=100
)


st.subheader("💭 Conversation")
chat_container = st.container()


with chat_container:
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"👤 **You:** {msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"🤖 **AI:** {msg['content']}")
    else:
        st.info("Start the conversation below!")

user_input = st.text_area("✍️ Enter your next prompt:", placeholder="Type your message here...", height=100)


if st.button("🚀 Send"):
    if not user_input.strip():
        st.warning("⚠️ Please enter a message before sending.")
    else:
        
        if not any(m["role"] == "system" for m in st.session_state.messages):
            st.session_state.messages.insert(0, {"role": "system", "content": st.session_state.system_prompt})

       
        st.session_state.messages.append({"role": "user", "content": user_input})

        
        with st.spinner("Generating response..."):
            response = test_prompt(st.session_state.messages)

        
        st.session_state.messages.append({"role": "assistant", "content": response})

        log_result(st.session_state.messages, response)

       
        st.rerun()


if st.button("🧹 Clear Conversation"):
    st.session_state.messages = []
    st.session_state.system_prompt = ""
    st.success("Conversation cleared!")


if st.checkbox("📜 Show Log File"):
    try:
        with open("logs.txt", "r", encoding="utf-8") as f:
            logs = f.read()
        st.text_area("Log Output", logs, height=300)
    except FileNotFoundError:
        st.info("No logs found yet. Run a conversation first.")
