from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import settings
from typing import Optional


class SearchTools:
    """External search tools wrapper"""
    
    def __init__(self):
        self.tavily = TavilySearchResults(
            max_results=settings.TAVILY_MAX_RESULTS
        )
    
    def search(self, question: str) -> Optional[str]:
        """
        Perform web search using Tavily
        
        Args:
            question: Search query
            
        Returns:
            Search results or None if error
        """
        try:
            print(f"\n[Tavily Search] Searching for: {question}")
            response = self.tavily.invoke(question)
            return response
        except Exception as e:
            print(f"[Tavily Search Error]: {e}")
            return None


# Singleton instance
search_tools = SearchTools()
