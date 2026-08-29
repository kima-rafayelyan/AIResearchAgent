import json
from src.state import ResearchState
from src.agents import llm
from src.utils import extract_text

def final_agent(state: ResearchState) -> dict:
    query = state["query"]
    summaries = state.get("summaries", [])
    quality_score = state.get("quality_score", 0.0)
    review_feedback = state.get("review_feedback", "")

    print("\n" + "=" * 60)
    print("FINAL REPORT GENERATION")
    print("=" * 60)

    prompt = f"""
You are the final research report agent.

Produce a clear, accurate, and well-structured answer to the user's research question using ONLY the provided research summaries.

USER QUESTION:
{query}

RESEARCH QUALITY SCORE:
{quality_score}

QUALITY REVIEW FEEDBACK:
{review_feedback}

RESEARCH SUMMARIES (WITH METADATA):
{json.dumps(summaries, ensure_ascii=False, indent=2)}

SMART CITATION RULES:
1. Do NOT place a bracketed citation after every single sentence. Group facts naturally and insert citations at key claims or at the end of cohesive paragraphs (e.g., [doc_1, doc_2]).
2. Do NOT cite bullet point headers or general transition sentences.
3. Use ONLY Document IDs provided in the summaries ([doc_1], [doc_2], etc.).
4. At the very end of the report, write a dedicated "## References" section.
5. In the References section, list every cited document using its exact metadata from the summaries:
   - **[doc_id]**: [Title](URL) - *Source*

Write the complete cited research report below:
"""

    response = llm.invoke(prompt)
    final_report = extract_text(response.content)

    print("\n✓ Final report generated.")
    return {"final_report": final_report}
