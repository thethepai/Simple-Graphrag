import streamlit as st
import pandas as pd
 
st.write("""
# Streamlit Example
Hello *world!*
""")
 
df = pd.read_csv("./data/table_csv/信安2102.csv")
st.line_chart(df)