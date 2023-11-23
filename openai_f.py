import re
import os
from tqdm import tqdm
import tiktoken
from openai import OpenAI


os.environ['OPENAI_API_KEY'] = "your openai api key"

# Your OpenAI API key
client = OpenAI()

# Decide paper field
paper_field = 'ai'

def make_chunks(pdf_id):
    print("Make chunk with Markdown file")
    with open("./markdown/" + pdf_id + ".md", "r") as f:
        text = f.read()
    
    tokenizer = tiktoken.encoding_for_model("gpt-4")

    chunks = text.split('\n\n')
    ntokens = []
    for chunk in chunks:
        ntokens.append(len(tokenizer.encode(chunk)))

    return chunks, ntokens


def group_chunks(chunks, ntokens, max_len=600, hard_max_len=3000):
    """
    Group very short chunks, to form approximately page long chunks.
    """
    print("Grouping chunks")
    batches = []
    cur_batch = ""
    cur_tokens = 0
    
    # iterate over chunks, and group the short ones together
    for chunk, ntoken in zip(chunks, ntokens):
        # discard chunks that exceed hard max length
        if ntoken > hard_max_len:
            print(f"Warning: Chunk discarded for being too long ({ntoken} tokens > {hard_max_len} token limit). Preview: '{chunk[:50]}...'")
            continue

        # if room in current batch, add new chunk
        if cur_tokens + 1 + ntoken <= max_len:
            cur_batch += "\n\n" + chunk
            cur_tokens += 1 + ntoken  # adds 1 token for the two newlines
        # otherwise, record the batch and start a new one
        else:
            batches.append(cur_batch)
            cur_batch = chunk
            cur_tokens = ntoken
            
    if cur_batch:  # add the last batch if it's not empty
        batches.append(cur_batch)
        
    return batches


def tranlate_content(text, paper_field):
    completion = client.chat.completions.create(
      model="gpt-4-1106-preview",
      messages=[
        {"role": "system", "content": f"You are an expert in the field of {paper_field}. You have the ability to explain the {paper_field} field easily, even to those who are not familiar with it."},
        {"role": "user", "content": f'''
You will translate English academic papers in the field of {paper_field}, which are written in Markdown, section by section into Korean.

Condition 1: Translate the {paper_field} academic papers into an easy-to-understand style.
Condition 2: For specialized terms related to the field, translate them in the format of Korean(English).
Condition 3: Do not create any other responses, only generate the translation.
Condition 4: Please Leave all Markdown or LaTeX commands unchanged.
Condition 5: Translate quotations, examples, etc., enclosed in double quotes (“”), in the format of Korean(English).
Condition 6: Do not omit image insertion commands starting with '!', and make sure to include them.

Translate the text below from English to Korean according to the above conditions.
         {text}
'''},
      ]
    )

    return completion.choices[0].message.content


def make_translated_markdown(chunks, file_name, paper_field):
    print("Translating")
    translated_content = []

    for chunk in tqdm(chunks):
        tranlated = tranlate_content(chunk, paper_field) + '\n\n'
        translated_content.append(tranlated)
    
    print("Make Translated Markdown")
    with open('./markdown/translated_' + file_name + '.md', 'w') as file:
        for line in translated_content:
            file.write(line)
    