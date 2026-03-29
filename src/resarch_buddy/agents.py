"""Subagents for specialized research tasks."""

from typing import Any
from agents import Agent, Runner, handoff
from pydantic import BaseModel

from .tools import web_search, fetch_url_content, search_academic, search_news
from .memory import ResearchMemory, ResearchMemoryStore
from .hooks import ResearchLogger


class SearchOutput(BaseModel):
    """Output from the search agent."""
    query: str
    search_results: list[dict[str, Any]]
    relevant_urls: list[str]
    summary: str


class AnalysisOutput(BaseModel):
    """Output from the analysis agent."""
    topic: str
    key_findings: list[str]
    evidence: list[dict[str, str]]
    confidence_score: float
    gaps: list[str]


class SynthesisOutput(BaseModel):
    """Output from the synthesis agent."""
    topic: str
    comprehensive_report: str
    sources: list[str]
    key_takeaways: list[str]
    quality_score: float


# Create memory store and logger as shared resources
_memory_store = ResearchMemoryStore()
_logger = ResearchLogger()


def create_search_agent() -> Agent:
    """Create the search agent responsible for finding information."""
    return Agent(
        name="SearchAgent",
        instructions="""You are a specialized Search Agent for research. Your role is to:
1. Search the web for information on the given topic
2. Find relevant URLs and sources
3. Provide a brief summary of what was found
4. Identify the most promising sources for deeper analysis

Be thorough and use multiple search strategies (general search, academic search, news search) 
when appropriate. Always return structured results with URLs for further analysis.""",
        model="gpt-4o",
        tools=[web_search, search_academic, search_news],
        output_type=SearchOutput,
    )


def create_analysis_agent() -> Agent:
    """Create the analysis agent responsible for analyzing found content."""
    return Agent(
        name="AnalysisAgent",
        instructions="""You are a specialized Analysis Agent for research. Your role is to:
1. Analyze the search results and content provided
2. Extract key findings and evidence
3. Assess the confidence level of the information
4. Identify any gaps or areas needing more research
5. Cross-reference information from multiple sources

Be critical and analytical. Distinguish between facts, opinions, and speculation.
Note the quality and reliability of sources.""",
        model="gpt-4o",
        tools=[fetch_url_content],
        output_type=AnalysisOutput,
    )


def create_synthesis_agent() -> Agent:
    """Create the synthesis agent responsible for creating final reports."""
    return Agent(
        name="SynthesisAgent",
        instructions="""You are a specialized Synthesis Agent for research. Your role is to:
1. Combine all findings into a comprehensive report
2. Structure the information logically
3. Cite all sources properly
4. Provide key takeaways for the user
5. Assess the overall quality of the research

Create well-structured, readable reports with:
- Clear headings and sections
- Bullet points for key information
- Proper source attribution
- Actionable insights

Always aim for clarity, accuracy, and completeness.""",
        model="gpt-4o",
        output_type=SynthesisOutput,
    )


def create_researcher_agent() -> Agent:
    """Create the main researcher agent that coordinates subagents."""
    search_agent = create_search_agent()
    analysis_agent = create_analysis_agent()
    synthesis_agent = create_synthesis_agent()
    
    return Agent(
        name="ResearcherAgent",
        instructions="""You are the main Research Coordinator Agent. Your role is to:
1. Understand the user's research topic and requirements
2. Coordinate the search, analysis, and synthesis agents
3. Ensure comprehensive coverage of the topic
4. Store research results in memory for future learning
5. Provide the final research output to the user

Workflow:
1. First, use the SearchAgent to find information
2. Then, use the AnalysisAgent to analyze the findings
3. Finally, use the SynthesisAgent to create the final report
4. Save the research to memory for future reference

Be methodical and thorough. Ensure each step builds on the previous one.""",
        model="gpt-4o",
        handoffs=[
            handoff(search_agent),
            handoff(analysis_agent),
            handoff(synthesis_agent),
        ],
    )


async def run_search_phase(topic: str, specific_questions: list[str] | None = None) -> SearchOutput:
    """Run the search phase of research."""
    agent = create_search_agent()
    
    query = f"Research the following topic thoroughly: {topic}"
    if specific_questions:
        query += f"\n\nSpecific questions to answer:\n" + "\n".join(f"- {q}" for q in specific_questions)
    
    result = await Runner.run(agent, query)
    return result.final_output


async def run_analysis_phase(
    topic: str,
    search_results: SearchOutput,
    urls_to_analyze: list[str] | None = None
) -> AnalysisOutput:
    """Run the analysis phase of research."""
    agent = create_analysis_agent()
    
    # Prepare context from search results
    context = f"""Topic: {topic}

Search Results Summary:
{search_results.summary}

Relevant URLs found:
{chr(10).join(search_results.relevant_urls)}
"""
    
    if urls_to_analyze:
        context += f"\nPlease analyze these specific URLs:\n" + "\n".join(urls_to_analyze)
    
    context += "\n\nAnalyze the available information and extract key findings."
    
    result = await Runner.run(agent, context)
    return result.final_output


async def run_synthesis_phase(
    topic: str,
    search_results: SearchOutput,
    analysis_results: AnalysisOutput
) -> SynthesisOutput:
    """Run the synthesis phase of research."""
    agent = create_synthesis_agent()
    
    context = f"""Topic: {topic}

Search Results:
{search_results.summary}

Key Findings from Analysis:
{chr(10).join(f"- {f}" for f in analysis_results.key_findings)}

Evidence:
{chr(10).join(f"- {e['source']}: {e['finding']}" for e in analysis_results.evidence)}

Confidence Score: {analysis_results.confidence_score}

Identified Gaps:
{chr(10).join(f"- {g}" for g in analysis_results.gaps) if analysis_results.gaps else "None identified"}

---

Create a comprehensive research report based on the above information.
"""
    
    result = await Runner.run(agent, context)
    return result.final_output


async def save_research_to_memory(
    topic: str,
    query: str,
    findings: str,
    sources: list[str],
    tags: list[str] | None = None
) -> str:
    """Save research results to memory."""
    memory = ResearchMemory(
        topic=topic,
        query=query,
        findings=findings,
        sources=sources,
        tags=tags or [],
        quality_score=0.8,
        learned_from=False
    )
    mem_hash = _memory_store.add(memory)
    _logger.logger.info(f"Saved research to memory: {topic[:50]}... (hash: {mem_hash})")
    return mem_hash


def get_relevant_memories(topic: str) -> list[ResearchMemory]:
    """Get relevant memories for a topic."""
    return _memory_store.find_similar(topic)
