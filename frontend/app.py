import streamlit as st
import requests

st.set_page_config(page_title="MetaKGP AI", layout="centered")
st.title("🎓 MetaKGP AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask about IIT Kharagpur..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the Backend API
    try:
        response = requests.post("http://127.0.0.1:8000/ask", json={"text": prompt})
        data = response.json()
        
        reply = data["answer"]
        if data["sources"]:
            reply += f"\n\n**Sources:** {', '.join(data['sources'])}"

        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error("Make sure your backend is running! (uvicorn main:app)")