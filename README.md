# Research Buddy 🤖📚

> **AI-powered research assistant built with the OpenAI Agents SDK**

Research Buddy automates comprehensive research using a multi-agent system that searches, analyzes, and synthesizes information from web, academic, and news sources. It learns from past research and user feedback to continuously improve.

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

- **🤖 Multi-Agent System** — Specialized agents for search, analysis, and synthesis with automatic handoffs
- **🔍 Comprehensive Search** — Web search, academic papers, and recent news sources
- **🧠 Persistent Memory** — Stores all research sessions with similarity-based retrieval
- **🛡️ Safety Guardrails** — Input/output validation with harmful content detection
- **📊 Learning System** — Improves from user feedback with pattern analysis
- **📝 Structured Reports** — Well-organized outputs with citations and key takeaways
- **💻 CLI Interface** — Full-featured command-line tool for all operations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI / API Layer                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ResearchBuddyAgent (Coordinator)                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Orchestrates workflow │ Manages memory │ Applies guardrails│    │
│  └─────────────────────────────────────────────────────────────┘    │
│         │                          │                          │      │
│         ▼                          ▼                          ▼      │
│  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐│
│  │ SearchAgent  │─────────▶│ AnalysisAgent│─────────▶│SynthesisAgent││
│  │ • web_search │          │ • fetch_url  │          │ • Report     ││
│  │ • academic   │          │ • Analyze    │          │ • Structure  ││
│  │ • news       │          │ • Evidence   │          │ • Takeaways  ││
│  └──────────────┘          └──────────────┘          └──────────────┘│
└─────────────────────────────────────────────────────────────────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│    TOOLS      │          │   MEMORY      │          │  GUARDRAILS   │
│ • web_search  │          │ • JSON store  │          │ • Input check │
│ • fetch_url   │          │ • Similarity  │          │ • Output check│
│ • academic    │          │ • Quality     │          │ • Safety      │
│ • news        │          │ • Tags        │          │ • Quality     │
└───────────────┘          └───────────────┘          └───────────────┘
                                    │
                                    ▼
                          ┌───────────────┐
                          │    HOOKS      │
                          │ • Logging     │
                          │ • Learning    │
                          │ • Feedback    │
                          └───────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- OpenAI API key

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd research_buddy

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Set API Key

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
```

---

## 🚀 Usage

### CLI Commands

#### Research a Topic

```bash
# Basic research (comprehensive depth)
resarch-buddy research "Climate change impacts on coral reefs"

# Quick research
resarch-buddy research "Quantum computing basics" --depth quick

# Standard depth
resarch-buddy research "Machine learning" --depth standard

# Exclude specific sources
resarch-buddy research "AI in healthcare" --no-academic
resarch-buddy research "Tech news" --no-news

# Save report to file
resarch-buddy research "Renewable energy" --output-file report.md

# Full options
resarch-buddy research "CRISPR gene editing" \
    --depth comprehensive \
    --no-news \
    --output-file crispr_report.md
```

#### View History & Search Memory

```bash
# View all research history
resarch-buddy history

# View history for specific topic
resarch-buddy history "artificial intelligence"

# Limit results
resarch-buddy history --limit 5

# Search through saved memories
resarch-buddy search-memory "machine learning"

# Search with limit
resarch-buddy search-memory "neural networks" --limit 3
```

#### Provide Feedback (Learning)

```bash
# Rate research quality
resarch-buddy feedback "Climate change" --rating 0.9

# Feedback with comment
resarch-buddy feedback "AI ethics" \
    --type quality \
    --comment "Excellent coverage of bias issues"

# Full feedback options
resarch-buddy feedback "Quantum computing" \
    --rating 0.85 \
    --type accuracy \
    --comment "Good but needs more recent sources"

# View learning insights
resarch-buddy insights
```

#### Management

```bash
# Clear all research history
resarch-buddy clear

# Show version
resarch-buddy version
```

---

### Programmatic Usage

#### Simple Research

```python
import asyncio
from resarch_buddy import create_research_buddy

async def main():
    agent = create_research_buddy()
    
    # Simple research - returns report as string
    report = await agent.research_simple(
        "Latest developments in quantum computing"
    )
    print(report)

asyncio.run(main())
```

#### Comprehensive Research

```python
import asyncio
from resarch_buddy import create_research_buddy

async def main():
    agent = create_research_buddy()
    
    # Full research with all options
    result = await agent.research(
        topic="Benefits and risks of artificial intelligence",
        include_academic=True,
        include_news=True,
        depth="comprehensive"  # "quick", "standard", "comprehensive"
    )
    
    # Access structured results
    print(f"📊 Report:\n{result.report}")
    print(f"\n📌 Key Takeaways:")
    for takeaway in result.key_takeaways:
        print(f"  • {takeaway}")
    print(f"\n📚 Sources: {len(result.sources)} found")
    print(f"✅ Quality Score: {result.quality_score:.2f}")
    print(f"💾 Memory Hash: {result.memory_hash}")
    
    # Access related memories from past research
    if result.related_memories:
        print(f"\n📖 Related Previous Research:")
        for mem in result.related_memories:
            print(f"  • {mem['topic']}: {mem['summary']}...")

