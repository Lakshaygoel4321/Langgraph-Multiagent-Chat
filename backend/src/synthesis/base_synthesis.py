from abc import ABC, abstractmethod
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config.settings import settings
from config.prompts import PromptTemplates
from src.utils.tools import search_tools


class BaseSynthesis(ABC):
    """Base class for synthesis agents"""
    
    def __init__(self, model_name: str = settings.MODEL_NAME):
        self.model_name = model_name
        self.llm = ChatGroq(model=model_name)
        self.search_tools = search_tools
    
    @abstractmethod
    def get_state_key(self) -> str:
        """Return the state key for generated content"""
        pass
    
    @abstractmethod
    def get_output_key(self) -> str:
        """Return the state key for synthesis output"""
        pass
    
    def synthesize(self, state: Dict) -> Dict:
        """
        Synthesize information from agent and web search
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with synthesized response
        """
        question = state["question"]
        agent_content = state.get(self.get_state_key(), "No content")
        
        # Perform web search
        web_search_content = self.search_tools.search(question)
        
        # Create synthesis prompt
        prompt = PromptTemplates.SYNTHESIS_PROMPT
        
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=prompt),
            HumanMessage(
                content=f"question: {question}\n"
                       f"web_search_information: {web_search_content}\n"
                       f"agent_generate: {agent_content}"
            )
        ])
        
        final_prompt = chat_prompt.format_messages(
            web_search_content=web_search_content,
            question=question,
            agent_generate=agent_content
        )
        
        response = self.llm.invoke(final_prompt)
        
        print(f"\n{'='*50}")
        print(f"[{self.get_output_key()} Synthesis]")
        print(f"{'='*50}")
        print(f"{response.content[:200]}..." if len(response.content) > 200 else response.content)
        
        return {
            "messages": AIMessage(content=response.content),
            self.get_output_key(): response.content,
            "next": "validator",
            "question": question
        }
