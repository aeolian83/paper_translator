import os
import time
import streamlit as st
import requests
import json

from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.few_shot import (
    FewShotPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

# from langchain.callbacks import StreamingStdOutCallbackHandler
from openai import OpenAI
import tiktoken

import mathpix_f as mf
import openai_f as of
import convert_f as cf


st.set_page_config(page_title="PaperTranslator", page_icon="📜")

st.title("Paper Translator")

markdown_folder_path = "./markdown"
translated_markdown_folder_path = "./markdown/translated"
html_folder_path = "./html"
pdf_folder_path = "./pdf"

if not os.path.exists(markdown_folder_path):
    os.makedirs(markdown_folder_path)
if not os.path.exists(translated_markdown_folder_path):
    os.makedirs(translated_markdown_folder_path)
if not os.path.exists(html_folder_path):
    os.makedirs(html_folder_path)
if not os.path.exists(pdf_folder_path):
    os.makedirs(pdf_folder_path)

try:
    check = st.session_state["markdowns"]
    del check
except:
    st.session_state["markdowns"] = {}
finally:
    markdown_files = [
        file
        for file in os.listdir(markdown_folder_path)
        if os.path.isfile(os.path.join(markdown_folder_path, file))
    ]
    for file in markdown_files:
        with open(os.path.join(markdown_folder_path, file), "r", encoding="utf-8") as f:
            temp_text = f.read()
            st.session_state["markdowns"][os.path.splitext(file)[0]] = temp_text

try:
    check = st.session_state["translated_markdowns"]
    del check
except:
    st.session_state["translated_markdowns"] = {}
finally:
    translated_markdown_files = [
        file
        for file in os.listdir(translated_markdown_folder_path)
        if os.path.isfile(os.path.join(translated_markdown_folder_path, file))
    ]
    for file in translated_markdown_files:
        with open(
            os.path.join(translated_markdown_folder_path, file), "r", encoding="utf-8"
        ) as f:
            temp_text = f.read()
            st.session_state["translated_markdowns"][
                os.path.splitext(file)[0]
            ] = temp_text

try:
    check = st.session_state["htmls"]
    del check
except:
    st.session_state["htmls"] = {}

mathpix_url = mf.mathpix_url


def save_markdown(path, filename, text):
    with open(os.path.join(path, filename + ".md"), "w") as file:
        for line in text:
            file.write(line)


@st.cache_data(show_spinner="making chunk group")
def make_chunk_group(text):
    chunks, ntokens = of.make_chunks(text)
    chunk_group = of.group_chunks(chunks, ntokens)
    return chunk_group


class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message = ""
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        pass

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)