asyncio.run(main())
```

#### Research History & Feedback

```python
from resarch_buddy import create_research_buddy

agent = create_research_buddy()

# Get research history
history = agent.get_research_history(limit=10)
for item in history:
    print(f"Topic: {item['topic']}, Quality: {item['quality_score']}")

# Get history filtered by topic
ai_history = agent.get_research_history(topic="artificial intelligence")

# Record feedback for learning
agent.record_feedback(
    topic="Benefits and risks of artificial intelligence",
    feedback_type="quality",
    feedback_text="Great comprehensive coverage of both pros and cons",
    quality_rating=0.9
)

# Get learning insights
insights = agent.get_learning_insights()
print(f"Total feedback: {insights['total_feedback']}")
print(f"Average quality: {insights['avg_quality']:.2f}")
print(f"Feedback patterns: {insights['patterns']}")
```

#### Using Individual Components

```python
import asyncio
from resarch_buddy import (
    create_search_agent,
    create_analysis_agent,
    create_synthesis_agent,
    run_search_phase,
    run_analysis_phase,
    run_synthesis_phase,
    ResearchMemoryStore,
    web_search,
    search_academic,
    search_news,
)

async def custom_workflow():
    topic = "Machine learning in healthcare"
    
    # Run individual research phases
    search_results = await run_search_phase(topic)
    analysis_results = await run_analysis_phase(topic, search_results)
    synthesis_results = await run_synthesis_phase(
        topic, search_results, analysis_results
    )
    
    # Use tools directly
    web_results = await web_search("Python programming", num_results=5)
    academic_results = await search_academic("deep learning", num_results=3)
    news_results = await search_news("AI regulation", num_results=5)
    
    # Access memory store directly
    memory_store = ResearchMemoryStore()
    similar = memory_store.find_similar("machine learning", limit=5)
    by_topic = memory_store.find_by_topic("healthcare", limit=3)
    
    # Update quality score for a memory
    memory_store.update_quality(mem_hash="abc123", score=0.95)

