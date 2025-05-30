"""
File: memory_system.py
Description: Advanced Memory System main class integrating all components including vector embeddings, knowledge graphs, auto-summarization, multi-modal content support, and memory consolidation

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Advanced Memory System - Main class integrating all components."""

import uuid
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union

from .types import MessageType, CompressionLevel, MediaType, SummaryTrigger
from .models import Message, MediaContent, KnowledgeNode, KnowledgeRelation
from ..utils.database import DatabaseManager
from ..embeddings.embedding_manager import EmbeddingManager
from ..knowledge.knowledge_graph import KnowledgeGraphManager
from ..summarization.summarization_manager import SummarizationManager
from ..multimodal.multimodal_manager import MultiModalManager
from ..consolidation.consolidation_manager import ConsolidationManager


class AdvancedMemorySystem:
    """Advanced Memory System with multi-modal support, knowledge graphs, and auto-summarization."""
    
    def __init__(self, db_path='advanced_memory.db', enable_compression=True, 
                 enable_embeddings=False, max_context_tokens=100000,
                 auto_summarize=True, embedding_model='all-MiniLM-L6-v2'):
        """Initialize the Advanced Memory System.
        
        Args:
            db_path: Path to SQLite database file
            enable_compression: Enable content compression
            enable_embeddings: Enable vector embeddings for semantic search
            max_context_tokens: Maximum tokens before triggering auto-summarization
            auto_summarize: Enable automatic summarization
            embedding_model: Sentence transformer model for embeddings
        """
        self.db_path = db_path
        self.enable_compression = enable_compression
        self.max_context_tokens = max_context_tokens
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.create_tables()
        self.db_manager.create_indexes()
        
        # Initialize components
        self.embedding_manager = EmbeddingManager(embedding_model, enable_embeddings)
        self.knowledge_manager = KnowledgeGraphManager(self.db_manager.conn, self.embedding_manager)
        self.summarization_manager = SummarizationManager(
            self.db_manager.conn, max_context_tokens, auto_summarize
        )
        self.multimodal_manager = MultiModalManager(self.db_manager.conn, self.embedding_manager)
        self.consolidation_manager = ConsolidationManager(self.db_manager.conn)
        
        self.logger.info("Advanced Memory System initialized successfully")

    # === CORE FUNCTIONALITY ===
    
    def create_session(self, user_id: str = None, session_name: str = None) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        cursor = self.db_manager.conn.cursor()
        cursor.execute('''INSERT INTO sessions (session_id, user_id, session_name)
                        VALUES (?, ?, ?)''', (session_id, user_id, session_name))
        self.db_manager.conn.commit()
        self.logger.info(f"Created session {session_id}")
        return session_id

    def add_message(self, session_id: str, content: str, message_type: MessageType,
                   role: str = None, parent_id: str = None, thread_id: str = None,
                   metadata: Dict[str, Any] = None, tokens: int = None) -> str:
        """Add a message to the conversation."""
        message_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Generate embedding if enabled
        embedding = self.embedding_manager.generate_embedding(content)
        
        # Calculate tokens if not provided (simple estimation)
        if tokens is None:
            tokens = len(content.split()) * 1.3  # Rough token estimation
        
        cursor = self.db_manager.conn.cursor()
        cursor.execute('''INSERT INTO conversations 
                        (conversation_id, session_id, content, content_hash, message_type, 
                         role, parent_id, thread_id, tokens, embedding, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (message_id, session_id, content, content_hash, message_type.value,
                       role, parent_id, thread_id, tokens, embedding, 
                       json.dumps(metadata) if metadata else None))
        
        # Update session stats
        cursor.execute('''UPDATE sessions 
                        SET last_active = CURRENT_TIMESTAMP,
                            total_messages = total_messages + 1,
                            total_tokens = total_tokens + ?
                        WHERE session_id = ?''', (tokens, session_id))
        
        self.db_manager.conn.commit()
        
        # Auto-extract knowledge if this is a significant message
        if len(content) > 50:  # Only for substantial content
            self.knowledge_manager.extract_knowledge_from_conversation(session_id, message_id)
        
        # Check for auto-summarization trigger
        self.summarization_manager.trigger_auto_summarization(session_id)
        
        self.logger.info(f"Added message {message_id} to session {session_id}")
        return message_id

    def add_file_context(self, session_id: str, file_name: str, content: str,
                        file_path: str = None, mime_type: str = None,
                        metadata: Dict[str, Any] = None) -> str:
        """Add file context to the session."""
        file_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Generate embedding
        embedding = self.embedding_manager.generate_embedding(content)
        
        cursor = self.db_manager.conn.cursor()
        cursor.execute('''INSERT INTO file_contexts 
                        (file_id, session_id, file_name, content, content_hash,
                         file_path, mime_type, file_size, embedding, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (file_id, session_id, file_name, content, content_hash,
                       file_path, mime_type, len(content.encode()),
                       embedding, json.dumps(metadata) if metadata else None))
        self.db_manager.conn.commit()
        
        self.logger.info(f"Added file context {file_id}")
        return file_id

    def create_summary(self, session_id: str, summary_type: str, summary: str,
                      conversation_id: str = None, token_range: Tuple[int, int] = None,
                      importance_score: float = 0.5, expires_hours: int = None) -> str:
        """Create a summary."""
        return self.summarization_manager._create_summary(
            session_id, summary_type, summary, conversation_id,
            token_range, importance_score, expires_hours
        )

    def get_intelligent_context(self, session_id: str, max_tokens: int = None,
                               include_files: bool = True, include_summaries: bool = True) -> Dict[str, Any]:
        """Get intelligent context for the session."""
        if max_tokens is None:
            max_tokens = self.max_context_tokens
        
        cursor = self.db_manager.conn.cursor()
        context = {
            'conversations': [],
            'files': [],
            'summaries': [],
            'total_tokens': 0
        }
        
        current_tokens = 0
        
        # Get recent conversations
        cursor.execute('''SELECT conversation_id, content, message_type, timestamp, tokens, metadata
                         FROM conversations 
                         WHERE session_id = ? AND is_deleted = FALSE
                         ORDER BY timestamp DESC''', (session_id,))
        
        for row in cursor.fetchall():
            msg_tokens = row[4] or len(row[1].split()) * 1.3
            if current_tokens + msg_tokens > max_tokens:
                break
            
            context['conversations'].append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'timestamp': row[3],
                'tokens': msg_tokens,
                'metadata': json.loads(row[5]) if row[5] else {}
            })
            current_tokens += msg_tokens
        
        # Add file contexts if enabled and space available
        if include_files and current_tokens < max_tokens:
            cursor.execute('''SELECT file_id, file_name, content, created_at, metadata
                             FROM file_contexts 
                             WHERE session_id = ? AND is_deleted = FALSE
                             ORDER BY created_at DESC''', (session_id,))
            
            for row in cursor.fetchall():
                file_tokens = len(row[2].split()) * 1.3
                if current_tokens + file_tokens > max_tokens:
                    break
                
                context['files'].append({
                    'id': row[0],
                    'name': row[1],
                    'content': row[2][:1000],  # Truncate for context
                    'timestamp': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {}
                })
                current_tokens += file_tokens
        
        # Add summaries if enabled and space available
        if include_summaries and current_tokens < max_tokens:
            cursor.execute('''SELECT summary_id, summary_type, summary, created_at, importance_score
                             FROM summaries 
                             WHERE session_id = ? AND is_deleted = FALSE
                             AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                             ORDER BY importance_score DESC, created_at DESC''', (session_id,))
            
            for row in cursor.fetchall():
                summary_tokens = len(row[2].split()) * 1.3
                if current_tokens + summary_tokens > max_tokens:
                    break
                
                context['summaries'].append({
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'timestamp': row[3],
                    'importance': row[4]
                })
                current_tokens += summary_tokens

        context['total_tokens'] = current_tokens
        return context

    # === SEARCH FUNCTIONALITY ===
    
    def search_conversations(self, session_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Search conversations using text matching."""
        cursor = self.db_manager.conn.cursor()
        cursor.execute('''SELECT conversation_id, content, message_type, timestamp, 
                               (CASE WHEN content LIKE ? THEN 2 ELSE 1 END) as relevance
                        FROM conversations 
                        WHERE session_id = ? AND content LIKE ? AND is_deleted = FALSE
                        ORDER BY relevance DESC, timestamp DESC
                        LIMIT ?''', 
                      (f'%{query}%', session_id, f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'timestamp': row[3],
                'relevance': row[4]
            })
        return results

    def semantic_search(self, session_id: str, query: str, 
                       search_types: List[str] = None, limit: int = 10,
                       min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings."""
        return self.embedding_manager.semantic_search(
            self.db_manager.conn, session_id, query, search_types, limit, min_similarity
        )

    # === KNOWLEDGE GRAPH FUNCTIONALITY ===
    
    def add_knowledge_node(self, session_id: str, content: str, node_type: str,
                          importance_score: float = 0.5, metadata: Dict[str, Any] = None) -> str:
        """Add a knowledge node."""
        return self.knowledge_manager.add_knowledge_node(
            session_id, content, node_type, importance_score, metadata
        )

    def add_knowledge_relation(self, source_node_id: str, target_node_id: str,
                              relation_type: str, confidence: float = 1.0,
                              strength: float = 1.0, metadata: Dict[str, Any] = None) -> str:
        """Add a knowledge relation."""
        return self.knowledge_manager.add_knowledge_relation(
            source_node_id, target_node_id, relation_type, confidence, strength, metadata
        )

    def get_knowledge_graph(self, session_id: str, node_types: List[str] = None,
                           min_importance: float = 0.0) -> Dict[str, Any]:
        """Get knowledge graph."""
        return self.knowledge_manager.get_knowledge_graph(session_id, node_types, min_importance)

    def find_related_concepts(self, session_id: str, concept: str, max_depth: int = 2) -> List[Dict]:
        """Find related concepts."""
        return self.knowledge_manager.find_related_concepts(session_id, concept, max_depth)

    # === MULTI-MODAL FUNCTIONALITY ===
    
    def add_media_content(self, session_id: str, content: Union[str, bytes], 
                         media_type: MediaType, file_path: str = None,
                         encoding: str = None, metadata: Dict[str, Any] = None) -> str:
        """Add multi-modal content."""
        return self.multimodal_manager.add_media_content(
            session_id, content, media_type, file_path, encoding, metadata
        )

    def search_media_content(self, session_id: str, media_types: List[MediaType] = None,
                           query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search multi-modal content."""
        return self.multimodal_manager.search_media_content(
            session_id, media_types, query, limit
        )

    # === CONSOLIDATION FUNCTIONALITY ===
    
    def start_memory_consolidation(self, session_id: str, job_type: str = "full") -> str:
        """Start memory consolidation."""
        return self.consolidation_manager.start_memory_consolidation(session_id, job_type)

    def get_consolidation_status(self, job_id: str) -> Dict[str, Any]:
        """Get consolidation job status."""
        return self.consolidation_manager.get_consolidation_status(job_id)

    # === AUTO-SUMMARIZATION FUNCTIONALITY ===
    
    def trigger_auto_summarization(self, session_id: str) -> Optional[str]:
        """Trigger auto-summarization."""
        return self.summarization_manager.trigger_auto_summarization(session_id)

    # === UTILITY FUNCTIONS ===
    
    def cleanup_old_data(self, days_old: int = 30, keep_important: bool = True):
        """Clean up old data."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cursor = self.db_manager.conn.cursor()

        if keep_important:
            # Only delete non-important data
            cursor.execute('''UPDATE conversations SET is_deleted = TRUE 
                            WHERE timestamp < ? AND is_deleted = FALSE 
                            AND (metadata IS NULL OR json_extract(metadata, '$.importance') < 0.7)''', 
                          (cutoff_date,))
        else:
            # Delete all old data
            cursor.execute('''UPDATE conversations SET is_deleted = TRUE 
                            WHERE timestamp < ? AND is_deleted = FALSE''', (cutoff_date,))

        # Clean up expired summaries
        cursor.execute('UPDATE summaries SET is_deleted = TRUE WHERE expires_at < ?', (datetime.now(),))
        
        # Archive old sessions instead of deleting
        cursor.execute('''UPDATE sessions SET is_archived = TRUE 
                        WHERE last_active < ? AND is_archived = FALSE''', (cutoff_date,))
        
        self.db_manager.conn.commit()
        self.logger.info(f"Cleaned up data older than {days_old} days")

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        cursor = self.db_manager.conn.cursor()
        
        # Basic session info
        cursor.execute('''SELECT user_id, session_name, created_at, last_active, 
                               total_messages, total_tokens, is_archived
                        FROM sessions WHERE session_id = ?''', (session_id,))
        session_data = cursor.fetchone()
        
        if not session_data:
            return {"error": "Session not found"}

        # Message type breakdown
        cursor.execute('''SELECT message_type, COUNT(*), SUM(tokens)
                        FROM conversations 
                        WHERE session_id = ? AND is_deleted = FALSE
                        GROUP BY message_type''', (session_id,))
        message_stats = cursor.fetchall()

        # File count
        cursor.execute('SELECT COUNT(*) FROM file_contexts WHERE session_id = ?', (session_id,))
        file_count = cursor.fetchone()[0]

        # Summary count
        cursor.execute('SELECT COUNT(*) FROM summaries WHERE session_id = ?', (session_id,))
        summary_count = cursor.fetchone()[0]

        # Knowledge graph stats
        cursor.execute('SELECT COUNT(*) FROM knowledge_nodes WHERE session_id = ?', (session_id,))
        knowledge_nodes = cursor.fetchone()[0]

        # Media content stats
        cursor.execute('''SELECT media_type, COUNT(*) FROM media_contents 
                         WHERE session_id = ? GROUP BY media_type''', (session_id,))
        media_stats = cursor.fetchall()

        return {
            'session_id': session_id,
            'user_id': session_data[0],
            'session_name': session_data[1],
            'created_at': session_data[2],
            'last_active': session_data[3],
            'total_messages': session_data[4],
            'total_tokens': session_data[5],
            'is_archived': session_data[6],
            'message_breakdown': {row[0]: {'count': row[1], 'tokens': row[2]} for row in message_stats},
            'file_count': file_count,
            'summary_count': summary_count,
            'knowledge_nodes': knowledge_nodes,
            'media_breakdown': {row[0]: row[1] for row in media_stats}
        }

    def close(self):
        """Close the memory system."""
        self.db_manager.close()
        self.logger.info("Advanced Memory System closed")
