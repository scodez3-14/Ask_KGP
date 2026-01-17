import streamlit as st
from Get_ans import ask_kgp_with_rerun
from pathlib import Path


# 1. Page Config & Theme
st.set_page_config(page_title="MetaKGP AI", page_icon="🎓", layout="centered")

# Custom CSS for a "Glassmorphism" effect on source cards
st.markdown("""
    <style>
    .source-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Branding
with st.sidebar:
    st.title("🎓 MetaKGP AI")
    st.markdown("---")
    st.markdown("### About")
    st.caption("Access the collective knowledge of IIT Kharagpur's student-run wiki.")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. Message History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm the MetaKGP assistant. Ask me anything about KGP societies, halls, or traditions."}
    ]

# 4. Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there are sources attached to the history item, show them
        if "sources" in message and message["sources"]:
            with st.expander("📚 Reference Sources"):
                for src in message["sources"]:
                    st.markdown(f"**{src['title']}**")
                    st.caption(src['text'])
                    st.divider()

# 5. Chat Input Logic
if prompt := st.chat_input("Ask about Spring Fest, KGPian lingo, or societies..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Response Generation
    with st.chat_message("assistant"):
        # Interactive status indicator
        with st.status("🧠 Consulting MetaKGP Wiki...", expanded=False) as status:
            answer, audit, chunks = ask_kgp_with_rerun(prompt)
            status.update(label="Information retrieved!", state="complete")

        # Handling Hallucinations
        if audit.get('status') == "HALLUCINATED":
            st.error("⚠️ Note: The information below might not be fully accurate based on current records.")
        
        # Display Answer
        st.markdown(answer)

        if chunks:
            st.markdown("---")
            st.markdown("#### 📖 Sources Found")
            cols = st.columns(len(chunks) if len(chunks) <= 3 else 3)
            for idx, chunk in enumerate(chunks):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"**{chunk['title']}**")
                        # Truncated snippet for UI cleanliness
                        st.caption(f"{chunk['text'][:120]}...")
                        st.link_button("View Wiki", chunk['source'], icon="🔗")

    # Save to history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer, 
        "sources": chunks
    })