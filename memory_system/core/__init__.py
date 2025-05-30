"""
File: __init__.py
Description: Core module exports for memory system components including types, models, and main system class

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

# Core module exports
from .memory_system import AdvancedMemorySystem
from .types import MessageType, CompressionLevel, MediaType, SummaryTrigger
from .models import Message, MediaContent, KnowledgeNode, KnowledgeRelation

__all__ = [
    "AdvancedMemorySystem",
    "MessageType",
    "CompressionLevel", 
    "MediaType",
    "SummaryTrigger",
    "Message",
    "MediaContent",
    "KnowledgeNode",
    "KnowledgeRelation"
]