# Paper_translator V0.4
- Paper Translator is a code that translates academic papers using mathpix and chatGPT APIs. It was developed to address various issues such as a significant drop in translation quality and reduced readability of equations that occur when academic papers are fully translated through services like DeepL or Google Translator.
- When fully translating a paper, a major factor that reduces readability is the improper OCR recognition of images and equations, leading to issues when recreating the document post-translation. Mathpix excels in the OCR process by accurately recognizing images and equations, and converting them into high-quality Latex or Markdown. Additionally, when an article contains equations, the fundamental idea of this code is to use GPT-4, which translates the article more effectively if it includes equations represented in Latex, rather than just the text converted from equations.

## Prepare

### API key
- Initially, two key preparations are required: the API keys for Mathpix and OpenAI. It's important to note that both services operate a paid membership system for web-based services and a separate API account system. Although the registration process is the same, care is needed as the paid membership and the API payment system are distinct in the payment system. To use this code, one must utilize the paid API payment system, not just be a paid member.
- After registering on https://mathpix.com/, you can obtain the App_ID and App_key by going to your account and creating an API key through 'create api key'.
- For GPT as well, after registering at https://openai.com/, you move to the API section to prepare for using the API key, and then you can obtain the key.

## How it works

### Installation
- Firstly, you may choose to create a virtual environment or not, but using a virtual environment is recommended. As for the Python version, the development was done on version 3.9.7, and it is believed that any version above 3.9 should work without major issues.

- Next, copy the git repository to your local environment.

```shell
$ git clone https://github.com/aeolian83/paper_translator.git
```

- Install the requirements using pip.

```shell
$ pip install -r requirements.txt
```

### Variable setting
1. Enter the App_ID and App_key from Mathpix into the headers of mathpix_f.py.
2. Enter the API key from OpenAI into the code for setting the environmental variables in openai_f.py.
3. Place the PDF document to be translated in the ./pdf folder, and then enter the filename without the extension into the filename variable in main.py.
4. Enter the field of the paper into the variable named 'paper_field' in openai_f.py. The default value is 'ai'.

### Execute
- Once the variable setting is complete, execute main.py.
```shell
$ python main.py
```

### Post-processing
- Since Mathpix's markdown to PDF is built on node.js, it was not possible to create an end-to-end code that directly produces a PDF in one go. This remains a task for future work. Currently, the translated content is stored in the markdown format in the markdown folder. You can view it as it is in markdown format, or you can convert it to PDF by visiting https://snip.mathpix.com/.


## Future Work
- V0.5: Integrate markdown_to_pdf into the main code (requires merging of the work process through Node.js).
- V0.6~0.7: Implement translation code using palm2 API or an open-source LLM to reduce API costs.
- V0.8: Implementation of a GUI through Gradio.
### Long-term project
- Explore free OCR libraries that can replace Mathpix OCR.

## Precautions
- This code is designed to translate English papers into Korean. If you want to translate into another language, you can change the prompt in the translate_content function in openai_f.py. Similarly, if you want to add other conditions to the translation, you can also modify the prompt.
- If you are not satisfied with the quality of the translation, or if images or equations are omitted, adjusting the max_len argument in the group_chunks function in openai_f.py can sometimes be helpful.


## Reference
- https://platform.openai.com/tokenizer
- https://github.com/openai/openai-cookbook/blob/main/examples/book_translation/translate_latex_book.ipynb
- https://docs.mathpix.com/#introduction
- https://jimmy-ai.tistory.com/399