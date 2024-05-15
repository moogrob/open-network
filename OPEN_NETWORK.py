import streamlit as st

st.set_page_config(page_title="Open Network")
st.header('Welcome to Open Network')
st.sidebar.selectbox('Select DNN',options=['DNN1','DNN2','DNN3'],index=0)