"""Research tools for the agent."""

from typing import Any
from agents import function_tool
from duckduckgo_search import DDGS
import httpx


@function_tool
async def web_search(query: str, num_results: int = 10) -> dict[str, Any]:
    """
    Search the web for information on a given query.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 10)
    
    Returns:
        Dictionary with search results including titles, URLs, and snippets
    """
    try:
        results = []
        ddgs = DDGS()
        for result in ddgs.text(query, max_results=num_results):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@function_tool
async def fetch_url_content(url: str, max_length: int = 10000) -> dict[str, Any]:
    """
    Fetch and extract content from a URL.
    
    Args:
        url: The URL to fetch
        max_length: Maximum characters to return (default: 10000)
    
    Returns:
        Dictionary with the page content
    """
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0
        ) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Simple text extraction (in production, use proper HTML parser)
            content = response.text[:max_length]
            # Remove excessive whitespace
            content = " ".join(content.split())
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "length": len(content)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


@function_tool
async def search_academic(query: str, num_results: int = 5) -> dict[str, Any]:
    """
    Search for academic papers and scholarly articles.
    
    Args:
        query: The academic search query
        num_results: Number of results to return (default: 5)
    
    Returns:
        Dictionary with academic search results
    """
    try:
        # Use DuckDuckGo with academic-focused query
        academic_query = f"{query} site:arxiv.org OR site:pubmed.gov OR site:scholar.google.com"
        results = []
        ddgs = DDGS()
        for result in ddgs.text(academic_query, max_results=num_results):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "type": "academic"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@function_tool
async def search_news(query: str, num_results: int = 5) -> dict[str, Any]:
    """
    Search for recent news articles on a topic.
    
    Args:
        query: The news search query
        num_results: Number of results to return (default: 5)
    
    Returns:
        Dictionary with news search results
    """
    try:
        results = []
        ddgs = DDGS()
        for result in ddgs.news(query, max_results=num_results):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "source": result.get("source", ""),
                "date": result.get("date", ""),
                "snippet": result.get("body", "")
            })
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "type": "news"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }
