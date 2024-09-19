import streamlit as st
import os

st.set_page_config(page_title="Indexing", page_icon="📊")

st.markdown("# Indexing Configuration")
st.sidebar.header("Indexing Configuration")
st.write(
    """Here you can configure the settings for the indexing."""
)

save_folder = "uploaded_files"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

uploaded_files = st.file_uploader(
    "Choose a txt or xlsx file", accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)
    
    with open(os.path.join(save_folder, uploaded_file.name), "wb") as f:
        f.write(bytes_data)
    st.write(f"File saved to {os.path.join(save_folder, uploaded_file.name)}")


def start_index():
    pass

def prompt_tune():
    pass

if st.sidebar.button("Start Indexing"):
    start_index()

if st.sidebar.button("Prompt Tune"):
    prompt_tune()