from concurrent.futures import ThreadPoolExecutor
from src.state import ResearchState
from src.agents import llm
from src.utils import extract_text

def document_analyzer(state: ResearchState) -> dict:
    documents = state.get("new_documents", [])

    if not documents:
        print("\nNo new documents to analyze.")
        return {"summaries": []}

    print(f"\nAnalyzing {len(documents)} new documents in parallel...")

    def summarize_doc(doc: SourceDocument) -> DocumentSummary:
        prompt = f"""
You are a Document Analysis Agent.
Analyze the document below and summarize the key findings.

ID: {doc['doc_id']}
Title: {doc['title']}
URL: {doc['url']}
Source: {doc['source_type']}

Content:
{doc['content']}


Return ONLY the summary.
"""
        try:
            response = llm.invoke(prompt)
            summary = extract_text(response.content)
            return {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "url": doc["url"],
                "source": doc["source"],
                "summary": summary_text
            }
        except Exception as e:
            print(f"  ✗ Failed to summarize document {i}: {e}")
            return ""

    with ThreadPoolExecutor(max_workers=min(len(documents), 10)) as executor:
        results = list(executor.map(summarize_doc, enumerate(documents, start=1)))

    new_summaries = [res for res in results if res]
    return {"summaries": new_summaries}
