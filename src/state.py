import operator
from typing import Annotated, List, TypedDict

class SourceDocument(TypedDict):
    doc_id: str         
    source_type: str     
    title: str
    url: str
    content: str

class DocumentSummary(TypedDict):
    doc_id: str
    source_type: str
    title: str
    url: str
    summary: str
    

class ResearchState(TypedDict):
    query: str
    topics: List[str]
    documents: Annotated[List[SourceDocument], operator.add]
    new_documents: List[SourceDocument]
    summaries: Annotated[List[DocumentSummary], operator.add]
    quality_score: float
    need_more_search: bool
    missing_topics: List[str]
    review_feedback: str
    final_report: str
    search_count: int
