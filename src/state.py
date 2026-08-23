import operator
from typing import Annotated, List, TypedDict

class ResearchState(TypedDict):
    query: str
    topics: List[str]
    documents: Annotated[List[str], operator.add]
    new_documents: Annotated[List[str], operator.add]
    summaries: Annotated[List[str], operator.add]
    quality_score: float
    need_more_search: bool
    missing_topics: List[str]
    review_feedback: str
    final_report: str
    search_count: int
