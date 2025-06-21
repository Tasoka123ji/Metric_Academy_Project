# app.py
import streamlit as st

st.set_page_config(page_title="Hi My Metric Team", page_icon="📊")

st.title("📣 Hi My Metric Team!")
st.subheader("We can start together 🚀")

name = st.text_input("👋 What's your name?")
if name:
    st.success(f"Welcome aboard, {name}! Let's build something amazing together!")

st.markdown("---")
st.markdown("### 🔧 Technologies we can use:")
st.markdown("- Streamlit for the frontend")
st.markdown("- Python for the logic")
st.markdown("- Render for deployment")
st.markdown("- Docker if needed")
st.balloons()

