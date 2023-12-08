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

# Translate samples
tr_example_orgin = """
## 3 INTRODUCTION

The second misconception arises from implementing the dual averaging form of AdaGrad without considering what modifications need to be made for the deep learning setting. The algorithm as originally stated, uses an initial point of the origin $x_{0}=0$, and a proximity function $\psi_{t}(x)=\frac{1}{2}\left\langle x, H_{t} x\right\rangle$ that is quadratic, but centered around the origin. It is well known that neural network training exhibits pathological behavior when initialized at the origin, and so naive use of this algorithm does not perform well. When centering around 0 , we have observed severely degraded empirical performance and a high risk of divergence. Instead, a proximity function centered about $x_{0}$ needs to be used:

![](https://cdn.mathpix.com/cropped/2023_11_23_f17960590d4cd40b8379g-2.jpg?height=325&width=805&top_left_y=233&top_left_x=194)

$$
x_{k+1}=x_{0}-\sum_{i=0}^{k} \gamma_{i} g_{i}
$$
"""

tr_example_trans = """
## 3 INTRODUCTION

두 번째 오해는 AdaGrad의 이중 평균 형태(the dual averaging form)를 딥 러닝(deep learning) 환경에 맞게 수정해야 한다는 점을 고려하지 않고 구현하는 데서 비롯됩니다. 원래의 알고리즘은 원점 $x_0=0$에서 시작하고, 근접시 함수 $\psi_t(x)=\frac{1}{2}\left\langle x, H_t x\right\rangle$를 사용하며, 이 함수는 이차 함수이지만 원점을 중심으로 합니다. 신경망 학습은 원점에서 초기화할 때 비정상적인 행동을 보인다는 것은 잘 알려져 있으며, 따라서 이 알고리즘을 순진하게 사용하면 성능이 좋지 않습니다. 0을 중심으로 할 때, 우리는 심각한 성능 저하와 발산의 위험을 관찰했습니다. 대신 $x_0$를 중심으로 한 근접 함수를 사용해야 합니다:

![](https://cdn.mathpix.com/cropped/2023_11_23_f17960590d4cd40b8379g-2.jpg?height=325&width=805&top_left_y=233&top_left_x=194)

$$
x_{k+1}=x_{0}-\sum_{i=0}^{k} \gamma_{i} g_{i}
$$
"""

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


def group_chunks(chunks, ntokens, max_len=600, hard_max_len=4000):
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


# def tranlate_content(text, paper_field):
#     completion = client.chat.completions.create(
#       model="gpt-4-1106-preview",
#       messages=[
#         {"role": "system", "content": f"You are an expert in the field of {paper_field}. You have the ability to explain the {paper_field} field easily, even to those who are not familiar with it."},
#         {"role": "user", "content": f'''
# You will translate English academic papers in the field of {paper_field}, which are written in Markdown, section by section into Korean.

# Condition 1: Translate the {paper_field} academic papers into an easy-to-understand style.
# Condition 2: For specialized terms related to the field, translate them in the format of Korean(English).
# Condition 3: Do not create any other responses, only generate the translation.
# Condition 4: Please Leave all Markdown or LaTeX commands unchanged.
# Condition 5: Translate quotations, examples, etc., enclosed in double quotes (“”), in the format of Korean(English).
# Condition 6: Do not omit image insertion commands starting with '!', and make sure to include them.

# Translate the text below from English to Korean according to the above conditions.
# '''},
#         {"role": "user", "content": text},
#       ]
#     )

#     return completion.choices[0].message.content

def make_prompts(paper_field, tr_example_orgin, tr_example_trans, text):
    prompt = [
        {"role": "system", "content": f"You are an expert in the field of {paper_field}. You have the ability to explain the {paper_field} field easily, even to those who are not familiar with it."},
        {"role": "system", "content": f'''
You will translate English academic papers in the field of {paper_field}, which are written in Markdown, section by section into Korean.

Condition 1: Translate the {paper_field} academic papers into an easy-to-understand style.
Condition 2: For specialized terms related to the field, translate them in the format of Korean(English).
Condition 3: Do not create any other responses, only generate the translation.
Condition 4: Please Leave all Markdown or LaTeX commands unchanged.
Condition 5: Translate quotations, examples, etc., enclosed in double quotes (“”), in the format of Korean(English).


'''},
        {"role": "user", "content": f'''Translation Sample

        {tr_example_orgin}
         
{tr_example_trans}
'''},
        {"role": "user", "content": f'''Based on the conditions and sample translation provided above, please translate the following English paper written in Markdown into Korean.
'''},
        {"role": "user", "content": f"""
        {text}

"""}
        ]
    return prompt

def tranlate_content(prompts):
    completion = client.chat.completions.create(
      model="gpt-4-1106-preview",
      messages=prompts,
      temperature = 0.1
    )

    return completion.choices[0].message.content


def make_translated_markdown(chunks, file_name, paper_field):
    print("Translating")
    translated_content = []

    for chunk in tqdm(chunks):
        prompt = make_prompts(paper_field, tr_example_orgin, tr_example_trans, chunk)
        tranlated = tranlate_content(prompt) + '\n\n'
        translated_content.append(tranlated)
    
    print("Make Translated Markdown")
    with open('./markdown/translated_' + file_name + '.md', 'w') as file:
        for line in translated_content:
            file.write(line)