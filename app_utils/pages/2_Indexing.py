import streamlit as st
import os
from api_utils.rag_client_init import InitPipeline
from api_utils.default_config import DATA_INPUT_DIR, DATA_INDEX_DIR

st.set_page_config(page_title="Indexing", page_icon="📊")

st.markdown("# Indexing Configuration")
st.sidebar.header("Indexing Configuration")
st.write("""Here you can choose files and do the indexing.""")

pipeline = InitPipeline()

save_folder = f"{DATA_INPUT_DIR}"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

ragtest_input = f"{DATA_INDEX_DIR}"

@st.cache_data
def get_files(uploaded_files):
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)

        with open(os.path.join(save_folder, uploaded_file.name), "wb") as f:
            f.write(bytes_data)
        st.success(f"File saved to {os.path.join(save_folder, uploaded_file.name)}")

        with open(os.path.join(ragtest_input, uploaded_file.name), "wb") as f:
            f.write(bytes_data)
        st.success(f"File saved to {os.path.join(ragtest_input, uploaded_file.name)}")


if not os.path.exists(f"{pipeline.root_dir}"):
    st.markdown("## Do the index init first and then use indexing")
else:
    uploaded_files = st.file_uploader(
        "Choose a txt or xlsx file", accept_multiple_files=True
    )
    
    get_files(uploaded_files)


if st.sidebar.button("Start Indexing"):
    if os.listdir(DATA_INDEX_DIR):
        pipeline.default_start_index()
    else:
        st.sidebar.error("Please upload files first")

if st.sidebar.button("Prompt Tune"):
    if os.listdir(DATA_INDEX_DIR):
        pipeline.default_prompt_tune()
    else:
        st.sidebar.error("Please upload files first")
