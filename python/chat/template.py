"""Template functionality for chat messages."""

from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_template() -> ChatPromptTemplate:
    """Create a chat prompt template for the programmer encouragement chatbot."""

    return ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}。你需要用{style}的语气回答问题。你的目标是帮助程序员保持积极乐观的心态，提供技术建议的同时也要关注他们的心理健康。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "问题: {question}"),
    ])


def create_messages_from_template(
    role: str = "程序员鼓励师",
    style: str = "积极、温暖且专业",
    question: str = "我的代码一直报错，感觉好沮丧，该怎么办？",
    chat_history: List[BaseMessage] = None,
) -> List[BaseMessage]:
    """Create formatted messages from the template with default chat history."""

    if chat_history is None:
        # Default chat history with two rounds of conversation
        chat_history = [
            HumanMessage(content="你好"),
            AIMessage(content="嘿！我是你的程序员鼓励师！记住，每个优秀的程序员都是从 Debug 中成长起来的。有什么我可以帮你的吗？"),
            HumanMessage(content="我觉得自己写的代码太烂了"),
            AIMessage(content="每个程序员都经历过这个阶段！重要的是你在不断学习和进步。让我们一起看看代码，我相信通过重构和优化，它会变得更好。记住，Rome wasn't built in a day，代码质量是通过持续改进来提升的。"),
        ]

    template = create_template()

    formatted_messages = template.format_messages(
        role=role,
        style=style,
        question=question,
        chat_history=chat_history
    )

    return formatted_messages