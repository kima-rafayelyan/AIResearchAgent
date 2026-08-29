import json
from src.state import ResearchState
from src.schemas import QualityReview
from src.agents import llm

def quality_reviewer(state: ResearchState) -> dict:
    query = state["query"]
    topics = state.get("topics", [])
    summaries = state.get("summaries", [])

    print("\n" + "=" * 60)
    print("QUALITY REVIEW")
    print("=" * 60)

    prompt = f"""
You are a strict research quality reviewer.

Evaluate whether the collected research is sufficient to answer
the user's question thoroughly.

USER QUESTION:
{query}

RESEARCH TOPICS:
{json.dumps(topics, ensure_ascii=False, indent=2)}

RESEARCH SUMMARIES:
{json.dumps(summaries, ensure_ascii=False, indent=2)}

Evaluate:

1. Completeness
   Does the research cover the important aspects of the question?

2. Relevance
   Are the summaries relevant to the user's question?

3. Depth
   Is there enough information for a good final answer?

4. Accuracy
   Does the information appear reliable and consistent?

5. Coverage
   Are there important topics that have not been researched?

SCORING:

0.0 - 0.3  Very poor
0.3 - 0.5  Poor
0.5 - 0.7  Moderate
0.7 - 0.85 Good
0.85 - 1.0 Excellent

IMPORTANT:

If the research is insufficient:
- quality_score should be below 0.85
- need_more_search must be true
- missing_topics must contain the specific missing research topics

If the research is sufficient:
- quality_score should be >= 0.85
- need_more_search must be false
- missing_topics must be an empty list

Each missing topic must be specific enough to search on the web.
"""

    reviewer_llm = llm.with_structured_output(QualityReview)

    result = None
    last_error = None
    for attempt in range(2):
        try:
            result = reviewer_llm.invoke(prompt)
            break
        except Exception as e:
            last_error = e
            print(f"\n⚠ Reviewer call failed (attempt {attempt + 1}/2): {e}")

    if result is None:
        print(f"\n❌ Reviewer failed after retries: {last_error}")
        return {
            "quality_score": state.get("quality_score", 0.0),
            "need_more_search": False,
            "missing_topics": [],
            "review_feedback": (
                f"Quality review could not be completed after retries "
                f"({last_error}). Proceeding to the final report with the "
                f"research collected so far; quality was not verified."
            ),
        }

    quality_score = max(0.0, min(1.0, float(result.quality_score)))
    need_more_search = bool(result.need_more_search)
    missing_topics = result.missing_topics if isinstance(result.missing_topics, list) else []
    review_feedback = result.review_feedback or ""

    print(f"\nQuality score: {quality_score}")
    print(f"Need more search: {need_more_search}")
    print("\nMissing topics:")
    if missing_topics:
        for topic in missing_topics:
            print(f"  - {topic}")
    else:
        print("  None")
    print(f"\nFeedback:\n{review_feedback}")

    return {
        "quality_score": quality_score,
        "need_more_search": need_more_search,
        "missing_topics": missing_topics,
        "review_feedback": review_feedback,
    }
