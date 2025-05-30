"""
File: advanced_example.py
Description: Advanced usage example demonstrating all features including vector embeddings, knowledge graphs, auto-summarization, multi-modal content, and memory consolidation

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""
Advanced usage example demonstrating all features of the Advanced Memory System.

This example shows:
- Vector embeddings and semantic search
- Knowledge graph functionality
- Auto-summarization
- Multi-modal content support
- Memory consolidation
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system import AdvancedMemorySystem, MessageType, MediaType

def advanced_example():
    """Advanced usage example with all features."""
    print("=== Advanced Memory System - Full Features Example ===")
    
    # Initialize with all features enabled
    memory = AdvancedMemorySystem(
        db_path='example_advanced.db',
        enable_embeddings=True,  # Enable semantic search
        auto_summarize=True,     # Enable auto-summarization
        max_context_tokens=50000,
        embedding_model='all-MiniLM-L6-v2'
    )
    
    try:
        # Create a session
        session_id = memory.create_session(
            user_id="advanced_user",
            session_name="Advanced Features Demo"
        )
        print(f"Created session: {session_id}")
        
        # === CONVERSATION WITH KNOWLEDGE EXTRACTION ===
        
        # Add technical conversation
        msg1_id = memory.add_message(
            session_id=session_id,
            content="I'm working on a machine learning project using TensorFlow and scikit-learn. I need to implement a neural network for image classification with convolutional layers.",
            message_type=MessageType.USER,
            metadata={"importance": 0.8, "topics": ["machine learning", "tensorflow", "neural networks"]}
        )
        
        msg2_id = memory.add_message(
            session_id=session_id,
            content="Great! For image classification with TensorFlow, you'll want to use Convolutional Neural Networks (CNNs). Let me help you set up a basic CNN architecture with Conv2D layers, pooling, and dense layers for classification.",
            message_type=MessageType.ASSISTANT,
            metadata={"importance": 0.9}
        )
        
        msg3_id = memory.add_message(
            session_id=session_id,
            content="Can you show me how to preprocess the image data and set up data augmentation? I'm working with a dataset of 10,000 images in 5 categories.",
            message_type=MessageType.USER,
            metadata={"importance": 0.7}
        )
        
        print("Added technical conversation with metadata")
        
        # === KNOWLEDGE GRAPH OPERATIONS ===
        
        # Manually add knowledge nodes
        tf_node = memory.add_knowledge_node(
            session_id=session_id,
            content="TensorFlow",
            node_type="framework",
            importance_score=0.9,
            metadata={"category": "deep_learning", "type": "library"}
        )
        
        cnn_node = memory.add_knowledge_node(
            session_id=session_id,
            content="Convolutional Neural Network",
            node_type="concept",
            importance_score=0.8,
            metadata={"category": "deep_learning", "type": "architecture"}
        )
        
        # Add relationship
        relation_id = memory.add_knowledge_relation(
            source_node_id=tf_node,
            target_node_id=cnn_node,
            relation_type="implements",
            confidence=0.95,
            metadata={"context": "image_classification"}
        )
        
        print(f"Created knowledge nodes and relations")
        
        # === MULTI-MODAL CONTENT ===
        
        # Add code file
        code_content = '''
import tensorflow as tf
from tensorflow.keras import layers, models

def create_cnn_model(input_shape, num_classes):
    """Create a CNN model for image classification."""
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model

# Example usage
model = create_cnn_model((224, 224, 3), 5)
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
'''
        
        code_id = memory.add_media_content(
            session_id=session_id,
            content=code_content,
            media_type=MediaType.CODE,
            metadata={"language": "python", "purpose": "cnn_model"}
        )
        print(f"Added code content: {code_id}")
        
        # Add documentation
        doc_content = """
# CNN Image Classification Guide

## Overview
Convolutional Neural Networks are excellent for image classification tasks.

## Key Components:
1. Convolutional layers - Extract features
2. Pooling layers - Reduce dimensionality  
3. Dense layers - Final classification
4. Data augmentation - Improve generalization

