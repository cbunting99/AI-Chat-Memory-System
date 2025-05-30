# Advanced Memory System

<!-- 
Copyright 2025 Chris Bunting
Advanced Memory System - A sophisticated, modular memory management system for AI applications
-->

A sophisticated, modular memory management system built in **Python** using **SQLite3** for AI applications featuring vector embeddings, knowledge graphs, auto-summarization, multi-modal content support, and memory consolidation.

## 🚀 Features

### Core Functionality
- **Session Management**: Create and manage conversation sessions with comprehensive metadata
- **Message Storage**: Store conversations with support for different message types and roles
- **File Context**: Add and manage file contexts with automatic embedding generation
- **Intelligent Context**: Retrieve relevant context based on token limits and importance

### Advanced Capabilities
- **🔍 Vector Embeddings**: Semantic search using sentence transformers
- **🕸️ Knowledge Graphs**: Relationship mapping between entities and concepts
- **📝 Auto-Summarization**: Automatic content summarization based on configurable triggers
- **🎯 Multi-Modal Support**: Process images, audio, video, and documents
- **💾 Memory Consolidation**: Intelligent memory organization and optimization
- **📊 Analytics**: Comprehensive session statistics and insights

## 📁 Project Structure

```
memory_system/
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── memory_system.py       # Main AdvancedMemorySystem class
│   ├── models.py              # Data models and classes
│   └── types.py               # Enums and type definitions
├── utils/                      # Utility modules
│   ├── __init__.py
│   └── database.py            # Database management
├── embeddings/                 # Vector embeddings
│   ├── __init__.py
│   └── embedding_manager.py   # Semantic search functionality
├── knowledge/                  # Knowledge graph
│   ├── __init__.py
│   └── knowledge_graph.py     # Knowledge graph operations
├── summarization/              # Auto-summarization
│   ├── __init__.py
│   └── summarization_manager.py # Summarization logic
├── multimodal/                 # Multi-modal support
│   ├── __init__.py
│   └── multimodal_manager.py  # Multi-modal content processing
├── consolidation/              # Memory consolidation
│   ├── __init__.py
│   └── consolidation_manager.py # Memory consolidation operations
├── examples/                   # Usage examples
│   ├── basic_example.py       # Basic usage demonstration
│   ├── advanced_example.py    # Full features demonstration
│   ├── knowledge_graph_example.py # Knowledge graph specific
│   └── multimodal_example.py  # Multi-modal processing
└── __init__.py                # Package initialization
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Clone or download the project
cd memory

# Install required packages
pip install -r requirements.txt
```

### Optional Dependencies

For enhanced functionality, you can install additional packages:

```bash
# Advanced NLP
pip install spacy nltk

# Enhanced image/video processing
pip install opencv-python moviepy

# Document processing
pip install PyPDF2 python-docx python-pptx

# Audio enhancements
pip install soundfile pydub
```

## 🚀 Quick Start

### Basic Usage

```python
from memory_system import AdvancedMemorySystem, MessageType

# Initialize the memory system
memory = AdvancedMemorySystem("my_memory.db", enable_embeddings=True)

# Create a session
session_id = memory.create_session(
    user_id="user123", 
    session_name="AI Assistant Chat"
)

# Add messages
memory.add_message(
    session_id=session_id,
    content="Hello, I'm working on a Python project.",
    message_type=MessageType.USER
)

memory.add_message(
    session_id=session_id,
    content="I'd be happy to help! What specific aspect of your Python project would you like assistance with?",
    message_type=MessageType.ASSISTANT
)

# Search conversations
results = memory.semantic_search(
    session_id=session_id,
    query="Python programming help",
    limit=5
)

# Get intelligent context
context = memory.get_intelligent_context(
    session_id=session_id,
    max_tokens=4000,
    include_files=True,
    include_summaries=True
)

# Close when done
memory.close()
```

### Multi-Modal Content

```python
from memory_system import AdvancedMemorySystem, MediaType

memory = AdvancedMemorySystem("multimodal_memory.db")
session_id = memory.create_session()

# Add image content
image_id = memory.add_media_content(
    session_id=session_id,
    content="A beautiful sunset over mountains",
    media_type=MediaType.IMAGE,
    metadata={
        "filename": "sunset.jpg",
        "location": "Rocky Mountains",
        "camera": "Canon EOS R5"
    }
)

# Add audio content
audio_id = memory.add_media_content(
    session_id=session_id,
    content="Jazz performance recording",
    media_type=MediaType.AUDIO,
    metadata={
        "duration": "4:32",
        "genre": "Jazz",
        "artist": "Miles Davis"
    }
)

# Search across media types
media_results = memory.search_media_content(
    session_id=session_id,
    media_types=[MediaType.IMAGE, MediaType.AUDIO],
    query="music mountains",
    limit=10
)
```

