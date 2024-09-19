import streamlit as st
from api_utils.rag_client_init import InitPipeline
import asyncio
import pandas as pd

st.set_page_config(page_title="Chat Demo", page_icon="📱")

st.markdown("# Chat Demo")
st.sidebar.header("Chat Demo")
st.write("""a test for the chat demo""")

global_engine, local_engine = InitPipeline.get_query_engines()

# 在侧边栏添加选择框
engine_option = st.sidebar.selectbox(
    "Select Engine",
    ("Global Engine", "Local Engine")
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 根据选择的引擎进行搜索
    if engine_option == "Global Engine":
        search_result = asyncio.run(global_engine.search(prompt))
    else:
        search_result = asyncio.run(local_engine.search(prompt))

    # 显示搜索结果
    with st.chat_message("assistant"):
        st.markdown("**Search Result:**")
        print(search_result.response)
        st.markdown(search_result.response)

    # 将搜索结果添加到会话状态中
    st.session_state.messages.append({"role": "assistant", "content": search_result.response})
    
    # Display result information on the dashboard using layout on the right side
    with st.expander("Search Result Details", expanded=True):
        st.markdown("### Search Result Details")
    
        st.markdown("**Reports:**")
        reports = search_result.context_data.get("reports", "No reports available")
        st.dataframe(reports if isinstance(reports, pd.DataFrame) else pd.DataFrame([reports]))
    
        st.markdown("**Entities:**")
        entities = search_result.context_data.get("entities", "No entities available")
        st.dataframe(entities if isinstance(entities, pd.DataFrame) else pd.DataFrame([entities]))
    
        st.markdown("**Relationships:**")
        relationships = search_result.context_data.get("relationships", "No relationships available")
        st.dataframe(relationships if isinstance(relationships, pd.DataFrame) else pd.DataFrame([relationships]))
    
        st.markdown("**Sources:**")
        sources = search_result.context_data.get("sources", "No sources available")
        st.dataframe(sources if isinstance(sources, pd.DataFrame) else pd.DataFrame([sources]))
    
        if "claims" in search_result.context_data:
            st.markdown("**Claims:**")
            claims = search_result.context_data.get("claims", "No claims available")
            st.dataframe(claims if isinstance(claims, pd.DataFrame) else pd.DataFrame([claims]))
    
        st.markdown(f"**LLM calls:** {search_result.llm_calls}")
        st.markdown(f"**LLM tokens:** {search_result.prompt_tokens}")