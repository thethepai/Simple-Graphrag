import streamlit as st
import os
from api_utils.rag_client_init import InitPipeline
import asyncio
import pandas as pd

st.set_page_config(page_title="Chat Demo", page_icon="📱")

st.markdown("# Chat Demo")
st.sidebar.header("Chat Demo Configuration")
st.write("""start a conversation with the assistant""")

pipeline = InitPipeline()

if not os.path.exists(f"{pipeline.root_dir}/output"):
    st.markdown("## Do the index init and index process first and then use chat demo")
else:
    col1, col2 = st.columns([2, 1])

    global_engine, local_engine = pipeline.get_query_engines()

    engine_option = st.sidebar.selectbox(
        "Select Engine", ("Global Engine", "Local Engine")
    )

    with st.expander("Global Search Engine Init Message"):
        """
        # output
        print(f"Total report count: {len(self.report_df)}")
        print(f"Report count after filtering by community level {
            request.community_level}: {len(reports)}")
        self.report_df.head()
        """
        st.markdown("### Total Report")
        st.write(f"Total report count: {len(global_engine.report_df)}")
        st.write(
            f"Report count after filtering by community level: {len(global_engine.reports)}"
        )
        st.dataframe(global_engine.report_df.head())

    with st.expander("Local Search Engine Init Message"):

        # print(f"Entity count: {len(self.entity_df)}")
        # self.entity_df.head()

        st.markdown("### Entity Count")
        st.write(f"Entity Count: {len(local_engine.entity_df)}")
        st.dataframe(local_engine.entity_df.head())

        # print(f"Relationship count: {len(self.relationship_df)}")
        # self.relationship_df.head()

        st.markdown("### Relationship Count")
        st.write(f"Relationship Count: {len(local_engine.relationship_df)}")
        st.dataframe(local_engine.relationship_df.head())

        # print(f"Claim records: {len(self.claims)}")

        st.markdown("### Claim Records")
        st.write(f"Claim Records: {len(local_engine.claims)}")

        # print(f"Report records: {len(self.report_df)}")
        # self.report_df.head()

        st.markdown("### Report Records")
        st.write(f"Report Records: {len(local_engine.report_df)}")
        st.dataframe(local_engine.report_df.head())

        # print(f"Text unit records: {len(self.text_unit_df)}")
        # self.text_unit_df.head()

        st.markdown("### Text Unit Records")
        st.write(f"Text Unit Records: {len(local_engine.text_unit_df)}")
        st.dataframe(local_engine.text_unit_df.head())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask question about entities and relationships"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if engine_option == "Global Engine":
            search_result = asyncio.run(global_engine.search(prompt))
        else:
            search_result = asyncio.run(local_engine.search(prompt))

        with st.chat_message("assistant"):
            st.markdown("**Search Result:**")
            print(search_result.response)
            st.markdown(search_result.response)

        st.session_state.messages.append(
            {"role": "assistant", "content": search_result.response}
        )

        with st.expander("Search Result Details", expanded=True):
            st.markdown("### Search Result Details")

            st.markdown("**Reports:**")
            reports = search_result.context_data.get("reports", "No reports available")
            st.dataframe(
                reports
                if isinstance(reports, pd.DataFrame)
                else pd.DataFrame([reports])
            )

            st.markdown("**Entities:**")
            entities = search_result.context_data.get(
                "entities", "No entities available"
            )
            st.dataframe(
                entities
                if isinstance(entities, pd.DataFrame)
                else pd.DataFrame([entities])
            )

            st.markdown("**Relationships:**")
            relationships = search_result.context_data.get(
                "relationships", "No relationships available"
            )
            st.dataframe(
                relationships
                if isinstance(relationships, pd.DataFrame)
                else pd.DataFrame([relationships])
            )

            st.markdown("**Sources:**")
            sources = search_result.context_data.get("sources", "No sources available")
            st.dataframe(
                sources
                if isinstance(sources, pd.DataFrame)
                else pd.DataFrame([sources])
            )

            if "claims" in search_result.context_data:
                st.markdown("**Claims:**")
                claims = search_result.context_data.get("claims", "No claims available")
                st.dataframe(
                    claims
                    if isinstance(claims, pd.DataFrame)
                    else pd.DataFrame([claims])
                )

            st.markdown(f"**LLM calls:** {search_result.llm_calls}")
            st.markdown(f"**LLM tokens:** {search_result.prompt_tokens}")