examples = of.examples

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{original}"),
        ("ai", "{translate}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt, examples=examples
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You will translate English academic papers in the field of {paper_field}, which are written in Markdown, section by section into Korean.

Condition 1: Translate the {paper_field} academic papers into an easy-to-understand style.
Condition 2: For specialized terms related to the field, translate them in the format of Korean(English).
Condition 3: Do not create any other responses, only generate the translation.
Condition 4: Please Leave all Markdown or LaTeX commands unchanged.
Condition 5: Translate quotations, examples, etc., enclosed in double quotes (“”), in the format of Korean(English).
""",
        ),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)

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
st.markdown("## Step 0. Select Model")
model = st.selectbox("Select GPT Model", ("gpt-4-turbo", "gpt-3.5-turbo-0125"))
try:
    llm = ChatOpenAI(
        model=model,
        temperature=0.01,
        streaming=True,
        callbacks=[
            ChatCallbackHandler(),
        ],
    )
except Exception as ex:
    st.write("Can't prepare LLM, Please check api key or network")

# Upload a PDF and convert it to markdown through OCR
st.markdown("## Step 1. File upload")
file = st.file_uploader("Upload a pdf file which you want to translate", type=["pdf"])
st.divider()

# Conver PDF to Markdown through OCR
st.markdown("## Step 2. Conver PDF to Markdown through OCR")
if file:
    mark_button = st.button(label="Make markdown")

    if mark_button:
        with st.status("OCR is working", expanded=False) as status:
            holder = "Done"
            start_time = time.time()
            api_response = mf.call_mathpix_api(file, headers)
            pdf_id = mf.get_id(api_response)
            while True:
                if start_time - time.time() > 150:
                    holder = "not done"
                    break
                ocr_status = mf.check_status(pdf_id, headers)
                st.write(ocr_status)
                if ocr_status == "completed":
                    break
                time.sleep(2)

            result_markdown = mf.get_result(pdf_id, headers)
            st.session_state["markdowns"][file.name[:-4]] = result_markdown.text
            if holder == "Done":
                status.update(label="OCR done!")
                save_markdown(
                    markdown_folder_path, file.name[:-4], result_markdown.text
                )
            else:
                status.update(label="OCR Error! Please check Mathpix")
else:
    st.write("Please Upload PDF file")
st.divider()


st.markdown("## Step 3. Choose Markdown and Download")
# 무슨 이유에서 인지 st.session_state["markdowns"].key()가 작동하지 않아 직접 이터레이션을 돌렸다.


markdown_list = [key for key in st.session_state["markdowns"]]
markdown_option = st.selectbox("choose", options=markdown_list)

if markdown_option:
    markdown_text = st.session_state["markdowns"][markdown_option]
    with st.container(height=400):
        st.markdown(markdown_text)
    st.download_button(
        label="Download Markdown",
        data=markdown_text,
        file_name=markdown_option + ".md",
        mime="text/csv",
    )

else:
    st.write("Please choose Markdown")
st.divider()

# with st.container(height=400):
#     st.markdown(final_prompt.format(paper_field="ai", input=markdown_text))
st.markdown("## Step 4. Translate with LLM(GPT-4)")
try:
    chunk_group = make_chunk_group(markdown_text)
except:
    pass

chain = final_prompt | llm

translate_button = st.button(label="Translate")


# st.write(markdown_text[1])

if translate_button:
    translated_text = []
    with st.container(height=400):
        for chunk in chunk_group:
            response = chain.invoke({"paper_field": "AI", "input": chunk})
            translated_text.append(response.content + "\n\n")
    save_markdown(
        translated_markdown_folder_path,
        "translated_" + markdown_option,
        translated_text,
    )
    with open(
        os.path.join(
            translated_markdown_folder_path, "translated_" + markdown_option + ".md"
        ),
        "r",
    ) as file:
        transtated_contents = file.read()
        st.session_state["translated_markdowns"][
            "translated_" + markdown_option
        ] = transtated_contents
st.divider()

st.markdown("## Step 5. Check the translated Markdown")
translated_markdown_list = [key for key in st.session_state["translated_markdowns"]]
translated_markdown_option = st.selectbox(
    "choose_translate", options=translated_markdown_list
)

if translated_markdown_option:
    translated_markdown_text = st.session_state["translated_markdowns"][
        translated_markdown_option
    ]
    with st.container(height=400):
        st.markdown(translated_markdown_text)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Translated Markdown",
            data=translated_markdown_text,
            file_name=translated_markdown_option + ".md",
            mime="text/csv",
        )
    # with col2:
    #     st.button(label="B")
    #     st.button(label="C")

else:
    st.write("Please choose Markdown")
st.divider()


st.markdown("## Step 6. Conert Markdown to you want, And Download")
convert_headers = headers.copy()
convert_headers["Content-Type"] = "application/json"

# html변환버튼을 위로 놓고 그 아래에 3개의 컬럼을 배치해서 일관성 있게 만들필요 있다.
# try except문과 if와 raise error 등을 적극 이용할 필요
convert_button = st.button(label="Convert to Html")
if convert_button:
    with st.status("Converting", expanded=False) as status:
        holder = "Done"
        start_time = time.time()
        api_response = mf.call_convert_api(translated_markdown_text, convert_headers)
        conversion_id = mf.get_id(api_response, type="conversion")
        while True:
            if start_time - time.time() > 150:
                holder = "not done"
                break
            convert_status = mf.check_status(
                conversion_id, convert_headers, type="converter"
            )
            st.write(convert_status["html"]["status"])
            if convert_status["html"]["status"] == "completed":
                break
            time.sleep(2)

        result_html = mf.get_result(conversion_id, convert_headers, type="converter")
        result_html = result_html.text
        updated_html_content = cf.update_css_style(result_html)
        if updated_html_content:
            print("CSS 스타일이 성공적으로 업데이트되었습니다.")
            # 수정된 HTML 내용을 파일에 다시 쓰기
            with open(
                os.path.join(html_folder_path, translated_markdown_option + ".html"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(updated_html_content)
            st.session_state["htmls"][translated_markdown_option] = updated_html_content
        else:
            print("지정된 CSS 스타일을 찾을 수 없습니다.")
            with open(
                os.path.join(html_folder_path, translated_markdown_option + ".html"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(result_html)
                st.session_state["htmls"][translated_markdown_option] = result_html
col1, col2, col3 = st.columns(3)
with col1:
    try:
        result_html = st.session_state["htmls"][translated_markdown_option]
        if result_html is not None:
            st.download_button(
                label="Download Translated HTML",
                data=result_html,
                file_name=translated_markdown_option + ".html",
                mime="text/html",
            )
        else:
            raise Exception
    except Exception as ex:
        st.markdown("#### Please start with the HTML conversion")

with col2:
    try:
        result_html = st.session_state["htmls"][translated_markdown_option]

        if result_html is not None:
            pdf_button = st.button(label="Convert to PDF")
            pdf_file_path = os.path.join(
                pdf_folder_path, translated_markdown_option + ".pdf"
            )
            if pdf_button:
                cf.convert_to_pdf(result_html, translated_markdown_option)
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as file:
                    pdf_content = file.read()
                st.download_button(
                    label="Download PDF",
                    data=pdf_content,
                    file_name=translated_markdown_option + ".pdf",
                    mime="pdf",
                )
            else:
                st.markdown("#### Please start with the PDF conversion")
    except:
        st.markdown("#### Please start with the HTML conversion")

# with col3:
#     st.button(label="delete somthing")


# chunk를 나눈 뒤에 청크별로 번역하고 번역하는 모습을 보여준 뒤에 비교해서 다시 번역 할수 있는 기능
# 컨테이너를 두개로 나누어서
