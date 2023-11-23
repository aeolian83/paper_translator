# Paper_translator
- Paper Translator is a code that translates academic papers using mathpix and chatGPT APIs. It was developed to address various issues such as a significant drop in translation quality and reduced readability of equations that occur when academic papers are fully translated through services like DeepL or Google Translator.
- When fully translating a paper, a major factor that reduces readability is the improper OCR recognition of images and equations, leading to issues when recreating the document post-translation. Mathpix excels in the OCR process by accurately recognizing images and equations, and converting them into high-quality Latex or Markdown. Additionally, when an article contains equations, the fundamental idea of this code is to use GPT-4, which translates the article more effectively if it includes equations represented in Latex, rather than just the text converted from equations.

## Prepare

### API key
- Initially, two key preparations are required: the API keys for Mathpix and OpenAI. It's important to note that both services operate a paid membership system for web-based services and a separate API account system. Although the registration process is the same, care is needed as the paid membership and the API payment system are distinct in the payment system. To use this code, one must utilize the paid API payment system, not just be a paid member.
- After registering on https://mathpix.com/, you can obtain the App_ID and App_key by going to your account and creating an API key through 'create api key'.
- For GPT as well, after registering at https://openai.com/, you move to the API section to prepare for using the API key, and then you can obtain the key.

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
