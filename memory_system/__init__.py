"""
File: __init__.py
Description: Memory System Package initialization and main exports

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

# Memory System Package
from .core.memory_system import AdvancedMemorySystem
from .core.types import MessageType, CompressionLevel, MediaType, SummaryTrigger
from .core.models import Message, MediaContent, KnowledgeNode, KnowledgeRelation

__version__ = "1.0.0"
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
