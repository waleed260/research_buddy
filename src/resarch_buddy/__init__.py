"""Research Buddy - AI-powered research assistant using OpenAI Agents SDK."""

from .research_agent import ResearchBuddyAgent, create_research_buddy
from .memory import ResearchMemory, ResearchMemoryStore
from .agents import (
    create_search_agent,
    create_analysis_agent,
    create_synthesis_agent,
    run_search_phase,
    run_analysis_phase,
    run_synthesis_phase,
)
from .tools import web_search, fetch_url_content, search_academic, search_news
from .guardrails import input_guardrail, output_guardrail
from .hooks import ResearchLogger, LearningHooks, FeedbackLearningHook


def main():
    """Main entry point for the CLI."""
    from .cli import cli
    cli()


__all__ = [
    # Main agent
    "ResearchBuddyAgent",
    "create_research_buddy",
    
    # Memory
    "ResearchMemory",
    "ResearchMemoryStore",
    
    # Subagents
    "create_search_agent",
    "create_analysis_agent",
    "create_synthesis_agent",
    "run_search_phase",
    "run_analysis_phase",
    "run_synthesis_phase",
    
    # Tools
    "web_search",
    "fetch_url_content",
    "search_academic",
    "search_news",
    
    # Guardrails
    "input_guardrail",
    "output_guardrail",
    
    # Hooks
    "ResearchLogger",
    "LearningHooks",
    "FeedbackLearningHook",
    
    # CLI
    "main",
]
