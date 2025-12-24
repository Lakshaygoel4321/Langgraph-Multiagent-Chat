from langgraph.graph import StateGraph, END
from typing import Dict, Optional
from src.utils.state import AgentState
from src.routers.supervisor import SupervisorAgent
from src.agents.business_agent import BusinessAgent
from src.agents.research_agent import ResearchAgent
from src.agents.technical_agent import TechnicalAgent
from langgraph.checkpoint.memory import MemorySaver
from src.synthesis.synthesis_agents import (
    BusinessSynthesis,
    ResearchSynthesis,
    TechnicalSynthesis
)
from src.validators.validator import ValidatorAgent


class AgentWorkflow:
    """Main workflow orchestrator for the agent system"""
    
    def __init__(self):
        # Initialize all agents
        self.supervisor = SupervisorAgent()
        self.business_agent = BusinessAgent()
        self.research_agent = ResearchAgent()
        self.technical_agent = TechnicalAgent()
        self.business_synthesis = BusinessSynthesis()
        self.research_synthesis = ResearchSynthesis()
        self.technical_synthesis = TechnicalSynthesis()
        self.validator = ValidatorAgent()
        
        # Initialize memory saver
        self.memory = MemorySaver()
        
        # Build graph
        self.app = self._build_graph()
    
    def _build_graph(self):
        """
        Construct the LangGraph workflow
        
        Returns:
            Compiled graph application
        """
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("supervisor", self.supervisor.classify)
        graph.add_node("business", self.business_agent.process)
        graph.add_node("research", self.research_agent.process)
        graph.add_node("technical", self.technical_agent.process)
        graph.add_node("business_analyst", self.business_synthesis.process)
        graph.add_node("research_analyst", self.research_synthesis.process)
        graph.add_node("technical_analyst", self.technical_synthesis.process)
        graph.add_node("validator", self.validator.validate)
        
        # Set entry point
        graph.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        graph.add_conditional_edges(
            "supervisor",
            self.supervisor.route,
            {
                "business": "business",
                "research": "research",
                "technical": "technical"
            }
        )
        
        # Add edges for business path
        graph.add_edge("business", "business_analyst")
        graph.add_edge("business_analyst", "validator")
        
        # Add edges for research path
        graph.add_edge("research", "research_analyst")
        graph.add_edge("research_analyst", "validator")
        
        # Add edges for technical path
        graph.add_edge("technical", "technical_analyst")
        graph.add_edge("technical_analyst", "validator")
        
        # End at validator
        graph.add_edge("validator", END)
        
        return graph.compile(checkpointer=self.memory)
    
    def invoke(self, question: str, thread_id: str = "default") -> Dict:
        """
        Execute workflow with a question
        
        Args:
            question: User question to process
            thread_id: Unique identifier for conversation thread
            
        Returns:
            Final state after workflow execution
        """
        config = {"configurable": {"thread_id": thread_id}}
        return self.app.invoke({"question": question}, config=config)
    
    def stream(self, question: str, thread_id: str = "default"):
        """
        Stream workflow execution
        
        Args:
            question: User question to process
            thread_id: Unique identifier for conversation thread
            
        Yields:
            State updates during execution
        """
        config = {"configurable": {"thread_id": thread_id}}
        for output in self.app.stream({"question": question}, config=config):
            yield output
    
    def get_state(self, thread_id: str) -> Optional[Dict]:
        """
        Get the current state of a conversation thread
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Current state or None
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.app.get_state(config)
            return state
        except Exception as e:
            print(f"Error getting state: {e}")
            return None
    
    def get_state_history(self, thread_id: str, limit: int = 10):
        """
        Get conversation history for a thread
        
        Args:
            thread_id: Thread identifier
            limit: Maximum number of history items to return
            
        Returns:
            List of state snapshots
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            history = []
            for state in self.app.get_state_history(config):
                history.append(state)
                if len(history) >= limit:
                    break
            return history
        except Exception as e:
            print(f"Error getting state history: {e}")
            return []
