from abc import ABC, abstractmethod
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from config.settings import settings


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, model_name: str = settings.MODEL_NAME):
        self.model_name = model_name
        self.llm = ChatGroq(model=model_name)
    
    @abstractmethod
    def get_prompt(self) -> str:
        """Return the prompt template for this agent"""
        pass
    
    @abstractmethod
    def process(self, state: Dict) -> Dict:
        """Process the state and return updated state"""
        pass
    
    def invoke_llm(self, prompt: str, question: str, conversation_history: List[BaseMessage] = None) -> str:
        """
        Common method to invoke LLM with prompt and conversation history
        
        Args:
            prompt: System prompt template
            question: User question
            conversation_history: Previous messages in conversation
            
        Returns:
            LLM response content
        """
        # Build message list with history
        messages = [SystemMessage(content=prompt)]
        
        # Add conversation history if available (last 10 messages to avoid token limits)
        if conversation_history:
            # Take last 10 messages to keep context manageable
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            messages.extend(recent_history)
        
        # Add current question
        messages.append(HumanMessage(content=f"question: {question}"))
        
        response = self.llm.invoke(messages)
        
        return response.content
    
    def log_workflow(self, agent_name: str, content: str):
        """Log workflow information"""
        print(f"\n{'='*50}")
        print(f"[{agent_name}] Workflow")
        print(f"{'='*50}")
        print(f"{content[:200]}..." if len(content) > 200 else content)
