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

    def summarize_doc(item: tuple[int, str]) -> str:
        i, doc = item
        prompt = f"""
You are a Document Analysis Agent in a research system.
Analyze the research document below.

Your summary must:
- Be concise and fact-based.
- Identify main ideas, important findings, technical details, definitions, or evidence.
- Avoid unsupported claims.

DOCUMENT:
{doc}

Return ONLY the summary.
"""
        try:
            response = llm.invoke(prompt)
            summary = extract_text(response.content)
            if summary:
                print(f"  ✓ Document {i} summarized")
                return summary
            else:
                print(f"  ⚠ Document {i} produced an empty summary")
                return ""
        except Exception as e:
            print(f"  ✗ Failed to summarize document {i}: {e}")
            return ""

    with ThreadPoolExecutor(max_workers=min(len(documents), 10)) as executor:
        results = list(executor.map(summarize_doc, enumerate(documents, start=1)))

    new_summaries = [res for res in results if res]
    return {"summaries": new_summaries}
