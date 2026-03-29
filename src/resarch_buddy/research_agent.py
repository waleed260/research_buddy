"""Main Research Buddy Agent - orchestrates the complete research workflow."""

import asyncio
from typing import Any
from dataclasses import dataclass

from agents import Agent, Runner, RunConfig
from pydantic import BaseModel

from .agents import (
    create_search_agent,
    create_analysis_agent,
    create_synthesis_agent,
    run_search_phase,
    run_analysis_phase,
    run_synthesis_phase,
    save_research_to_memory,
    get_relevant_memories,
)
from .guardrails import input_guardrail, output_guardrail
from .hooks import ResearchLogger, LearningHooks, FeedbackLearningHook
from .memory import ResearchMemoryStore


@dataclass
class ResearchResult:
    """Result of a research operation."""
    topic: str
    report: str
    sources: list[str]
    key_takeaways: list[str]
    quality_score: float
    memory_hash: str
    related_memories: list[dict[str, Any]]


class ResearchBuddyAgent:
    """
    Main Research Buddy Agent that coordinates the complete research workflow.
    
    Features:
    - Multi-agent system with search, analysis, and synthesis agents
    - Input/output guardrails for safety
    - Memory for storing and retrieving research
    - Hooks for logging and learning
    - Handoffs between specialized agents
    """
    
    def __init__(self):
        self.logger = ResearchLogger()
        self.memory_store = ResearchMemoryStore()
        self.feedback_hook = FeedbackLearningHook(self.logger)
        self.learning_hooks = LearningHooks(self.logger)
        
        # Create the main coordinator agent
        self.coordinator_agent = self._create_coordinator_agent()
    
    def _create_coordinator_agent(self) -> Agent:
        """Create the main coordinator agent."""
        search_agent = create_search_agent()
        analysis_agent = create_analysis_agent()
        synthesis_agent = create_synthesis_agent()
        
        return Agent(
            name="ResearchBuddy",
            instructions="""You are Research Buddy, an expert research assistant. Your goal is to:

1. Understand the user's research topic thoroughly
2. Conduct comprehensive research using multiple sources
3. Analyze information critically
4. Synthesize findings into a clear, well-structured report
5. Learn from each research session to improve future results

WORKFLOW:
1. First, check if there's relevant memory from previous research
2. Search for information using web search, academic search, and news search
3. Analyze the found content for key findings and evidence
4. Synthesize everything into a comprehensive report
5. Save the research to memory for future learning

OUTPUT FORMAT:
- Start with a brief overview
- Use clear headings and sections
- Include key takeaways as bullet points
- List all sources used
- Note any limitations or gaps in the research

Be thorough, accurate, and cite your sources properly.""",
            model="gpt-4o",
            handoffs=[
                search_agent,
                analysis_agent,
                synthesis_agent,
            ],
            input_guardrails=[input_guardrail],
            output_guardrails=[output_guardrail],
        )
    
    async def research(
        self,
        topic: str,
        include_academic: bool = True,
        include_news: bool = True,
        depth: str = "comprehensive"  # "quick", "standard", "comprehensive"
    ) -> ResearchResult:
        """
        Conduct research on a topic.
        
        Args:
            topic: The research topic
            include_academic: Whether to include academic sources
            include_news: Whether to include recent news
            depth: Research depth level
        
        Returns:
            ResearchResult with the complete research output
        """
        self.logger.logger.info(f"Starting research on: {topic}")
        
        # Check for relevant memories
        related_memories = get_relevant_memories(topic)
        memory_context = ""
        if related_memories:
            memory_context = "\n\nPrevious research on this topic:\n"
            for mem in related_memories[:2]:
                memory_context += f"- {mem.topic}: {mem.findings[:200]}...\n"
        
        # Build the research query
        query = f"Research this topic thoroughly: {topic}"
        query += f"\n\nDepth: {depth}"
        if include_academic:
            query += "\n- Include academic sources"
        if include_news:
            query += "\n- Include recent news"
        if memory_context:
            query += memory_context
        
        # Run the phased research approach
        try:
            # Phase 1: Search
            self.logger.logger.info("Phase 1: Searching for information...")
            search_results = await run_search_phase(topic)
            
            # Phase 2: Analysis
            self.logger.logger.info("Phase 2: Analyzing findings...")
            analysis_results = await run_analysis_phase(topic, search_results)
            
            # Phase 3: Synthesis
            self.logger.logger.info("Phase 3: Synthesizing report...")
            synthesis_results = await run_synthesis_phase(
                topic, search_results, analysis_results
            )
            
            # Save to memory
            mem_hash = await save_research_to_memory(
                topic=topic,
                query=query,
                findings=synthesis_results.comprehensive_report,
                sources=list(synthesis_results.sources),
                tags=[topic, "research", depth]
            )
            
            # Prepare related memories for output
            related_mem_data = [
                {"topic": m.topic, "summary": m.findings[:100]}
                for m in related_memories[:3]
            ]
            
            self.logger.logger.info(f"Research complete! Saved to memory: {mem_hash}")
            
            return ResearchResult(
                topic=topic,
                report=synthesis_results.comprehensive_report,
                sources=list(synthesis_results.sources),
                key_takeaways=list(synthesis_results.key_takeaways),
                quality_score=synthesis_results.quality_score,
                memory_hash=mem_hash,
                related_memories=related_mem_data
            )
            
        except Exception as e:
            self.logger.log_error(topic, str(e))
            raise
    
    async def research_simple(self, topic: str) -> str:
        """
        Simple research method that runs the coordinator agent directly.
        
        Args:
            topic: The research topic
        
        Returns:
            The research report as a string
        """
        result = await Runner.run(
            self.coordinator_agent,
            f"Research this topic thoroughly and provide a comprehensive report: {topic}",
            hooks=self.learning_hooks
        )
        
        # Save to memory
        output_text = str(result.final_output)
        await save_research_to_memory(
            topic=topic,
            query=topic,
            findings=output_text,
            sources=[],
            tags=[topic, "simple_research"]
        )
        
        return output_text
    
    def record_feedback(
        self,
        topic: str,
        feedback_type: str,
        feedback_text: str,
        quality_rating: float | None = None
    ) -> None:
        """Record feedback for learning."""
        self.feedback_hook.record_feedback(
            topic, feedback_type, feedback_text, quality_rating
        )
    
    def get_learning_insights(self) -> dict[str, Any]:
        """Get insights from accumulated learning."""
        return self.feedback_hook.get_learning_patterns()
    
    def get_research_history(self, topic: str | None = None, limit: int = 10) -> list[dict]:
        """Get research history, optionally filtered by topic."""
        if topic:
            memories = self.memory_store.find_by_topic(topic, limit)
        else:
            memories = self.memory_store.get_all()[:limit]
        
        return [
            {
                "topic": m.topic,
                "timestamp": m.timestamp,
                "quality_score": m.quality_score,
                "tags": m.tags
            }
            for m in memories
        ]


# Convenience function for creating the agent
def create_research_buddy() -> ResearchBuddyAgent:
    """Create a new Research Buddy agent instance."""
    return ResearchBuddyAgent()
