import re
from typing import List

from duowen_agent.llm import tokenizer
from duowen_agent.rag.models import Document


def split_text_with_regex(
    text: str, separator: str = "\n\n", keep_separator: bool = True
) -> list[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({re.escape(separator)})", text)
            splits = [_splits[i - 1] + _splits[i] for i in range(1, len(_splits), 2)]
            if len(_splits) % 2 != 0:
                splits += _splits[-1:]
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if (s not in {"", "\n"})]


def merge_documents(documents: List[Document], chunk_size=512) -> List[Document]:
    if chunk_size == 0:
        return documents

    _data = []
    _curr_data = []

    for i in documents:
        _curr_data_str = "\n\n".join(_curr_data + [i.page_content])
        if tokenizer.emb_len(_curr_data_str) <= chunk_size:
            _curr_data.append(i.page_content)
        elif tokenizer.emb_len(_curr_data_str) > chunk_size:
            _data.append("\n\n".join(_curr_data))
            _curr_data = [i.page_content]

    if _curr_data:
        _data.append("\n\n".join(_curr_data))

    return [
        Document(
            page_content=i,
            metadata=dict(token_count=tokenizer.emb_len(i), chunk_index=idx),
        )
        for idx, i in enumerate(_data)
    ]
