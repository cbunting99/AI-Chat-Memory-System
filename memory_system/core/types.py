"""
File: types.py
Description: Core types and enums for the memory system including MessageType, CompressionLevel, MediaType, and SummaryTrigger

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Core types and enums for the memory system."""

from enum import Enum


class MessageType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class CompressionLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 6
    HIGH = 9


class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"


class SummaryTrigger(Enum):
    TOKEN_LIMIT = "token_limit"
    TIME_BASED = "time_based"
    MANUAL = "manual"
    IMPORTANCE_THRESHOLD = "importance_threshold"
