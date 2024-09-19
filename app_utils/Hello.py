import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Simple-Graphrag! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    # simple-graphrag

    The `simple-graphrag` project is a user-friendly interface for the `graphrag` engine. It provides a range of features to facilitate the management and configuration of graph databases. Key functionalities include:

    ## Features

    - **API Service Calls**: Easily interact with the `graphrag` engine through a comprehensive set of API endpoints.
    - **Graphical Configuration**: Configure your graph databases using an intuitive graphical interface.
    - **Database Management**: Connect to and manage multiple databases seamlessly.

    ## Getting Started

    To get started with `simple-graphrag`, follow these steps:

    1. **Installation**: Install the necessary dependencies and set up the environment.
    2. **Configuration**: Configure the connection settings for your databases.
    3. **Usage**: Start using the graphical interface to manage your graph databases and make API calls.
    """
)