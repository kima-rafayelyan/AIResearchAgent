from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from src.agents import llm
from src.state import ResearchState
from src.utils import extract_text


def summarize_doc(item: tuple) -> Optional[Dict[str, Any]]:
    """Unpacks (index, doc) safely handling dicts and string fallbacks."""
    i, doc = item

    if isinstance(doc, dict):
        doc_id = doc.get("doc_id", f"doc_{i}")
        title = doc.get("title", f"Document {i}")
        url = doc.get("url", "N/A")
        source = doc.get("source", "Web")
        content = doc.get("content", "")
    else:
        doc_id = f"doc_{i}"
        title = f"Document {i}"
        url = "N/A"
        source = "Unknown"
        content = str(doc)

    prompt = f"""You are a Document Analysis Agent.
Analyze the document below and summarize key findings, facts, and metrics.

ID: {doc_id}
Title: {title}
URL: {url}
Source: {source}

Content:
{content}

Return ONLY the summary text."""

    try:
        response = llm.invoke(prompt)
        summary_text = extract_text(response.content)

        if not summary_text:
            return None

        return {
            "doc_id": doc_id,
            "title": title,
            "url": url,
            "source": source,
            "summary": summary_text,
        }
    except Exception as e:
        print(f"  ✗ Failed to summarize document {i} ({doc_id}): {e}")
        return None


def document_analyzer(state: ResearchState) -> dict:
    documents = state.get("new_documents", [])

    if not documents:
        print("\nNo new documents to analyze.")
        return {"summaries": []}

    print(f"\nAnalyzing {len(documents)} new documents in parallel...")

    with ThreadPoolExecutor(max_workers=min(len(documents), 10)) as executor:
        results = list(executor.map(summarize_doc, enumerate(documents, start=1)))

    new_summaries = [res for res in results if res is not None]
    return {"summaries": new_summaries}
