"""Memory module for storing and retrieving research data."""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field, asdict


@dataclass
class ResearchMemory:
    """Represents a single research memory entry."""
    topic: str
    query: str
    findings: str
    sources: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    learned_from: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchMemory":
        return cls(**data)
    
    def get_hash(self) -> str:
        """Generate a unique hash for this memory based on topic and query."""
        content = f"{self.topic}:{self.query}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ResearchMemoryStore:
    """Persistent storage for research memories."""
    
    def __init__(self, storage_path: Path | None = None):
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "research_memories.json"
        self.storage_path = storage_path
        self.memories: list[ResearchMemory] = []
        self._load()
    
    def _load(self) -> None:
        """Load memories from disk."""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.memories = [ResearchMemory.from_dict(m) for m in data]
    
    def _save(self) -> None:
        """Save memories to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump([m.to_dict() for m in self.memories], f, indent=2)
    
    def add(self, memory: ResearchMemory) -> str:
        """Add a new memory and return its hash."""
        mem_hash = memory.get_hash()
        # Check if similar memory exists
        existing = self.find_by_hash(mem_hash)
        if existing:
            # Update existing memory
            existing.findings = memory.findings
            existing.sources = memory.sources
            existing.timestamp = memory.timestamp
            self._save()
            return mem_hash
        self.memories.append(memory)
        self._save()
        return mem_hash
    
    def find_by_hash(self, mem_hash: str) -> ResearchMemory | None:
        """Find a memory by its hash."""
        for mem in self.memories:
            if mem.get_hash() == mem_hash:
                return mem
        return None
    
    def find_by_topic(self, topic: str, limit: int = 5) -> list[ResearchMemory]:
        """Find memories related to a topic."""
        topic_lower = topic.lower()
        matches = []
        for mem in self.memories:
            if topic_lower in mem.topic.lower() or topic_lower in mem.query.lower():
                matches.append(mem)
        # Sort by timestamp (most recent first) and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:limit]
    
    def find_similar(self, query: str, limit: int = 3) -> list[ResearchMemory]:
        """Find memories similar to a query using simple keyword matching."""
        query_words = set(query.lower().split())
        scored = []
        for mem in self.memories:
            text = f"{mem.topic} {mem.query} {' '.join(mem.tags)}".lower()
            overlap = len(query_words & set(text.split()))
            if overlap > 0:
                scored.append((overlap, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:limit]]
    
    def get_all(self) -> list[ResearchMemory]:
        """Get all memories."""
        return self.memories.copy()
    
    def update_quality(self, mem_hash: str, score: float) -> bool:
        """Update the quality score of a memory."""
        for mem in self.memories:
            if mem.get_hash() == mem_hash:
                mem.quality_score = score
                mem.learned_from = True
                self._save()
                return True
        return False
    
    def get_learning_data(self) -> list[dict[str, Any]]:
        """Get all memories that have been learned from."""
        return [m.to_dict() for m in self.memories if m.learned_from]
