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
        # Example 4: Provide feedback (for learning)
    print("\n" + "=" * 60)
    print("Example 4: Providing Feedback")
    print("=" * 60)
    
    agent.record_feedback(
        topic="Benefits and risks of artificial intelligence",
        feedback_type="quality",
        feedback_text="Great comprehensive coverage of the topic",
        quality_rating=0.9
    )
    print("✅ Feedback recorded!")
    
    # Example 5: Get learning insights
    print("\n" + "=" * 60)
    print("Example 5: Learning Insights")
    print("=" * 60)
    
    insights = agent.get_learning_insights()
    print(f"Total feedback: {insights.get('total_feedback', 0)}")
    print(f"Average quality: {insights.get('avg_quality', 0):.2f}")


if __name__ == "__main__":
    asyncio.run(main())

