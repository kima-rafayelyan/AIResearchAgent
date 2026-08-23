from src.state import ResearchState
from src.schemas import ResearchPlan
from src.agents import llm

def research_agent(state: ResearchState) -> dict:
    prompt = f"""
     You are a research planning agent.
     Break the user's question into focused 4-5 research topics that together cover the question thoroughly.
     Each topic must:

    - Cover an important aspect of the question.
    - Be specific enough to search on the web.
    - Avoid unnecessary overlap.
    - Be independently researchable.
    - Together provide comprehensive coverage.
    
     USER QUESTION: {state["query"]}
    
     Return ONLY a JSON array of strings.
    """
    planner_llm = llm.with_structured_output(ResearchPlan)
    response = planner_llm.invoke(prompt)
    topics = response.topics

    print("\nResearch plan:")
    for topic in topics:
        print(f"  - {topic}")

    return {"topics": topics}
