import streamlit as st
import os
from api_utils.rag_client_init import InitPipeline

st.set_page_config(page_title="Settings", page_icon="📈")

st.markdown("# Settings Page")
st.sidebar.header("Settings Page")
st.write(
    """Here you can configure the settings for the application. You don't need to add ' ' to the input fields."""
)

# Initialize configuration engines
pipeline = InitPipeline()

if not os.path.exists(f"{pipeline.root_dir}"):
    st.markdown("## Do the index init first and then configure the settings")
else:
    st.markdown(f"**{pipeline.root_dir} exists, it will be the root configuration directory**")
    yaml_manager, user_dotenv_manager, config_operator = pipeline.get_config_engines()

    user_config = user_dotenv_manager.read_env()

    graphrag_api_key = st.text_input(
        "GRAPHRAG_API_KEY", user_config.get("GRAPHRAG_API_KEY", "default_key")
    ).strip("'")
    api_base = st.text_input(
        "API_BASE", user_config.get("API_BASE", "https://open.bigmodel.cn/api/paas/v4/")
    ).strip("'")
    model_id = st.text_input("MODEL_ID", user_config.get("MODEL_ID", "glm-4")).strip("'")
    embedding_model_id = st.text_input(
        "EMBEDDING_MODEL_ID", user_config.get("EMBEDDING_MODEL_ID", "embedding-3")
    ).strip("'")
    claim_extraction = st.toggle(
        "CLAIM_EXTRACTION",
        value=user_config.get("CLAIM_EXTRACTION", "True").strip("'\"") == "True",
    )


def update_config():
    user_config = {
        "GRAPHRAG_API_KEY": graphrag_api_key.strip("'\""),
        "API_BASE": api_base.strip("'\""),
        "MODEL_ID": model_id.strip("'\""),
        "EMBEDDING_MODEL_ID": embedding_model_id.strip("'\""),
        "CLAIM_EXTRACTION": (str(claim_extraction)).strip("'\""),
    }
    print(user_config)
    user_dotenv_manager.write_env(user_config)
    config_operator.initialize_config()
    st.success("Configuration updated successfully!")


st.sidebar.markdown("## Index Init")
st.sidebar.write("you should init index first before config")

if st.sidebar.button("init index"):
    if not os.path.exists(f"{pipeline.root_dir}"):
        pipeline.default_init()
        st.rerun()
    else:
        st.sidebar.warning(f"{pipeline.root_dir} exists, have you done the indexing already?")
    

st.sidebar.markdown("## Configuration Details")
st.sidebar.write("you submit the configuration here")

if st.sidebar.button("Submit"):
    update_config()

if st.sidebar.button("Refresh"):
    st.rerun()
