from typing import Dict
from src.synthesis.base_synthesis import BaseSynthesis
from src.utils.state import AgentState


class BusinessSynthesis(BaseSynthesis):
    """Synthesis agent for business domain"""
    
    def get_state_key(self) -> str:
        return "business_generate"
    
    def get_output_key(self) -> str:
        return "business_analyst"
    
    def process(self, state: AgentState) -> Dict:
        return self.synthesize(state)


class ResearchSynthesis(BaseSynthesis):
    """Synthesis agent for research domain"""
    
    def get_state_key(self) -> str:
        return "research_generate"
    
    def get_output_key(self) -> str:
        return "research_analyst"
    
    def process(self, state: AgentState) -> Dict:
        return self.synthesize(state)


class TechnicalSynthesis(BaseSynthesis):
    """Synthesis agent for technical domain"""
    
    def get_state_key(self) -> str:
        return "technical_generate"
    
    def get_output_key(self) -> str:
        return "technical_analyst"
    
    def process(self, state: AgentState) -> Dict:
        return self.synthesize(state)
