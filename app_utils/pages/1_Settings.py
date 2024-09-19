import streamlit as st
from api_utils.rag_client_init import InitPipeline

st.set_page_config(page_title="Settings", page_icon="📈")

st.markdown("# Settings Page")
st.sidebar.header("Settings Page")
st.write(
    """Here you can configure the settings for the application."""
)

# Initialize configuration engines
yaml_manager, user_dotenv_manager, config_operator = InitPipeline.get_config_engines()

# Read configuration from file
user_config = user_dotenv_manager.read_env()

# Define input fields with default values from the configuration
graphrag_api_key = st.text_input("GRAPHRAG_API_KEY", user_config.get("GRAPHRAG_API_KEY", "default_key"))
api_base = st.text_input("API_BASE", user_config.get("API_BASE", "https://open.bigmodel.cn/api/paas/v4/"))
model_id = st.text_input("MODEL_ID", user_config.get("MODEL_ID", "glm-4"))
embedding_model_id = st.text_input("EMBEDDING_MODEL_ID", user_config.get("EMBEDDING_MODEL_ID", "embedding-3"))
claim_extraction = st.toggle("CLAIM_EXTRACTION", value=user_config.get("CLAIM_EXTRACTION", "True"))

# Define a function to update the configuration
def update_config():
    user_config["GRAPHRAG_API_KEY"] = graphrag_api_key
    user_config["API_BASE"] = api_base
    user_config["MODEL_ID"] = model_id
    user_config["EMBEDDING_MODEL_ID"] = embedding_model_id
    user_config["CLAIM_EXTRACTION"] = claim_extraction
    user_dotenv_manager.write_env(user_config)
    st.success("Configuration updated successfully!")

# Define a function to reload the configuration
def reload_config():
    user_config = user_dotenv_manager.read_env()
    st.experimental_rerun()

# Add buttons for submitting and reading configuration
if st.button("Submit"):
    update_config()

if st.button("Read Configuration"):
    reload_config()

"""
Initializing configuration with user_config_path: .env, env_config_path: ./ragtest/.env, yaml_config_path: ./ragtest/settings.yaml
2024-09-20 00:44:25.186 Uncaught app exception
Traceback (most recent call last):
  File "E:\documents\vscode-project\Simple-Graphrag\.venv\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 88, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "E:\documents\vscode-project\Simple-Graphrag\.venv\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 590, in code_to_exec
    exec(code, module.__dict__)
  File "E:\documents\vscode-project\Simple-Graphrag\app_utils\pages\1_Settings.py", line 42, in <module>
    update_config()
  File "E:\documents\vscode-project\Simple-Graphrag\app_utils\pages\1_Settings.py", line 32, in update_config
    user_dotenv_manager.write_env(user_config)
  File "E:\documents\vscode-project\Simple-Graphrag\api_utils\config.py", line 25, in write_env
    set_key(self.dotenv_path, key, value)
  File "E:\documents\vscode-project\Simple-Graphrag\.venv\Lib\site-packages\dotenv\main.py", line 175, in set_key
    value_out = "'{}'".format(value_to_set.replace("'", "\\'"))
                              ^^^^^^^^^^^^^^^^^^^^
AttributeError: 'bool' object has no attribute 'replace'
"""