## Best Practices:
- Use appropriate input normalization
- Implement dropout for regularization
- Monitor validation accuracy
- Use appropriate batch sizes
"""
        
        doc_id = memory.add_media_content(
            session_id=session_id,
            content=doc_content,
            media_type=MediaType.DOCUMENT,
            metadata={"format": "markdown", "topic": "cnn_guide"}
        )
        print(f"Added documentation: {doc_id}")
        
        # === SEMANTIC SEARCH ===
        
        if memory.embedding_manager.enable_embeddings:
            print("\n=== Semantic Search ===")
            
            # Search for neural network related content
            semantic_results = memory.semantic_search(
                session_id=session_id,
                query="deep learning neural network architecture",
                search_types=['conversations', 'files'],
                limit=5,
                min_similarity=0.3
            )
            
            print(f"Semantic search results: {len(semantic_results)} found")
            for result in semantic_results:
                print(f"  - {result['type']}: {result['similarity']:.3f} - {result['content'][:50]}...")
        
        # === KNOWLEDGE GRAPH EXPLORATION ===
        
        print("\n=== Knowledge Graph ===")
        
        # Get full knowledge graph
        knowledge_graph = memory.get_knowledge_graph(session_id)
        print(f"Knowledge graph: {knowledge_graph['stats']['total_nodes']} nodes, {knowledge_graph['stats']['total_relations']} relations")
        
        # Find related concepts
        related = memory.find_related_concepts(session_id, "TensorFlow", max_depth=2)
        print(f"Related to TensorFlow: {len(related)} concepts found")
        for concept in related[:3]:
            print(f"  - {concept['content']} (importance: {concept['importance']:.2f})")
        
        # === AUTO-SUMMARIZATION ===
        
        print("\n=== Auto-Summarization ===")
        
        # Add more messages to trigger summarization
        for i in range(15):
            memory.add_message(
                session_id=session_id,
                content=f"This is message {i+4} discussing various aspects of machine learning, neural networks, and TensorFlow implementation details.",
                message_type=MessageType.USER if i % 2 == 0 else MessageType.ASSISTANT,
                metadata={"importance": 0.5 + (i % 3) * 0.1}
            )
        
        # Trigger summarization manually
        summary_id = memory.trigger_auto_summarization(session_id)
        if summary_id:
            print(f"Auto-summary created: {summary_id}")
        else:
            print("No auto-summary triggered (conditions not met)")
        
        # === MEMORY CONSOLIDATION ===
        
        print("\n=== Memory Consolidation ===")
        
        # Start consolidation job
        job_id = memory.start_memory_consolidation(session_id, job_type="full")
        print(f"Started consolidation job: {job_id}")
        
        # Wait a moment and check status
        time.sleep(2)
        status = memory.get_consolidation_status(job_id)
        print(f"Consolidation status: {status['status']} ({status['progress']*100:.1f}%)")
        
        # === MULTI-MODAL SEARCH ===
        
        print("\n=== Multi-Modal Search ===")
        
        # Search code content
        code_results = memory.search_media_content(
            session_id=session_id,
            media_types=[MediaType.CODE],
            query="tensorflow",
            limit=5
        )
        print(f"Code search results: {len(code_results)} found")
        
        # Search documentation
        doc_results = memory.search_media_content(
            session_id=session_id,
            media_types=[MediaType.DOCUMENT],
            query="CNN",
            limit=5
        )
        print(f"Document search results: {len(doc_results)} found")
        
        # === FINAL STATISTICS ===
        
        print("\n=== Final Session Statistics ===")
        stats = memory.get_session_stats(session_id)
        print(f"Session: {stats['session_name']}")
        print(f"Total messages: {stats['total_messages']}")
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"Files: {stats['file_count']}")
        print(f"Summaries: {stats['summary_count']}")
        print(f"Knowledge nodes: {stats['knowledge_nodes']}")
        print(f"Media content: {stats.get('media_breakdown', {})}")
        
        # === CLEANUP DEMO ===
        
        print("\n=== Cleanup Demo ===")
        print("Performing cleanup of old data...")
        memory.cleanup_old_data(days_old=0, keep_important=True)  # Aggressive cleanup for demo
        
        # Show updated stats
        updated_stats = memory.get_session_stats(session_id)
        print(f"After cleanup - Total messages: {updated_stats['total_messages']}")
        
    except Exception as e:
        print(f"Error during advanced example: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        memory.close()
    
    print("\nAdvanced example completed!")

if __name__ == "__main__":
    advanced_example()
