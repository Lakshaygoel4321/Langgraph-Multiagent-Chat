from typing import Dict
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.utils.state import AgentState
from config.prompts import PromptTemplates


class BusinessAgent(BaseAgent):
    """Business domain expert agent"""
    
    def get_prompt(self) -> str:
        return PromptTemplates.BUSINESS_AGENT_PROMPT
    
    def process(self, state: AgentState) -> Dict:
        """
        Generate business-focused answer with conversation history
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with business response
        """
        question = state["question"]
        prompt = self.get_prompt()
        
        # Get conversation history from state
        conversation_history = state.get("messages", [])
        
        # Invoke LLM with history
        response_content = self.invoke_llm(prompt, question, conversation_history)
        self.log_workflow("Business Agent", response_content)
        
        return {
            "business_generate": response_content,
            "messages": [AIMessage(content=response_content)],  # Append to messages
            "next": "business_analyst",
            "question": question
        }