### Knowledge Graph

```python
# Add knowledge nodes
person_id = memory.add_knowledge_node(
    session_id=session_id,
    content="Albert Einstein",
    node_type="person",
    importance_score=0.9
)

concept_id = memory.add_knowledge_node(
    session_id=session_id,
    content="Theory of Relativity",
    node_type="concept", 
    importance_score=0.8
)

# Create relationships
memory.add_knowledge_relation(
    source_node_id=person_id,
    target_node_id=concept_id,
    relation_type="developed",
    confidence=0.95
)

# Query the knowledge graph
graph = memory.get_knowledge_graph(
    session_id=session_id,
    min_importance=0.5
)

# Find related concepts
related = memory.find_related_concepts(
    session_id=session_id,
    concept="physics",
    max_depth=2
)
```

## 📚 API Reference

### Core Classes

#### AdvancedMemorySystem

The main class that provides all functionality.

```python
AdvancedMemorySystem(
    db_path='advanced_memory.db',
    enable_compression=True,
    enable_embeddings=False,
    max_context_tokens=100000,
    auto_summarize=True,
    embedding_model='all-MiniLM-L6-v2'
)
```

**Parameters:**
- `db_path`: Path to SQLite database file
- `enable_compression`: Enable content compression for storage efficiency
- `enable_embeddings`: Enable vector embeddings for semantic search
- `max_context_tokens`: Maximum tokens before triggering auto-summarization
- `auto_summarize`: Enable automatic summarization
- `embedding_model`: Sentence transformer model for embeddings

### Key Methods

#### Session Management
- `create_session(user_id, session_name)` - Create a new session
- `get_session_stats(session_id)` - Get session statistics
- `cleanup_old_data(days_old, keep_important)` - Clean up old data

#### Message Operations
- `add_message(session_id, content, message_type, ...)` - Add a message
- `search_conversations(session_id, query, limit)` - Search conversations
- `semantic_search(session_id, query, ...)` - Semantic search using embeddings

#### File Context
- `add_file_context(session_id, file_name, content, ...)` - Add file context
- `get_intelligent_context(session_id, max_tokens, ...)` - Get intelligent context

#### Knowledge Graph
- `add_knowledge_node(session_id, content, node_type, ...)` - Add knowledge node
- `add_knowledge_relation(source_id, target_id, relation_type, ...)` - Add relation
- `get_knowledge_graph(session_id, node_types, min_importance)` - Get graph
- `find_related_concepts(session_id, concept, max_depth)` - Find related concepts

#### Multi-Modal
- `add_media_content(session_id, content, media_type, ...)` - Add media content
- `search_media_content(session_id, media_types, query, limit)` - Search media

#### Summarization
- `create_summary(session_id, summary_type, summary, ...)` - Create summary
- `trigger_auto_summarization(session_id)` - Trigger auto-summarization

#### Memory Consolidation
- `start_memory_consolidation(session_id, job_type)` - Start consolidation
- `get_consolidation_status(job_id)` - Get consolidation status

## 📖 Examples

The `examples/` directory contains comprehensive examples:

1. **`basic_example.py`** - Basic usage patterns and core functionality
2. **`advanced_example.py`** - Advanced features including embeddings and knowledge graphs
3. **`knowledge_graph_example.py`** - Detailed knowledge graph operations
4. **`multimodal_example.py`** - Multi-modal content processing

Run an example:

```bash
# Run examples using module syntax from the project root
cd memory

# Basic functionality
python -m memory_system.examples.basic_example

# Advanced features with embeddings
python -m memory_system.examples.advanced_example

# Knowledge graph demonstration
python -m memory_system.examples.knowledge_graph_example

# Multi-modal content processing
python -m memory_system.examples.multimodal_example
```

## 🏗️ Architecture

### Modular Design

The system is built with a modular architecture for maintainability and extensibility:

- **Core Module**: Main memory system class and essential functionality
- **Database Utils**: Database management and schema operations
- **Embeddings Module**: Vector embeddings and semantic search
- **Knowledge Module**: Knowledge graph operations and relationship management
- **Summarization Module**: Auto-summarization logic and triggers
- **Multi-Modal Module**: Multi-modal content processing
- **Consolidation Module**: Memory consolidation and optimization

### Database Schema

The system uses SQLite with the following main tables:

