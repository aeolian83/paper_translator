import re
import os
from tqdm import tqdm
import tiktoken
from openai import OpenAI

examples = [
    {"original": "## 3 INTRODUCTION", "translate": "## 3 서론(INTRODUCTION)"},
    {
        "original": "The second misconception arises from implementing the dual averaging form of AdaGrad without considering what modifications need to be made for the deep learning setting. The algorithm as originally stated, uses an initial point of the origin $x_{0}=0$, and a proximity function $\psi_{t}(x)=\frac{1}{2}\left\langle x, H_{t} x\right\rangle$ that is quadratic, but centered around the origin. It is well known that neural network training exhibits pathological behavior when initialized at the origin, and so naive use of this algorithm does not perform well. When centering around 0 , we have observed severely degraded empirical performance and a high risk of divergence. Instead, a proximity function centered about $x_{0}$ needs to be used:",
        "translate": "두 번째 오해는 AdaGrad의 이중 평균 형태(the dual averaging form)를 딥 러닝(deep learning) 환경에 맞게 수정해야 한다는 점을 고려하지 않고 구현하는 데서 비롯됩니다. 원래의 알고리즘은 원점 $x_0=0$에서 시작하고, 근접시 함수 $\psi_t(x)=\frac{1}{2}\left\langle x, H_t x\right\rangle$를 사용하며, 이 함수는 이차 함수이지만 원점을 중심으로 합니다. 신경망 학습은 원점에서 초기화할 때 비정상적인 행동을 보인다는 것은 잘 알려져 있으며, 따라서 이 알고리즘을 순진하게 사용하면 성능이 좋지 않습니다. 0을 중심으로 할 때, 우리는 심각한 성능 저하와 발산의 위험을 관찰했습니다. 대신 $x_0$를 중심으로 한 근접 함수를 사용해야 합니다:",
    },
    {
        "original": "![](https://cdn.mathpix.com/cropped/2023_11_23_f17960590d4cd40b8379g-2.jpg?height=325&width=805&top_left_y=233&top_left_x=194)",
        "translate": "![](https://cdn.mathpix.com/cropped/2023_11_23_f17960590d4cd40b8379g-2.jpg?height=325&width=805&top_left_y=233&top_left_x=194)",
    },
    {
        "original": """
$$
x_{k+1}=x_{0}-\sum_{i=0}^{k} \gamma_{i} g_{i}
$$
""",
        "translate": """
$$
x_{k+1}=x_{0}-\sum_{i=0}^{k} \gamma_{i} g_{i}
$$
""",
    },
]


def make_chunks(text):
    tokenizer = tiktoken.encoding_for_model("gpt-4")

    chunks = text.split("\n\n")
    ntokens = []
    for chunk in chunks:
        ntokens.append(len(tokenizer.encode(chunk)))

    return chunks, ntokens


def group_chunks(chunks, ntokens, max_len=700, hard_max_len=4000):
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
            print(
                f"Warning: Chunk discarded for being too long ({ntoken} tokens > {hard_max_len} token limit). Preview: '{chunk[:50]}...'"
            )
            continue

        if chunk.startswith("![]"):
            print(chunk[:5])
            cur_batch += "\n\n" + chunk
            cur_tokens += 1 + ntoken  # adds 1 token for the two newlines
        # if room in current batch, add new chunk
        elif cur_tokens + 1 + ntoken <= max_len:
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
