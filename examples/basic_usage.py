#!/usr/bin/env python3
"""Example usage of Research Buddy agent."""

import asyncio
from resarch_buddy import create_research_buddy


async def main():
    # Create the research buddy agent
    agent = create_research_buddy()
    
    # Example 1: Simple research
    print("=" * 60)
    print("Example 1: Simple Research")
    print("=" * 60)
    
    topic = "Latest developments in quantum computing"
    print(f"\nResearching: {topic}\n")
    
    # Run simple research
    result = await agent.research_simple(topic)
    print(result)
    
    # Example 2: Full research with options
    print("\n" + "=" * 60)
    print("Example 2: Comprehensive Research")
    print("=" * 60)
    
    research_result = await agent.research(
        topic="Benefits and risks of artificial intelligence",
        include_academic=True,
        include_news=True,
        depth="comprehensive"
    )
    
    print(f"\n📊 Report:\n{research_result.report}")
    print(f"\n📌 Key Takeaways:")
    for takeaway in research_result.key_takeaways:
        print(f"  • {takeaway}")
    print(f"\n📚 Sources: {len(research_result.sources)} found")
    print(f"✅ Quality Score: {research_result.quality_score:.2f}")
    print(f"💾 Memory Hash: {research_result.memory_hash}")
    
    # Example 3: View research history
    print("\n" + "=" * 60)
    print("Example 3: Research History")
    print("=" * 60)
    
    history = agent.get_research_history(limit=5)
    for item in history:
        print(f"  • {item['topic']} (Quality: {item['quality_score']:.2f})")
    

