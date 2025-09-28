"""Tests for template functionality."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from template import create_template, create_messages_from_template


def test_create_template():
    """Test template creation."""
    template = create_template()

    # Check if it's a ChatPromptTemplate
    assert hasattr(template, 'format_messages')

    # Format with test data
    messages = template.format_messages(
        role="test_role",
        style="test_style",
        question="test_question",
        chat_history=[]
    )

    assert len(messages) == 2  # System + Human
    assert isinstance(messages[0], SystemMessage)
    assert "test_role" in messages[0].content
    assert "test_style" in messages[0].content
    assert isinstance(messages[1], HumanMessage)
    assert "test_question" in messages[1].content


def test_create_messages_from_template_defaults():
    """Test creating messages from template with default values."""
    messages = create_messages_from_template()

    # Should have 6 messages total (system + 4 history + 1 current question)
    assert len(messages) == 6

    # Check message types
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert isinstance(messages[2], AIMessage)
    assert isinstance(messages[3], HumanMessage)
    assert isinstance(messages[4], AIMessage)
    assert isinstance(messages[5], HumanMessage)

    # Check content contains expected values
    assert "程序员鼓励师" in messages[0].content
    assert "积极、温暖且专业" in messages[0].content
    assert messages[1].content == "你好"
    assert "程序员鼓励师" in messages[2].content
    assert "我觉得自己写的代码太烂了" == messages[3].content
    assert "每个程序员都经历过这个阶段" in messages[4].content
    assert "我的代码一直报错，感觉好沮丧，该怎么办？" in messages[5].content


def test_create_messages_from_template_custom():
    """Test creating messages from template with custom values."""
    custom_history = [
        HumanMessage(content="Custom hello"),
        AIMessage(content="Custom response"),
    ]

    messages = create_messages_from_template(
        role="custom_role",
        style="custom_style",
        question="custom_question",
        chat_history=custom_history
    )

    # Should have 4 messages total (system + 2 history + 1 current question)
    assert len(messages) == 4

    # Check custom values are used
    assert "custom_role" in messages[0].content
    assert "custom_style" in messages[0].content
    assert messages[1].content == "Custom hello"
    assert messages[2].content == "Custom response"
    assert "custom_question" in messages[3].content


def test_create_messages_from_template_empty_history():
    """Test creating messages from template with empty history."""
    messages = create_messages_from_template(chat_history=[])

    # Should have 2 messages total (system + 1 current question)
    assert len(messages) == 2

    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)