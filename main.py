import warnings
warnings.filterwarnings("ignore")
from src.config import MAX_SEARCH_ITERATIONS
from src.state import ResearchState
from src.graph import app_graph

def main():
    query = input(" Enter your research question:  ")

    initial_state: ResearchState = {
        "query": query,
        "topics": [],
        "documents": [],
        "new_documents": [],
        "summaries": [],
        "quality_score": 0.0,
        "need_more_search": False,
        "missing_topics": [],
        "review_feedback": "",
        "final_report": "",
        "search_count": 0,
        "max_search_iterations": MAX_SEARCH_ITERATIONS,
    }

    result = app_graph.invoke(initial_state, config={"recursion_limit": 40})

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result["final_report"])

if __name__ == "__main__":
    main()
