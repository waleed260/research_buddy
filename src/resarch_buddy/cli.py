"""CLI interface for Research Buddy."""

import asyncio
import click

from .research_agent import create_research_buddy
from .memory import ResearchMemoryStore


@click.group()
def cli():
    """Research Buddy - AI-powered research assistant."""
    pass


@cli.command()
@click.argument("topic")
@click.option(
    "--depth",
    type=click.Choice(["quick", "standard", "comprehensive"]),
    default="comprehensive",
    help="Research depth level"
)
@click.option(
    "--no-academic",
    is_flag=True,
    help="Exclude academic sources"
)
@click.option(
    "--no-news",
    is_flag=True,
    help="Exclude recent news"
)
@click.option(
    "--output-file",
    type=click.Path(),
    help="Save report to file"
)
def research(topic: str, depth: str, no_academic: bool, no_news: bool, output_file: str | None):
    """Research a topic and get a comprehensive report."""
    agent = create_research_buddy()
    
    click.echo(f"\n🔍 Starting research on: {topic}")
    click.echo(f"   Depth: {depth}")
    click.echo(f"   Academic sources: {'No' if no_academic else 'Yes'}")
    click.echo(f"   News sources: {'No' if no_news else 'Yes'}")
    click.echo("-" * 50)
    
    try:
        result = asyncio.run(agent.research(
            topic=topic,
            include_academic=not no_academic,
            include_news=not no_news,
            depth=depth
        ))
        
        click.echo("\n" + "=" * 60)
        click.echo("📊 RESEARCH REPORT")
        click.echo("=" * 60)
        click.echo(result.report)
        
        click.echo("\n" + "-" * 50)
        click.echo("📌 KEY TAKEAWAYS")
        click.echo("-" * 50)
        for takeaway in result.key_takeaways:
            click.echo(f"  • {takeaway}")
        
        if result.sources:
            click.echo("\n" + "-" * 50)
            click.echo("📚 SOURCES")
            click.echo("-" * 50)
            for source in result.sources[:10]:
                click.echo(f"  • {source}")
        
        click.echo("\n" + "-" * 50)
        click.echo(f"✅ Quality Score: {result.quality_score:.2f}")
        click.echo(f"💾 Saved to memory: {result.memory_hash}")
        
        if result.related_memories:
            click.echo("\n📖 Related previous research:")
            for mem in result.related_memories:
                click.echo(f"  • {mem['topic']}: {mem['summary']}...")
        
        if output_file:
            with open(output_file, "w") as f:
                f.write(result.report)
                f.write("\n\n---\n\n")
                f.write("KEY TAKEAWAYS:\n")
                for takeaway in result.key_takeaways:
                    f.write(f"• {takeaway}\n")
                f.write("\nSOURCES:\n")
                for source in result.sources:
                    f.write(f"{source}\n")
            click.echo(f"\n💾 Report saved to: {output_file}")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("topic", required=False)
@click.option("--limit", default=10, help="Number of results to show")
def history(topic: str | None, limit: int):
    """Show research history."""
    agent = create_research_buddy()
    
    click.echo("\n📜 RESEARCH HISTORY")
    click.echo("=" * 50)
    
    history_items = agent.get_research_history(topic if topic else None, limit)
    
    if not history_items:
        click.echo("No research history found.")
        return
    
    for item in history_items:
        click.echo(f"\n📌 {item['topic']}")
        click.echo(f"   Date: {item['timestamp']}")
        click.echo(f"   Quality: {item['quality_score']:.2f}")
        if item['tags']:
            click.echo(f"   Tags: {', '.join(item['tags'])}")


@cli.command()
@click.argument("topic")
@click.option("--rating", type=float, help="Quality rating (0.0-1.0)")
@click.option("--type", "feedback_type", default="general", 
              help="Type of feedback")
@click.option("--comment", default="", help="Feedback comment")
def feedback(topic: str, rating: float | None, feedback_type: str, comment: str):
    """Provide feedback on research results."""
    agent = create_research_buddy()
    
    agent.record_feedback(
        topic=topic,
        feedback_type=feedback_type,
        feedback_text=comment,
        quality_rating=rating
    )
    
    click.echo("✅ Feedback recorded! This will help improve future research.")


@cli.command()
def insights():
    """Show learning insights from past research."""
    agent = create_research_buddy()
    
    insights = agent.get_learning_insights()
    
    click.echo("\n🧠 LEARNING INSIGHTS")
    click.echo("=" * 50)
    click.echo(f"Total feedback received: {insights.get('total_feedback', 0)}")
    click.echo(f"Average quality rating: {insights.get('avg_quality', 0):.2f}")
    
    patterns = insights.get('patterns', {})
    if patterns:
        click.echo("\nFeedback types:")
        for ftype, count in patterns.items():
            click.echo(f"  • {ftype}: {count}")


@cli.command()
@click.argument("query")
@click.option("--limit", default=5, help="Number of results")
def search_memory(query: str, limit: int):
    """Search through saved research memories."""
    store = ResearchMemoryStore()
    
    memories = store.find_similar(query, limit)
    
    click.echo(f"\n🔍 SEARCH RESULTS for: {query}")
    click.echo("=" * 50)
    
    if not memories:
        click.echo("No matching memories found.")
        return
    
    for mem in memories:
        click.echo(f"\n📌 {mem.topic}")
        click.echo(f"   Date: {mem.timestamp}")
        click.echo(f"   Quality: {mem.quality_score:.2f}")
        click.echo(f"   Preview: {mem.findings[:150]}...")
        if mem.tags:
            click.echo(f"   Tags: {', '.join(mem.tags)}")

@cli.command()
def clear():
    """Clear all research history and memories."""
    if click.confirm("Are you sure you want to clear all research history?"):
        store = ResearchMemoryStore()
        # Clear by reinitializing the storage file
        import json
        with open(store.storage_path, "w") as f:
            json.dump([], f)
        click.echo("✅ Research history cleared.")
    else:
        click.echo("Operation cancelled.")


@cli.command()
def version():
    """Show version information."""
    click.echo("Research Buddy v0.1.0")
    click.echo("Powered by OpenAI Agents SDK")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()

