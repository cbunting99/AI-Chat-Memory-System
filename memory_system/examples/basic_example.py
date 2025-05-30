"""
File: basic_example.py
Description: Basic usage example of the Advanced Memory System demonstrating core functionality like creating sessions, adding messages, and basic search

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""
Basic usage example of the Advanced Memory System.

This example demonstrates core functionality like creating sessions,
adding messages, and basic search.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system import AdvancedMemorySystem, MessageType

def basic_example():
    """Basic usage example."""
    print("=== Basic Advanced Memory System Example ===")
    
    # Initialize the memory system
    memory = AdvancedMemorySystem(
        db_path='example_basic.db',
        enable_embeddings=False,  # Disable for basic example
        auto_summarize=False
    )
    
    try:
        # Create a session
        session_id = memory.create_session(
            user_id="user123",
            session_name="Basic Example Session"
        )
        print(f"Created session: {session_id}")
        
        # Add some messages
        msg1_id = memory.add_message(
            session_id=session_id,
            content="Hello, I need help with Python programming.",
            message_type=MessageType.USER
        )
        print(f"Added user message: {msg1_id}")
        
        msg2_id = memory.add_message(
            session_id=session_id,
            content="I'd be happy to help you with Python! What specific topic would you like to learn about?",
            message_type=MessageType.ASSISTANT
        )
        print(f"Added assistant message: {msg2_id}")
        
        msg3_id = memory.add_message(
            session_id=session_id,
            content="I want to learn about list comprehensions and how to use them effectively.",
            message_type=MessageType.USER
        )
        print(f"Added user message: {msg3_id}")
        
        # Add a file context
        code_content = """
# List comprehension examples
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
even_squares = [x**2 for x in numbers if x % 2 == 0]
"""
        
        file_id = memory.add_file_context(
            session_id=session_id,
            file_name="list_comprehensions.py",
            content=code_content,
            mime_type="text/x-python"
        )
        print(f"Added file context: {file_id}")
        
        # Search conversations
        search_results = memory.search_conversations(
            session_id=session_id,
            query="Python",
            limit=5
        )
        print(f"\nSearch results for 'Python': {len(search_results)} found")
        for result in search_results:
            print(f"  - {result['type']}: {result['content'][:50]}...")
        
        # Get session context
        context = memory.get_intelligent_context(session_id)
        print(f"\nSession context: {context['total_tokens']} tokens")
        print(f"  - Conversations: {len(context['conversations'])}")
        print(f"  - Files: {len(context['files'])}")
        
        # Get session statistics
        stats = memory.get_session_stats(session_id)
        print(f"\nSession Statistics:")
        print(f"  - Total messages: {stats['total_messages']}")
        print(f"  - Total tokens: {stats['total_tokens']}")
        print(f"  - Files: {stats['file_count']}")
        
    finally:
        memory.close()
    
    print("Basic example completed successfully!")

if __name__ == "__main__":
    basic_example()
