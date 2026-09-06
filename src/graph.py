from typing import Literal

from langgraph.graph import END, START, StateGraph

from src.agents.analyzer import document_analyzer
from src.agents.planner import research_agent
from src.agents.reporter import final_agent
from src.agents.reviewer import quality_reviewer
from src.agents.search import search_agent
from src.config import MAX_SEARCH_ITERATIONS
from src.state import ResearchState


def quality_router(state: ResearchState) -> Literal["search", "final"]:
    search_count = state.get("search_count", 0)
    need_more_search = state.get("need_more_search", False)
    max_iterations = state.get("max_search_iterations") or MAX_SEARCH_ITERATIONS

    if need_more_search and search_count < max_iterations:
        print(
            f"\n🔄 Iteration {search_count}/{max_iterations}: Additional research required. Returning to Search Agent."
        )
        return "search"

    if search_count >= max_iterations and need_more_search:
        print(
            f"\n⚠️ Search cap reached ({max_iterations} iterations). Proceeding directly to Final Report."
        )

    return "final"


def build_graph():
    graph_builder = StateGraph(ResearchState)

    graph_builder.add_node("research", research_agent)
    graph_builder.add_node("search", search_agent)
    graph_builder.add_node("analyze", document_analyzer)
    graph_builder.add_node("review", quality_reviewer)
    graph_builder.add_node("final", final_agent)

    graph_builder.add_edge(START, "research")
    graph_builder.add_edge("research", "search")
    graph_builder.add_edge("search", "analyze")
    graph_builder.add_edge("analyze", "review")

    graph_builder.add_conditional_edges(
        "review",
        quality_router,
        {
            "search": "search",
            "final": "final",
        },
    )

    graph_builder.add_edge("final", END)

    return graph_builder.compile()


app_graph = build_graph()
