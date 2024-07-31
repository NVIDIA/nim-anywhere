# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module defines the application's chain."""

from langchain.pydantic_v1 import BaseModel
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.vectorstores.milvus import Milvus
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import ContextualCompressionRetriever
from langchain_nvidia_ai_endpoints import NVIDIARerank

from . import prompts
from .configuration import config as app_config
from .utils import itemgetter
import requests

# %% unstructured data retrieval components
embedding_model = NVIDIAEmbeddings(
    model=app_config.embedding_model.name,
    base_url=str(app_config.embedding_model.url),
    api_key=app_config.nvidia_api_key
)
vector_store = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": app_config.milvus.url},
    collection_name=app_config.milvus.collection_name,
    auto_id=True,
    timeout=10,
)
retriever = vector_store.as_retriever()

reranker = NVIDIARerank(
    model=app_config.reranking_model.name,
    base_url=str(app_config.reranking_model.url),
    api_key=app_config.nvidia_api_key,
)
reranking_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=retriever
)

def format_docs(docs: list[Document]) -> str:
    """Take in a list of docs and concatenate the content, separating by newlines."""
    return "\n\n".join(doc.page_content for doc in docs)


# %% language model components
llm = ChatNVIDIA(
    model=app_config.chat_model.name,
    curr_mode="nim",
    base_url=str(app_config.chat_model.url),
    api_key=app_config.nvidia_api_key,
)


# %% define the llm powered chain

# document retrieval
@chain
async def retrieve_context(msg, config) -> str:
    """The Retrieval part of the RAG chain."""
    use_kb = msg["use_kb"]
    use_reranker = msg["use_reranker"]
    question = msg["question"]

    if not use_kb:
        return ""
    
    if use_reranker:
        return (reranking_retriever | format_docs).invoke(question, config)

    return (retriever | format_docs).invoke(question, config)

# create a question and history condensing chain
@chain
async def question_parsing(msg, config) -> str:
    """Condense the question with chat history"""
    
    condense_question_prompt = prompts.CONDENSE_QUESTION_TEMPLATE.with_config(run_name="condense_question_prompt")
    condensed_chain = condense_question_prompt | llm | StrOutputParser().with_config(run_name="condense_question_chain")
    if msg["history"]:
        return condensed_chain.invoke(msg, config)
    else:
        return msg["question"]

my_chain = (
    {
        "context": retrieve_context,
        "question": question_parsing,
        "history": itemgetter("history", []),
    }
    | RunnablePassthrough().with_config(run_name="LLM Prompt Input")
    | prompts.CHAT_PROMPT
    | llm
)


# %% finalize the chain with history and an explicit API
class ChainInputs(BaseModel):
    """Declaration of the chain's input values."""

    question: str
    use_kb: bool = True
    use_reranker: bool = True


ChainOutputs = str


my_chain = RunnableWithMessageHistory(
    my_chain,
    lambda session_id: RedisChatMessageHistory(session_id, url=str(app_config.redis_dsn)),
    input_messages_key="question",
    output_messages_key="output",
    history_messages_key="history",
    custom_input_type=ChainInputs,
    custom_output_type=ChainOutputs,
)

# %% uncomment this line to print the chain architecture on startup
# chain.get_graph().print_ascii()
