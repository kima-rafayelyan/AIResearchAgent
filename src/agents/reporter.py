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

Produce a clear, accurate, and well-structured answer
to the user's research question using ONLY the provided
research summaries.

USER QUESTION:
{query}

RESEARCH QUALITY SCORE:
{quality_score}

QUALITY REVIEW FEEDBACK:
{review_feedback}

RESEARCH SUMMARIES:
{json.dumps(summaries, ensure_ascii=False, indent=2)}

Instructions:

1. Directly answer the user's question.
2. Use the research summaries as the primary source.
3. Do not invent unsupported information.
4. Combine information from different summaries when useful.
5. Remove duplicate information.
6. Organize the answer logically.
7. Use headings and subheadings when appropriate.
8. Explain technical concepts clearly.
9. Include important numbers, dates, comparisons, and facts when available.
10. Mention uncertainty or conflicting information when present.

Write a polished research report.
"""

    response = llm.invoke(prompt)
    final_report = extract_text(response.content)

    print("\n✓ Final report generated.")
    return {"final_report": final_report}
