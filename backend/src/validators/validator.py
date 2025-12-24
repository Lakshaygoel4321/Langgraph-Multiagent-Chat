from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config.settings import settings
from config.prompts import PromptTemplates
from src.utils.state import AgentState
from src.utils.schemas import ConfidenceScore


class ValidatorAgent:
    """Validator agent for quality assurance"""
    
    def __init__(self, model_name: str = settings.MODEL_NAME):
        self.model_name = model_name
        self.llm = ChatGroq(model=model_name).with_structured_output(ConfidenceScore)
    
    def validate(self, state: AgentState) -> Dict:
        """
        Validate generated answer quality
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validation score
        """
        question = state["question"]
        
        # Collect result from appropriate analyst
        result = ""
        if state.get("technical_analyst", ""):
            result = state["technical_analyst"]
        elif state.get("research_analyst", ""):
            result = state["research_analyst"]
        elif state.get("business_analyst", ""):
            result = state["business_analyst"]
        
        prompt = PromptTemplates.VALIDATOR_PROMPT
        
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=prompt),
            HumanMessage(content=f"question: {question}\nGenerated Answer: {result}")
        ])
        
        system_prompt = chat_prompt.format_messages(
            question=question,
            result=result
        )
        
        response = self.llm.invoke(system_prompt)
        
        print(f"\n{'='*50}")
        print("[Validator Agent] Confidence Score")
        print(f"{'='*50}")
        print(f"Score: {response.range}/10")
        
        return {
            "validator_score": response.range,
            "final_data": result,
            "question": question,
            "messages": AIMessage(content=response.range)
        }
