import json

from src.utils import extract_documents, extract_text


def test_extract_text_empty_string():
    assert extract_text(None) == ""


def test_extract_text_plain_string():
    assert extract_text("  hello world  ") == "hello world"


def test_extract_text_list_of_strings():
    assert extract_text(["a", "b", "c"]) == "a\nb\nc"


def test_extract_text_list_of_dicts_with_text_key():
    assert extract_text([{"text": "first"}, {"text": "second"}]) == "first\nsecond"


def test_extract_text_list_of_dicts_with_content_key():
    assert extract_text([{"content": "first"}, {"content": "second"}]) == "first\nsecond"


def test_extract_text_mixed_and_malformed_input():
    content = ["plain", {"text": "dict-text"}, 42, None, {"other": "ignored"}]
    assert extract_text(content) == "plain\ndict-text"


def test_extract_document_valid_json_list():
    content = json.dumps([{"title": "A", "url": "http://a", "content": "body a"}])
    docs = extract_documents(content, 0)
    assert docs == [
        {
            "doc_id": "doc_1",
            "title": "A",
            "url": "http://a",
            "source": "Web Search",
            "content": "body a",
        }
    ]


def test_extract_document_tavily_results():
    content = json.dumps(
        {"results": [{"title": "A", "content": "a"}, {"title": "B", "content": "b"}]}
    )
    docs = extract_documents(content, 0)
    assert [d["doc_id"] for d in docs] == ["doc_1", "doc_2"]
    assert [d["title"] for d in docs] == ["A", "B"]


def test_extract_document_error_items():
    content = json.dumps([{"title": "Good", "content": "kept"}, {"error": "boom"}])
    docs = extract_documents(content, 0)
    assert len(docs) == 1
    assert docs[0]["title"] == "Good"


def test_extract_document_all_errors_returns_empty_list():
    content = json.dumps([{"error": "boom"}])
    assert extract_documents(content, 0) == []


def test_extract_document_malformed_json():
    content = "this is not valid json {{{"
    docs = extract_documents(content, 0)
    assert docs == [
        {
            "doc_id": "doc_1",
            "title": "Web Source 1",
            "url": "N/A",
            "source": "Web",
            "content": content,
        }
    ]


def test_extract_document_sequential_ids_with_nonzero_start_idx():
    content = json.dumps([{"title": "A", "content": "a"}, {"title": "B", "content": "b"}])
    docs = extract_documents(content, 5)
    assert [d["doc_id"] for d in docs] == ["doc_6", "doc_7"]
