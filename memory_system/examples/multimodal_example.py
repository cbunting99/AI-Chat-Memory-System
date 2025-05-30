"""
File: multimodal_example.py
Description: Multi-Modal Memory System example demonstrating processing of images, audio files, and documents with different formats

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

#!/usr/bin/env python3
"""
Multi-Modal Memory System Example

This example demonstrates the multi-modal capabilities of the advanced memory system,
including processing of images, audio files, and documents with different formats.
"""

import logging
import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system import AdvancedMemorySystem, MessageType, MediaType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def multimodal_example():
    """
    Comprehensive example showing multi-modal memory operations.
    """
    print("=== Multi-Modal Memory System Example ===\n")
    
    # Initialize the memory system
    memory_system = AdvancedMemorySystem("multimodal_memory.db")
    
    try:
        # Create a session
        session_id = memory_system.create_session(
            user_id="multimodal_user",
            session_name="Multi-Modal Demo"
        )
        
        print("1. Storing Image with Metadata")
        print("-" * 40)
        
        # Store an image memory (simulated)
        image_memory_id = memory_system.add_media_content(
            session_id=session_id,
            content="A beautiful sunset over the mountains with orange and purple hues",
            media_type=MediaType.IMAGE,
            metadata={
                "filename": "sunset_mountains.jpg",
                "image_format": "JPEG",
                "dimensions": "1920x1080",
                "location": "Rocky Mountains, Colorado",
                "camera": "Canon EOS R5",
                "iso": 100,
                "aperture": "f/8",
                "shutter_speed": "1/60s"
            }
        )
        print(f"✓ Stored image memory with ID: {image_memory_id}")
        
        print("\n2. Storing Audio Content")
        print("-" * 40)
        
        # Store audio memory
        audio_memory_id = memory_system.add_media_content(
            session_id=session_id,
            content="Recording of a jazz quartet performing 'Take Five' by Dave Brubeck. "
                   "Features piano, saxophone, bass, and drums. High energy performance "
                   "with excellent improvisation sections.",
            media_type=MediaType.AUDIO,
            metadata={
                "filename": "take_five_live.mp3",
                "format": "MP3",
                "duration": "6:45",
                "bitrate": "320kbps",
                "genre": "Jazz",
                "artists": ["John Smith Quartet"],
                "venue": "Blue Note NYC",
                "recording_date": "2023-10-15"
            }
        )
        print(f"✓ Stored audio memory with ID: {audio_memory_id}")
        
        print("\n3. Storing Document Content")
        print("-" * 40)
        
        # Store document memory
        doc_memory_id = memory_system.add_media_content(
            session_id=session_id,
            content="Research paper on machine learning applications in climate modeling. "
                   "Discusses neural networks, ensemble methods, and deep learning approaches "
                   "for predicting weather patterns and climate change impacts. "
                   "Contains 47 pages with extensive references and case studies.",
            media_type=MediaType.DOCUMENT,
            metadata={
                "filename": "climate_ml_research.pdf",
                "format": "PDF",
                "pages": 47,
                "authors": ["Dr. Sarah Johnson", "Prof. Michael Chen"],
                "journal": "Nature Climate Change",
                "publication_date": "2023-09-01",
                "doi": "10.1038/s41558-023-01234-5",
                "keywords": ["machine learning", "climate modeling", "neural networks"]
            }
        )
        print(f"✓ Stored document memory with ID: {doc_memory_id}")
        
        print("\n4. Storing Video Content")
        print("-" * 40)
        
        # Store video memory
        video_memory_id = memory_system.add_media_content(
            session_id=session_id,
            content="Educational video explaining quantum computing principles. "
                   "Covers qubits, superposition, entanglement, and quantum gates. "
                   "Features animations and expert interviews. Suitable for undergraduate level.",
            media_type=MediaType.VIDEO,
            metadata={
                "filename": "quantum_computing_intro.mp4",
                "format": "MP4",
                "duration": "23:45",
                "resolution": "4K",
                "framerate": "60fps",
                "instructor": "Dr. Alice Quantum",
                "university": "MIT",
                "course": "Physics 8.04",
                "chapter": "Introduction to Quantum Mechanics"
            }
        )
        print(f"✓ Stored video memory with ID: {video_memory_id}")
        
        print("\n5. Creating Knowledge Graph Connections")
        print("-" * 40)
        
        # Create knowledge nodes for the media content
        image_node = memory_system.add_knowledge_node(
            session_id, "Mountain Sunset Photography", "media_content",
            importance_score=0.7,
            metadata={"media_id": image_memory_id, "type": "visual"}
        )
        
        doc_node = memory_system.add_knowledge_node(
            session_id, "Climate ML Research", "academic_content", 
            importance_score=0.9,
            metadata={"media_id": doc_memory_id, "type": "research"}
        )
        
        # Create relationships between different media types
        memory_system.add_knowledge_relation(
            image_node, doc_node, "related_to",
            confidence=0.6,
            metadata={"reason": "Both involve nature/environment themes"}
        )
        
        print("✓ Created cross-modal knowledge relationships")
        
        print("\n6. Searching Across Media Types")
        print("-" * 40)
        
        # Search for nature-related content
        nature_results = memory_system.search_media_content(
            session_id=session_id,
            media_types=[MediaType.IMAGE, MediaType.DOCUMENT],
            query="mountains nature environment",
            limit=3
        )
        print(f"Nature search found {len(nature_results)} results:")
        for result in nature_results:
            media_type = result.get('media_type', 'unknown')
            print(f"  - {media_type.upper()}: Content found")
        
        # Search for educational content
        educational_results = memory_system.search_media_content(
            session_id=session_id,
            media_types=[MediaType.VIDEO, MediaType.AUDIO],
            query="educational learning science",
            limit=3
        )
        print(f"\nEducational search found {len(educational_results)} results:")
        for result in educational_results:
            media_type = result.get('media_type', 'unknown')
            print(f"  - {media_type.upper()}: Content found")
        
        print("\n7. Multi-Modal Content Analysis")
        print("-" * 40)
        
        # Analyze content patterns across media types
        all_media = memory_system.search_media_content(
            session_id=session_id,
            limit=10
        )
        media_types = {}
        
        for media in all_media:
            media_type = media.get('media_type', 'unknown')
            media_types[media_type] = media_types.get(media_type, 0) + 1
        
        print("Content distribution by media type:")
        for media_type, count in media_types.items():
            print(f"  - {media_type.capitalize()}: {count} items")
        
        print("\n8. Demonstrating Auto-Summarization")
        print("-" * 40)
        
        # Create a large content piece and summarize it
        large_content = """
        This is a comprehensive multi-modal dataset containing various types of media files.
        The dataset includes high-quality photographs of natural landscapes, specifically 
        focusing on mountain ranges and sunset photography. The images were captured using
        professional camera equipment and showcase excellent composition and lighting.
        
        Audio content consists of live jazz performances recorded at prestigious venues.
        The recordings feature skilled musicians performing classic jazz standards with
        modern interpretations. Audio quality is exceptional with clear separation of
        instruments and minimal background noise.
        
        Document collection includes peer-reviewed research papers on cutting-edge topics
        in climate science and machine learning. These academic works represent significant
        contributions to their respective fields and include extensive citations and
        methodology descriptions.
        
        Video content provides educational material suitable for university-level courses.
        The videos feature expert instructors explaining complex scientific concepts using
        visual aids and demonstrations. Production quality is professional with clear
        audio and high-definition video.
        """
        
        summary_memory_id = memory_system.add_message(
            session_id=session_id,
            content=large_content,
            message_type=MessageType.SYSTEM,
            metadata={"source": "dataset_description", "auto_summarize": True}
        )
        
        print("✓ Added large content for summarization")
        
        print("\n9. Memory Consolidation Demonstration")
        print("-" * 40)
        
        # Trigger memory consolidation
        consolidation_job_id = memory_system.start_memory_consolidation(
            session_id=session_id,
            job_type="full"
        )
        
        # Check consolidation status
        status = memory_system.get_consolidation_status(consolidation_job_id)
        print(f"✓ Started consolidation job: {consolidation_job_id}")
        print(f"✓ Status: {status.get('status', 'unknown')}")
        
        print("\n10. Knowledge Graph Analysis")
        print("-" * 40)
        
        # Get the knowledge graph
        graph = memory_system.get_knowledge_graph(session_id=session_id)
        print(f"Knowledge graph contains:")
        print(f"  - {graph['stats']['total_nodes']} nodes")
        print(f"  - {graph['stats']['total_relations']} relationships")
        print(f"  - Node types: {graph['stats']['node_types']}")
        
        print("\n=== Multi-Modal Example Complete ===")
        print("✓ Successfully demonstrated:")
        print("  - Image processing and storage")
        print("  - Audio content management")
        print("  - Document handling")
        print("  - Video content processing")
        print("  - Cross-modal knowledge relationships")
        print("  - Multi-type semantic search")
        print("  - Auto-summarization")
        print("  - Memory consolidation")
        print("  - Knowledge graph analysis")
        
    except Exception as e:
        logger.error(f"Error in multi-modal example: {e}")
        raise
    
    finally:
        memory_system.close()

def demonstrate_file_processing():
    """
    Demonstrate processing of actual files (when available).
    """
    print("\n=== File Processing Example ===")
    
    memory_system = AdvancedMemorySystem("file_processing_memory.db")
    
    try:
        # This would be used with actual files
        sample_files = [
            {"path": "documents/report.pdf", "type": "document"},
            {"path": "images/photo.jpg", "type": "image"},
            {"path": "audio/recording.mp3", "type": "audio"},
            {"path": "videos/tutorial.mp4", "type": "video"}
        ]
        
        print("File processing workflow (simulated):")
        for file_info in sample_files:
            print(f"  1. Detect file type: {file_info['type']}")
            print(f"  2. Extract metadata from: {file_info['path']}")
            print(f"  3. Generate embeddings for content")
            print(f"  4. Store in memory system")
            print(f"  5. Create knowledge relationships")
            print()
        
        print("✓ File processing workflow demonstrated")
        
    finally:
        memory_system.close()

if __name__ == "__main__":
    # Run the multi-modal example
    multimodal_example()
    
    # Run the file processing demonstration
    demonstrate_file_processing()
