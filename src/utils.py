from typing import Any

def extract_text(content: Any) -> str:
    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part and part.strip())

    return str(content).strip()
    
    
import json
from typing import List, Any
from src.state import SourceDocument

def extract_documents(content: Any, start_idx: int) -> List[SourceDocument]:
    docs = []
    if not content:
        return docs

    try:
        parsed = json.loads(content) if isinstance(content, str) else content

        if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
            parsed = parsed["results"]

        items = parsed if isinstance(parsed, list) else [parsed]

        for item in items:
            if not isinstance(item, dict) or "error" in item:
                continue
            start_idx += 1

            docs.append({
                "doc_id": f"doc_{start_idx}",
                "title": item.get("title") or item.get("heading") or f"Document {start_idx}",
                "url": item.get("url") or item.get("link") or "N/A",
                "source": item.get("source") or item.get("source_type") or "Web Search",
                "content": item.get("content") or item.get("raw_content") or item.get("summary") or ""
            })
    except Exception:
        if isinstance(content, str) and content.strip():
            start_idx += 1
            docs.append({
                "doc_id": f"doc_{start_idx}",
                "title": f"Web Source {start_idx}",
                "url": "N/A",
                "source": "Web",
                "content": content.strip()
            })

    return docs
