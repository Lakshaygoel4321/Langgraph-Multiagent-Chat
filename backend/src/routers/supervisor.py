from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config.settings import settings
from config.prompts import PromptTemplates
from src.utils.state import AgentState
from src.utils.schemas import SupervisorResponse


class SupervisorAgent:
    """Supervisor agent for routing decisions"""
    
    def __init__(self, model_name: str = settings.MODEL_NAME):
        self.model_name = model_name
        self.llm = ChatGroq(model=model_name).with_structured_output(SupervisorResponse)
    
    def classify(self, state: AgentState) -> Dict:
        """
        Classify question and route to appropriate agent
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with classification
        """
        question = state["question"]
        prompt = PromptTemplates.SUPERVISOR_PROMPT
        
        # Build messages with history
        messages = [SystemMessage(content=prompt)]
        
        # Add conversation history (last 5 messages for context)
        conversation_history = state.get("messages", [])
        if conversation_history:
            recent_history = conversation_history[-5:]
            messages.extend(recent_history)
        
        # Add current question
        messages.append(HumanMessage(content=f"Question: {question}"))
        
        response = self.llm.invoke(messages)
        
        classifier_response = response.classifier
        region_response = response.region
        
        print(f"\n{'='*50}")
        print("[Supervisor Agent] Classification")
        print(f"{'='*50}")
        print(f"Category: {classifier_response}")
        print(f"Reason: {region_response}")
        
        return {
            "region_response": region_response,
            "classifier_response": classifier_response,
            "question": question,
            "messages": [HumanMessage(content=question)],  # Add user question to messages
            "next": "overall_route"
        }
    
    @staticmethod
    def route(state: AgentState) -> str:
        """
        Route to appropriate agent based on classification
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        classifier_response = state.get("classifier_response", "no content")
        
        routing_map = {
            "business": "business",
            "research": "research",
            "technical": "technical"
        }
        
        return routing_map.get(classifier_response, "no content")
