from unittest.mock import patch

from langchain_core.messages import AIMessage

from src.graph import build_graph
from src.schemas import QualityReview, ResearchPlan


@patch("src.agents.reporter.llm")
@patch("src.agents.reviewer.llm")
@patch("src.agents.analyzer.llm")
@patch("src.agents.search.llm_with_tools")
@patch("src.agents.search.llm_with_tools_forced")
@patch("src.agents.planner.llm")
def test_graph_runs_end_to_end(
    mock_planner,
    mock_search_forced,
    mock_search,
    mock_analyzer,
    mock_reviewer,
    mock_reporter,
    base_state,
):

    mock_planner.with_structured_output.return_value.invoke.return_value = ResearchPlan(
        topics=["topic one", "topic two"]
    )


    mock_search_forced.invoke.return_value = AIMessage(content="")

    mock_search.invoke.return_value = AIMessage(content="")

    mock_analyzer.invoke.return_value = AIMessage(content="Fake document summary.")


    mock_reviewer.with_structured_output.return_value.invoke.return_value = QualityReview(
        quality_score=0.9,
        need_more_search=False,
        missing_topics=[],
        review_feedback="Coverage looks sufficient.",
    )


    mock_reporter.invoke.return_value = AIMessage(content="# Fake Final Report\n\nDone.")


    graph = build_graph()
    result = graph.invoke(base_state, config={"recursion_limit": 40})


    assert result["topics"] == ["topic one", "topic two"]
    assert result["quality_score"] == 0.9
    assert result["need_more_search"] is False
    assert result["final_report"] == "# Fake Final Report\n\nDone."


    assert mock_planner.with_structured_output.called
    assert mock_search_forced.invoke.called
    assert mock_reviewer.with_structured_output.called
    assert mock_reporter.invoke.called
