from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State definition for the agent workflow"""
    
    question: str
    business_generate: str
    research_generate: str
    technical_generate: str
    business_analyst: str
    research_analyst: str
    technical_analyst: str
    messages: Annotated[List[BaseMessage], add_messages]
    classifier_response: str
    region_response: str
    next: str
    validator_score: str
    final_data: str
