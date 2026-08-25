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
    print("FINAL REPORT")
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

STRICT CITATION INSTRUCTIONS:
1. Every major fact, statement, number, or claim MUST be cited inline using its corresponding Document ID in brackets (e.g., [doc_1] or [doc_2]).
2. Do NOT invent facts or citations that do not appear in the summaries.
3. At the end of the report, write a dedicated "## References" section.
4. For every Document ID cited in the report, list it in the References section using this format:
   - **[doc_id]**: [Title](URL) - *Source Type*

Write the complete cited research report below:
"""

    response = llm.invoke(prompt)
    final_report = extract_text(response.content)

    print("\n✓ Final report generated.")
    return {"final_report": final_report}
