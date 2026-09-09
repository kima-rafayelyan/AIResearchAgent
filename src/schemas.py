from typing import List

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    topics: List[str] = Field(description="4-5 focused research topics")


class QualityReview(BaseModel):
    quality_score: float = Field(description="Overall research quality score from 0.0 to 1.0.")
    need_more_search: bool = Field(
        description="True if additional research is needed, otherwise False."
    )
    missing_topics: List[str] = Field(
        description="Specific research topics that are missing and should be searched if more research is needed."
    )
    review_feedback: str = Field(description="Detailed explanation of the quality assessment.")
