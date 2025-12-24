from typing import Dict
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.utils.state import AgentState
from config.prompts import PromptTemplates


class ResearchAgent(BaseAgent):
    """Research domain expert agent"""
    
    def get_prompt(self) -> str:
        return PromptTemplates.RESEARCH_AGENT_PROMPT
    
    def process(self, state: AgentState) -> Dict:
        """
        Generate research-focused answer with conversation history
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with research response
        """
        question = state.get("question", "No content")
        prompt = self.get_prompt()
        
        # Get conversation history from state
        conversation_history = state.get("messages", [])
        
        # Invoke LLM with history
        response_content = self.invoke_llm(prompt, question, conversation_history)
        self.log_workflow("Research Agent", response_content)
        
        return {
            "research_generate": response_content,
            "messages": [AIMessage(content=response_content)],  # Append to messages
            "next": "research_analyst",
            "question": question
        }
