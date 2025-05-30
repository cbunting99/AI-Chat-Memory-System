"""
File: knowledge_graph_example.py
Description: Knowledge Graph example demonstrating relationship tracking and concept exploration functionality

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""
Knowledge Graph example demonstrating relationship tracking and concept exploration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system import AdvancedMemorySystem, MessageType

def knowledge_graph_example():
    """Demonstrate knowledge graph functionality."""
    print("=== Knowledge Graph Example ===")
    
    memory = AdvancedMemorySystem(
        db_path='example_knowledge.db',
        enable_embeddings=True,
        auto_summarize=False
    )
    
    try:
        session_id = memory.create_session(
            user_id="knowledge_user",
            session_name="Knowledge Graph Demo"
        )
        
        # === BUILD A KNOWLEDGE GRAPH ABOUT PROGRAMMING ===
        
        # Programming languages
        python_node = memory.add_knowledge_node(
            session_id, "Python", "programming_language",
            importance_score=0.9,
            metadata={"paradigm": "multi-paradigm", "typing": "dynamic"}
        )
        
        javascript_node = memory.add_knowledge_node(
            session_id, "JavaScript", "programming_language", 
            importance_score=0.8,
            metadata={"paradigm": "multi-paradigm", "typing": "dynamic"}
        )
        
        java_node = memory.add_knowledge_node(
            session_id, "Java", "programming_language",
            importance_score=0.8,
            metadata={"paradigm": "object-oriented", "typing": "static"}
        )
        
        # Frameworks and libraries
        django_node = memory.add_knowledge_node(
            session_id, "Django", "web_framework",
            importance_score=0.7,
            metadata={"language": "Python", "type": "full-stack"}
        )
        
        react_node = memory.add_knowledge_node(
            session_id, "React", "frontend_library",
            importance_score=0.8,
            metadata={"language": "JavaScript", "type": "component-based"}
        )
        
        tensorflow_node = memory.add_knowledge_node(
            session_id, "TensorFlow", "ml_framework",
            importance_score=0.9,
            metadata={"language": "Python", "domain": "machine_learning"}
        )
        
        # Concepts
        oop_node = memory.add_knowledge_node(
            session_id, "Object-Oriented Programming", "concept",
            importance_score=0.8,
            metadata={"paradigm": "programming_paradigm"}
        )
        
        ml_node = memory.add_knowledge_node(
            session_id, "Machine Learning", "concept",
            importance_score=0.9,
            metadata={"domain": "artificial_intelligence"}
        )
        
        # === CREATE RELATIONSHIPS ===
        
        # Language -> Framework relationships
        memory.add_knowledge_relation(
            python_node, django_node, "supports_framework",
            confidence=1.0, metadata={"relationship": "implements"}
        )
        
        memory.add_knowledge_relation(
            python_node, tensorflow_node, "supports_framework", 
            confidence=1.0, metadata={"relationship": "implements"}
        )
        
        memory.add_knowledge_relation(
            javascript_node, react_node, "supports_library",
            confidence=1.0, metadata={"relationship": "implements"}
        )
        
        # Language -> Concept relationships
        memory.add_knowledge_relation(
            python_node, oop_node, "implements_concept",
            confidence=0.9, metadata={"support_level": "full"}
        )
        
        memory.add_knowledge_relation(
            java_node, oop_node, "implements_concept",
            confidence=1.0, metadata={"support_level": "native"}
        )
        
        # Framework -> Concept relationships
        memory.add_knowledge_relation(
            tensorflow_node, ml_node, "enables_concept",
            confidence=1.0, metadata={"relationship": "tool_for"}
        )
        
        print("Built knowledge graph with programming concepts")
        
        # === ADD CONVERSATIONS TO AUTO-EXTRACT KNOWLEDGE ===
        
        memory.add_message(
            session_id,
            "I'm learning Python and want to build web applications. Should I use Django or Flask?",
            MessageType.USER
        )
        
        memory.add_message(
            session_id,
            "For web development in Python, both Django and Flask are excellent choices. Django is a full-featured framework with batteries included, while Flask is more minimalist and flexible.",
            MessageType.ASSISTANT
        )
        
        memory.add_message(
            session_id,
            "I'm also interested in machine learning. Can I use TensorFlow with Python for deep learning projects?",
            MessageType.USER
        )
        
        memory.add_message(
            session_id,
            "Absolutely! TensorFlow is one of the most popular deep learning frameworks for Python. It's great for neural networks, computer vision, and natural language processing.",
            MessageType.ASSISTANT
        )
        
        print("Added conversations with auto-knowledge extraction")
        
        # === EXPLORE THE KNOWLEDGE GRAPH ===
        
        print("\n=== Knowledge Graph Exploration ===")
        
        # Get full graph
        graph = memory.get_knowledge_graph(session_id)
        print(f"Total nodes: {graph['stats']['total_nodes']}")
        print(f"Total relations: {graph['stats']['total_relations']}")
        print(f"Node types: {graph['stats']['node_types']}")
        
        # Show all nodes
        print("\nAll knowledge nodes:")
        for node in graph['nodes']:
            print(f"  - {node['content']} ({node['type']}, importance: {node['importance']:.2f})")
        
        # Show all relations
        print("\nAll relations:")
        for relation in graph['relations']:
            source_name = next(n['content'] for n in graph['nodes'] if n['id'] == relation['source'])
            target_name = next(n['content'] for n in graph['nodes'] if n['id'] == relation['target'])
            print(f"  - {source_name} --[{relation['type']}]--> {target_name} (confidence: {relation['confidence']:.2f})")
        
        # === FIND RELATED CONCEPTS ===
        
        print("\n=== Related Concepts Exploration ===")
        
        # Find concepts related to Python
        python_related = memory.find_related_concepts(session_id, "Python", max_depth=2)
        print(f"\nConcepts related to Python ({len(python_related)} found):")
        for concept in python_related:
            print(f"  - {concept['content']} (depth: {concept['depth']}, relation: {concept['relation_type']})")
        
        # Find concepts related to Machine Learning
        ml_related = memory.find_related_concepts(session_id, "Machine Learning", max_depth=2)
        print(f"\nConcepts related to Machine Learning ({len(ml_related)} found):")
        for concept in ml_related:
            print(f"  - {concept['content']} (depth: {concept['depth']}, relation: {concept['relation_type']})")
        
        # === FILTER BY NODE TYPE ===
        
        print("\n=== Filtered Views ===")
        
        # Get only programming languages
        lang_graph = memory.get_knowledge_graph(
            session_id, 
            node_types=["programming_language"],
            min_importance=0.7
        )
        print(f"\nProgramming languages (importance >= 0.7): {len(lang_graph['nodes'])} found")
        for node in lang_graph['nodes']:
            print(f"  - {node['content']} (importance: {node['importance']:.2f})")
        
        # Get frameworks and libraries
        framework_graph = memory.get_knowledge_graph(
            session_id,
            node_types=["web_framework", "frontend_library", "ml_framework"],
            min_importance=0.5
        )
        print(f"\nFrameworks and libraries: {len(framework_graph['nodes'])} found")
        for node in framework_graph['nodes']:
            print(f"  - {node['content']} ({node['type']}, importance: {node['importance']:.2f})")
        
        # === SEMANTIC SEARCH IN KNOWLEDGE ===
        
        if memory.embedding_manager.enable_embeddings:
            print("\n=== Semantic Knowledge Search ===")
            
            # Search for web development related content
            web_results = memory.semantic_search(
                session_id,
                "web development framework",
                search_types=['conversations'],
                limit=5
            )
            
            print(f"Web development semantic search: {len(web_results)} results")
            for result in web_results:
                print(f"  - {result['similarity']:.3f}: {result['content'][:80]}...")
    
    finally:
        memory.close()
    
    print("\nKnowledge graph example completed!")

if __name__ == "__main__":
    knowledge_graph_example()
