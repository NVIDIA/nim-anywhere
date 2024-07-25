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

"""The collection of prompts used in this application."""

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder


CONDENSE_QUESTION_TEMPLATE = PromptTemplate.from_template(
    """Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone question
    which can be understood without the chat history. Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is.
    Chat History:
    {history}
    Follow Up question: {question}
    Standalone question:"""
)




# Primary Chat Prompt template
CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You're an honest and helpful assistant. Answer the question to the best of your ability."
            "and answer questions based on the following context: {context}",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)
