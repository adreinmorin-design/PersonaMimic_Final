"""
app/database/memory_service.py - Centralized Neural Memory Service
Handles long-term vector memory using ChromaDB.
"""

import datetime
import logging
import os
import uuid
from typing import Any

try:
    import chromadb
except ImportError:
    chromadb = None

logger = logging.getLogger("database.memory_service")


class NeuralMemory:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            # Default to a 'neural_memory' folder in the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.persist_directory = os.path.join(base_dir, "neural_memory")
        else:
            self.persist_directory = persist_directory

        self.client = None
        self.collection = None
        self.enabled = False

        try:
            if chromadb is None:
                raise RuntimeError("chromadb is not installed")

            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="agent_memories",
                metadata={"hnsw:space": "cosine"},
            )
            self.enabled = True
        except Exception as exc:
            logger.warning(f"Neural memory disabled: {exc}")

    def store_memory(self, content: str, role: str, brain_name: str, niche: str = "general"):
        """Store a structured memory from an agent."""
        if not self.enabled or not content:
            return None

        memory_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        try:
            self.collection.add(
                documents=[content],
                metadatas=[
                    {
                        "role": role,
                        "brain_name": brain_name,
                        "niche": niche,
                        "timestamp": timestamp,
                        "type": "experience",
                    }
                ],
                ids=[memory_id],
            )
            return memory_id
        except Exception as exc:
            logger.warning(f"Failed to store memory for {brain_name}: {exc}")
            return None

    def recall_memories(
        self,
        query: str,
        brain_name: str | None = None,
        niche: str | None = None,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Recall relevant memories based on semantic similarity."""
        if not self.enabled or not query:
            return []

        where_filter = {}
        if brain_name:
            where_filter["brain_name"] = brain_name
        if niche:
            where_filter["niche"] = niche

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None,
            )
        except Exception as exc:
            logger.warning(f"Failed to recall memories for {brain_name or 'global'}: {exc}")
            return []

        formatted_results = []
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        distances = results.get("distances") or []
        if documents and documents[0]:
            for i, content in enumerate(documents[0]):
                formatted_results.append(
                    {
                        "content": content,
                        "metadata": (metadatas[0][i] if metadatas and metadatas[0] else {}),
                        "distance": (distances[0][i] if distances and distances[0] else None),
                    }
                )

        return formatted_results

    def store_tool_outcome(
        self, tool_name: str, tool_args: dict[str, Any], result: str, brain_name: str
    ):
        """Specifically store the outcome of a tool call as a memory."""
        if not self.enabled or not tool_name:
            return None

        content = f"Tool '{tool_name}' with args {tool_args} resulted in: {result[:500]}"
        memory_id = str(uuid.uuid4())

        try:
            self.collection.add(
                documents=[content],
                metadatas=[
                    {
                        "tool_name": tool_name,
                        "brain_name": brain_name,
                        "type": "tool_outcome",
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                ],
                ids=[memory_id],
            )
            return memory_id
        except Exception as exc:
            logger.warning(f"Failed to store tool outcome for {tool_name}: {exc}")
            return None


# Singleton instance
memory_service = NeuralMemory()