asyncio.run(custom_workflow())
```

---

## 🔄 Research Workflow

Research Buddy follows a three-phase workflow:

### Phase 1: Search 🔍
The **SearchAgent** discovers information using:
- **Web Search** — General information from across the internet
- **Academic Search** — Scholarly articles and papers
- **News Search** — Recent news and developments

**Output:** `SearchOutput` with query, results, relevant URLs, and summary

### Phase 2: Analysis 🧪
The **AnalysisAgent** critically examines findings:
- Extracts key findings and evidence
- Assesses confidence levels
- Identifies gaps needing more research
- Cross-references multiple sources

**Output:** `AnalysisOutput` with findings, evidence, confidence score, and gaps

### Phase 3: Synthesis 📝
The **SynthesisAgent** creates the final report:
- Combines all findings logically
- Structures with clear headings
- Cites all sources properly
- Provides actionable key takeaways

**Output:** `SynthesisOutput` with comprehensive report, sources, and quality score

---

## 📁 Project Structure

```
research_buddy/
├── pyproject.toml              # Project configuration & dependencies
├── README.md                   # This documentation
├── uv.lock                     # Dependency lock file
├── research_memories.json      # Persistent memory (auto-generated)
├── research_logs.jsonl         # Activity logs (auto-generated)
├── feedback_logs.jsonl         # Feedback logs (auto-generated)
│
├── examples/
│   └── basic_usage.py          # Example usage code
│
├── src/
│   └── resarch_buddy/
│       ├── __init__.py         # Package exports
│       ├── research_agent.py   # Main ResearchBuddyAgent class
│       ├── agents.py           # Subagent definitions & phase functions
│       ├── tools.py            # Search and fetch tools
│       ├── memory.py           # Memory storage system
│       ├── guardrails.py       # Input/output validation
│       ├── hooks.py            # Logging and learning hooks
│       └── cli.py              # CLI interface
│
└── .venv/                      # Virtual environment
```

---

## 📚 API Reference

### Main Class: `ResearchBuddyAgent`

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `research()` | `topic`, `include_academic`, `include_news`, `depth` | `ResearchResult` | Full phased research |
| `research_simple()` | `topic` | `str` | Simple one-call research |
| `record_feedback()` | `topic`, `feedback_type`, `feedback_text`, `quality_rating` | `None` | Record user feedback |
| `get_learning_insights()` | — | `dict` | Get learning patterns |
| `get_research_history()` | `topic`, `limit` | `list[dict]` | Get research history |

### Research Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `topic` | `str` | Research topic |
| `report` | `str` | Comprehensive report |
| `sources` | `list[str]` | Source URLs |
| `key_takeaways` | `list[str]` | Main insights |
| `quality_score` | `float` | Quality rating (0-1) |
| `memory_hash` | `str` | Unique memory identifier |
| `related_memories` | `list[dict]` | Related past research |

### Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `web_search()` | `query`, `num_results=10` | Search the web |
| `fetch_url_content()` | `url`, `max_length=10000` | Fetch webpage content |
| `search_academic()` | `query`, `num_results=5` | Search academic papers |
| `search_news()` | `query`, `num_results=5` | Search news articles |

### Memory Store

| Method | Parameters | Description |
|--------|------------|-------------|
| `add()` | `memory` | Add memory, return hash |
| `find_by_topic()` | `topic`, `limit=5` | Find by topic |
| `find_similar()` | `query`, `limit=3` | Keyword similarity search |
| `get_all()` | — | Get all memories |
| `update_quality()` | `mem_hash`, `score` | Update quality score |

---

## ⚙️ Configuration

### Research Depth Levels

| Level | Description | Best For |
|-------|-------------|----------|
| `quick` | Fast, surface-level | Quick facts, definitions |
| `standard` | Balanced depth/speed | General research |
| `comprehensive` | Thorough, multi-source | In-depth analysis |

### Source Options

| Option | CLI Flag | API Parameter | Default |
|--------|----------|---------------|---------|
| Academic Sources | `--no-academic` | `include_academic` | `True` |
| News Sources | `--no-news` | `include_news` | `True` |

### Storage Locations

| File | Default Location | Format |
|------|------------------|--------|
| Memories | `research_memories.json` | JSON |
| Logs | `research_logs.jsonl` | JSONL |
| Feedback | `feedback_logs.jsonl` | JSONL |

### Model Configuration

All agents use `gpt-4o` by default. Modify in `agents.py`:

```python
return Agent(
    name="SearchAgent",
    model="gpt-4o",  # Change here
    ...
)
```

---

## 🛡️ Guardrails

Research Buddy includes safety and quality checks:

### Input Validation
- ✅ Empty input detection
- ✅ Length limits (max 2000 chars)
- ✅ Harmful content detection (regex patterns)
- ✅ Topic safety assessment

### Output Validation
- ✅ Empty output detection
- ✅ Harmful content filtering
- ✅ Quality scoring (structure, length, formatting)
- ✅ Tripwire mechanism for blocking unsafe content

---

## 🧠 Learning System

Research Buddy learns from every interaction:

### Memory-Based Learning
- All research sessions stored persistently
- Similar topic retrieval for context
- Quality scoring for each session
- Tag-based organization

### Feedback-Based Learning
- User ratings (0.0-1.0)
- Feedback categories (quality, accuracy, completeness, etc.)
- Pattern analysis from accumulated feedback
- Average quality tracking

### View Learning Insights

```bash
resarch-buddy insights
```

Output example:
```
🧠 LEARNING INSIGHTS
==================================================
Total feedback received: 15
Average quality rating: 0.87

Feedback types:
  • quality: 8
  • accuracy: 4
  • completeness: 3
```

---

## 📊 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai-agents` | >=0.13.2 | Multi-agent orchestration |
| `duckduckgo-search` | >=8.1.1 | Web search |
| `httpx` | >=0.28.1 | Async HTTP client |
| `click` | >=8.3.1 | CLI framework |
| `pydantic` | >=2.12.5 | Data validation |

---

## 📝 Example Output

```
============================================================
📊 RESEARCH REPORT
============================================================

# Quantum Computing: Latest Developments

## Overview
Quantum computing has made significant strides in 2025-2026...

## Key Developments

### Hardware Advances
- IBM's 1000+ qubit processor...
- Google's error correction breakthrough...

### Applications
- Drug discovery simulations...
- Cryptography implications...

## Challenges
- Decoherence issues...
- Scaling limitations...

------------------------------------------------------------
📌 KEY TAKEAWAYS
------------------------------------------------------------
  • Quantum error correction reached new milestones
  • Commercial applications emerging in pharma
  • Post-quantum cryptography adoption accelerating
  • Hardware scaling remains a key challenge

------------------------------------------------------------
📚 SOURCES
------------------------------------------------------------
  • https://www.nature.com/articles/quantum-2025
  • https://arxiv.org/abs/quantum-computing
  • https://www.ibm.com/quantum
  ...

------------------------------------------------------------
✅ Quality Score: 0.92
💾 Saved to memory: a3f8b2c1d4e5
```

---


