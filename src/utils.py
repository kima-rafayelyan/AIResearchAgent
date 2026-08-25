from typing import Any

    def extract_documents(content: Any, start_idx: int) -> List[SourceDocument]:
    docs = []
    if not content:
        return docs
        
    try:
        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content

        items = parsed if isinstance(parsed, list) else [parsed]
        
        for item in items:
            if isinstance(item, dict) and "content" in item:
                start_idx += 1
                docs.append({
                    "doc_id": f"doc_{start_idx}",
                    "title": item.get("title", "Untitled"),
                    "url": item.get("url") or item.get("url", "N/A"),
                    "source": item.get("source", "Web"),
                    "content": item.get("content", "")
                })
            elif isinstance(item, dict) and "raw_content" in item: 
                start_idx += 1
                docs.append({
                    "doc_id": f"doc_{start_idx}",
                    "title": item.get("title", "Web Result"),
                    "url": item.get("url", "N/A"),
                    "source": "Tavily Search",
                    "content": item.get("content") or item.get("raw_content", "")
                })
    except Exception:
        if isinstance(content, str) and content.strip():
            start_idx += 1
            docs.append({
                "doc_id": f"doc_{start_idx}",
                "title": "Text Snippet",
                "url": "N/A",
                "source": "Unknown",
                "content": content.strip()
            })
            
    return docs
