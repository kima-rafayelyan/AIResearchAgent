import os

import pytest

os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key")


@pytest.fixture
def base_state():
    return {
        "query": "What is retrieval-augmented generation?",
        "topics": [],
        "documents": [],
        "new_documents": [],
        "summaries": [],
        "quality_score": 0.0,
        "need_more_search": False,
        "missing_topics": [],
        "review_feedback": "",
        "final_report": "",
        "search_count": 0,
        "max_search_iterations": 5,
    }
