from pydantic import BaseModel, Field
from typing import Literal


class SupervisorResponse(BaseModel):
    """Schema for supervisor classification response"""
    classifier: Literal["business", "research", "technical"] = Field(
        ..., 
        description="Classifies the question and returns one of: ['business','research','technical']"
    )
    region: str = Field(
        ..., 
        description="Explanation of why this classification was chosen"
    )


class ConfidenceScore(BaseModel):
    """Schema for validator confidence score"""
    range: str = Field(
        description="Confidence score in the range between 0-10 only"
    )