- `sessions` - Session metadata and statistics
- `conversations` - Message storage with embeddings
- `file_contexts` - File content and metadata
- `summaries` - Generated summaries
- `media_contents` - Multi-modal content
- `knowledge_nodes` - Knowledge graph nodes
- `knowledge_relations` - Knowledge graph relationships
- `consolidation_jobs` - Memory consolidation jobs

## ⚙️ Configuration

### Embedding Models

Supported sentence transformer models:
- `all-MiniLM-L6-v2` (default) - Fast and efficient
- `all-mpnet-base-v2` - Higher quality embeddings
- `multi-qa-MiniLM-L6-cos-v1` - Optimized for Q&A

### Media Types

Supported media types:
- `TEXT` - Plain text content
- `IMAGE` - Image files (JPEG, PNG, etc.)
- `AUDIO` - Audio files (MP3, WAV, etc.)
- `VIDEO` - Video files (MP4, AVI, etc.)
- `DOCUMENT` - Documents (PDF, DOCX, etc.)
- `CODE` - Source code files

### Compression Levels

Available compression levels:
- `NONE` (0) - No compression
- `LOW` (1) - Fast compression
- `MEDIUM` (6) - Balanced compression (default)
- `HIGH` (9) - Maximum compression

## 🧪 Testing

Run the examples to test functionality:

```bash
# Navigate to project root
cd memory

# Test basic functionality
python -m memory_system.examples.basic_example

# Test advanced features
python -m memory_system.examples.advanced_example

# Test knowledge graph
python -m memory_system.examples.knowledge_graph_example

# Test multi-modal support
python -m memory_system.examples.multimodal_example
```

### Validate Package Installation

```bash
# Test that imports work correctly
python -c "from memory_system import AdvancedMemorySystem, MessageType, MediaType; print('✓ All imports successful')"
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Embedding Model Download**: First run may be slow as models download
   ```python
   # Models are cached after first download
   memory = AdvancedMemorySystem(enable_embeddings=True)
   ```

3. **Database Permissions**: Ensure write permissions for database file
   ```python
   # Use absolute path if needed
   memory = AdvancedMemorySystem("/path/to/memory.db")
   ```

4. **Multi-Modal Dependencies**: Install optional dependencies for full functionality
   ```bash
   pip install Pillow librosa opencv-python
   ```

### Performance Tips

- Enable embeddings only when semantic search is needed
- Use compression for large content storage
- Set appropriate `max_context_tokens` for your use case
- Regular cleanup of old data for optimal performance

## 📊 Project Status

**✅ COMPLETED REFACTORING** - The system has been successfully refactored from a monolithic structure into a clean, modular architecture.

### What's Working:
- ✅ **Modular Architecture**: Clean separation of concerns across modules
- ✅ **All Examples**: Basic, advanced, knowledge graph, and multi-modal examples
- ✅ **Package Structure**: Proper imports and module initialization
- ✅ **Documentation**: Comprehensive API reference and usage examples
- ✅ **Multi-Modal Support**: Image, audio, video, and document processing
- ✅ **Knowledge Graphs**: Entity relationships and concept mapping
- ✅ **Memory Consolidation**: Background optimization processes
- ✅ **Auto-Summarization**: Intelligent content summarization

### Key Benefits of Modular Design:
- **Maintainability**: Each component has a clear responsibility
- **Extensibility**: Easy to add new features without affecting existing code
- **Testability**: Individual modules can be tested in isolation
- **Performance**: Optimized imports and lazy loading where appropriate

## 🤝 Contributing

This is a modular system designed for easy extension:

1. **Adding New Media Types**: Extend `MediaType` enum and add processing logic
2. **Custom Summarization**: Implement custom summarization strategies
3. **New Knowledge Relations**: Add custom relationship types
4. **Enhanced Search**: Implement additional search algorithms

## 📄 License

```
Copyright 2025 Chris Bunting

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🔗 Dependencies

### Core Dependencies
- `numpy` - Numerical operations
- `sentence-transformers` - Semantic embeddings
- `torch` - ML framework backend

### Optional Dependencies
- `Pillow` - Image processing
- `librosa` - Audio processing
- `opencv-python` - Advanced image/video processing
- `PyPDF2` - PDF processing
- `spacy` - Advanced NLP

## 📞 Support

For issues and questions:
1. Check the examples directory for usage patterns
2. Review the troubleshooting section
3. Examine the modular code structure for customization

---

**Advanced Memory System** © 2025 Chris Bunting - Intelligent memory management for AI applications with multi-modal support and knowledge graphs.
