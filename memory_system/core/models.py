"""
File: models.py
Description: Data models and classes for memory system including Message, MediaContent, KnowledgeNode, and KnowledgeRelation

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Data models for the memory system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from .types import MessageType, MediaType


@dataclass
class Message:
    message_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    metadata: Dict[str, Any]
    tokens: Optional[int] = None
    embedding: Optional[bytes] = None


@dataclass
class MediaContent:
    content_id: str
    media_type: MediaType
    content: Union[str, bytes]
    metadata: Dict[str, Any]
    file_path: Optional[str] = None
    encoding: Optional[str] = None
    embedding: Optional[bytes] = None


@dataclass
class KnowledgeNode:
    node_id: str
    content: str
    node_type: str
    importance_score: float
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class KnowledgeRelation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    confidence: float
    metadata: Dict[str, Any]
