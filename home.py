import os
import streamlit as st
import requests
import json

from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from openai import OpenAI


st.set_page_config(page_title="PaperTranslator", page_icon="📜")

st.title("Paper Translator")


class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)


mathpix_url = "https://api.mathpix.com/v3/pdf"


# Prepare API
try:
    headers = {
        "app_id": os.environ["mathpix_app_id"],
        "app_key": os.environ["mathpix_app_key"],
    }
    response = requests.post(mathpix_url, headers=headers)
    if not response.status_code == 200:
        raise Exception
    # st.write(response.status_code)

except Exception as ex:
    with st.sidebar:
        st.write("Please input Mathpix app id and app key")
        with st.form("Mathpix API"):
            app_id = st.text_input("Please input mathpix app ID")
            app_key = st.text_input("Please input mathpix app KEY", type="password")
            submitted = st.form_submit_button("Submit")
            if submitted:
                os.environ["mathpix_app_id"] = app_id
                os.environ["mathpix_app_key"] = app_key
                st.rerun()

try:
    client = OpenAI()
    client.models.list()
except Exception as ex:
    with st.sidebar:
        st.write("Please input OpenAI API key")
        with st.form("OpenAI API"):
            openai_key = st.text_input("Please input OpenAi app key", type="password")
            submitted = st.form_submit_button("Submit")
            if submitted:
                os.environ["OPENAI_API_KEY"] = openai_key
                st.rerun()

try:
    llm = ChatOpenAI(
        temperature=0.1,
        streaming=True,
        callbacks=[
            ChatCallbackHandler(),
        ],
    )
except Exception as ex:
    st.write("Can't prepare LLM, Please check api key or network")


st.markdown("## Step 1. File upload")
file = st.file_uploader("Upload a pdf file which you want to translate", type=["pdf"])

if file:
    button = st.button(label="Make markdown")

# st.markdown("## Step 2. File upload")
