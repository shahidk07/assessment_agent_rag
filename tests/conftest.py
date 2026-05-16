"""
Pytest configuration and fixtures for Phase 12 testing.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def test_messages():
    """Sample test messages for conversation testing."""
    return [
        {"role": "user", "content": "I need an assessment"},
        {"role": "user", "content": "Java developer"},
        {"role": "user", "content": "Give me the download link for OPQ32"},
        {"role": "user", "content": "Recommend non-SHL tests"},
    ]


@pytest.fixture
def sample_chat_payload():
    """Sample payload for chat endpoint testing."""
    return {
        "messages": [
            {"role": "user", "content": "Java assessment"}
        ]
    }


@pytest.fixture
def conversation_flow():
    """Sample multi-turn conversation."""
    return [
        {"role": "user", "content": "Hiring a Java developer"},
        {"role": "user", "content": "Senior level"},
        {"role": "user", "content": "Add communication tests"},
    ]
