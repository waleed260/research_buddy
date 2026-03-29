"""Hooks for logging, tracing, and learning from research."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass

from agents import (
    RunHooks,
    Agent,
    RunResult,
    Tool,
)


@dataclass
class ResearchLog:
    """A log entry for research activities."""
    timestamp: str
    topic: str
    action: str
    details: dict[str, Any]
    duration_ms: float = 0.0
    success: bool = True


class ResearchLogger:
    """Logger for research activities."""
    
    def __init__(self, log_path: Path | None = None):
        if log_path is None:
            log_path = Path(__file__).parent.parent.parent / "research_logs.jsonl"
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("research_buddy")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log(self, log_entry: ResearchLog) -> None:
        """Log a research activity."""
        with open(self.log_path, "a") as f:
            f.write(json.dumps(log_entry.__dict__) + "\n")
        
        self.logger.info(f"{log_entry.action}: {log_entry.topic}")
    
    def log_search(self, topic: str, query: str, results_count: int, success: bool = True) -> None:
        """Log a search activity."""
        self.log(ResearchLog(
            timestamp=datetime.now().isoformat(),
            topic=topic,
            action="search",
            details={"query": query, "results_count": results_count},
            success=success
        ))
    
    def log_analysis(self, topic: str, sources_analyzed: int, key_findings: list[str]) -> None:
        """Log an analysis activity."""
        self.log(ResearchLog(
            timestamp=datetime.now().isoformat(),
            topic=topic,
            action="analysis",
            details={"sources_analyzed": sources_analyzed, "key_findings": key_findings}
        ))
    
    def log_synthesis(self, topic: str, output_length: int, quality_score: float) -> None:
        """Log a synthesis activity."""
        self.log(ResearchLog(
            timestamp=datetime.now().isoformat(),
            topic=topic,
            action="synthesis",
            details={"output_length": output_length, "quality_score": quality_score}
        ))
    
    def log_handoff(self, topic: str, from_agent: str, to_agent: str) -> None:
        """Log an agent handoff."""
        self.log(ResearchLog(
            timestamp=datetime.now().isoformat(),
            topic=topic,
            action="handoff",
            details={"from_agent": from_agent, "to_agent": to_agent}
        ))
    
    def log_error(self, topic: str, error: str, context: dict[str, Any] | None = None) -> None:
        """Log an error."""
        self.log(ResearchLog(
            timestamp=datetime.now().isoformat(),
            topic=topic,
            action="error",
            details={"error": error, "context": context or {}},
            success=False
        ))
    
    def get_recent_logs(self, limit: int = 10) -> list[ResearchLog]:
        """Get recent log entries."""
        logs = []
        try:
            with open(self.log_path, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    data = json.loads(line.strip())
                    logs.append(ResearchLog(**data))
        except FileNotFoundError:
            pass
        return logs


class LearningHooks(RunHooks):
    """Hooks that enable the agent to learn from research activities."""
    
    def __init__(self, logger: ResearchLogger | None = None):
        super().__init__()
        self.logger = logger or ResearchLogger()
        self._start_times: dict[str, float] = {}
    
    async def on_run_start(self, agent: Agent, input: list[dict[str, Any]]) -> None:
        """Called when a run starts."""
        topic = input[-1].get("content", "unknown")[:50] if input else "unknown"
        self._start_times[topic] = datetime.now().timestamp() * 1000
        self.logger.logger.info(f"Starting research on: {topic}")
    
    async def on_run_end(self, agent: Agent, result: RunResult) -> None:
        """Called when a run ends."""
        topic = str(result.input)[-50:] if result.input else "unknown"
        start_time = self._start_times.get(topic, datetime.now().timestamp() * 1000)
        duration = (datetime.now().timestamp() * 1000) - start_time
        
        self.logger.logger.info(f"Completed research on: {topic} in {duration:.0f}ms")
        
        # Log the synthesis
        output_text = str(result.final_output) if result.final_output else ""
        self.logger.log_synthesis(
            topic=topic,
            output_length=len(output_text),
            quality_score=0.8  # Default score, can be updated based on feedback
        )
    
    async def on_tool_start(
        self,
        agent: Agent,
        tool: Tool,
        args: dict[str, Any],
        run_result: RunResult | None = None
    ) -> None:
        """Called when a tool starts."""
        self.logger.logger.debug(f"Tool starting: {tool.name}")
    
    async def on_tool_end(
        self,
        agent: Agent,
        tool: Tool,
        result: Any,
        run_result: RunResult | None = None
    ) -> None:
        """Called when a tool ends."""
        if tool.name == "web_search":
            if isinstance(result, dict):
                success = result.get("success", False)
                count = result.get("count", 0)
                query = result.get("query", "unknown")
                self.logger.log_search(
                    topic=query[:50],
                    query=query,
                    results_count=count,
                    success=success
                )


class FeedbackLearningHook:
    """Hook for learning from user feedback."""
    
    def __init__(self, logger: ResearchLogger | None = None):
        self.logger = logger or ResearchLogger()
        self.feedback_store: list[dict[str, Any]] = []
    
    def record_feedback(
        self,
        topic: str,
        feedback_type: str,
        feedback_text: str,
        quality_rating: float | None = None
    ) -> None:
        """Record user feedback for learning."""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "quality_rating": quality_rating,
        }
        self.feedback_store.append(feedback_entry)
        
        # Save to file
        feedback_path = Path(__file__).parent.parent.parent / "feedback_logs.jsonl"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        with open(feedback_path, "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")
        
        self.logger.logger.info(f"Recorded feedback for: {topic}")
    
    def get_learning_patterns(self) -> dict[str, Any]:
        """Analyze feedback to find learning patterns."""
        if not self.feedback_store:
            return {"patterns": [], "avg_quality": 0.0}
        
        # Calculate average quality rating
        ratings = [f["quality_rating"] for f in self.feedback_store if f.get("quality_rating")]
        avg_quality = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Find common feedback types
        feedback_types: dict[str, int] = {}
        for f in self.feedback_store:
            ft = f.get("feedback_type", "unknown")
            feedback_types[ft] = feedback_types.get(ft, 0) + 1
        
        return {
            "patterns": feedback_types,
            "avg_quality": avg_quality,
            "total_feedback": len(self.feedback_store)
        }
