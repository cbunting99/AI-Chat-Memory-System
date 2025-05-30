"""
File: embedding_manager.py
Description: Vector embeddings functionality for semantic search using sentence transformers and similarity calculations

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Vector embeddings functionality for semantic search."""

import numpy as np
import pickle
import logging
from typing import List, Optional, Tuple, Dict, Any

# Vector embeddings support
try:
    from sentence_transformers import SentenceTransformer
    import torch
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class EmbeddingManager:
    """Manages vector embeddings for semantic search."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', enable_embeddings: bool = True):
        self.enable_embeddings = enable_embeddings and EMBEDDINGS_AVAILABLE
        self.model_name = model_name
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        if self.enable_embeddings:
            try:
                self.model = SentenceTransformer(model_name)
                self.logger.info(f"Loaded embedding model: {model_name}")
            except Exception as e:
                self.logger.warning(f"Failed to load embedding model: {e}")
                self.enable_embeddings = False
    
    def generate_embedding(self, text: str) -> Optional[bytes]:
        """Generate embedding for text."""
        if not self.enable_embeddings or not self.model:
            return None
        
        try:
            embedding = self.model.encode([text])[0]
            return pickle.dumps(embedding.astype(np.float32))
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return None
    
    def deserialize_embedding(self, embedding_bytes: bytes) -> Optional[np.ndarray]:
        """Deserialize embedding from bytes."""
        try:
            return pickle.loads(embedding_bytes)
        except Exception as e:
            self.logger.error(f"Error deserializing embedding: {e}")
            return None
    
    def calculate_similarity(self, embedding1: bytes, embedding2: bytes) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            emb1 = self.deserialize_embedding(embedding1)
            emb2 = self.deserialize_embedding(embedding2)
            
            if emb1 is None or emb2 is None:
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def semantic_search(self, db_conn, session_id: str, query: str, 
                       search_types: List[str] = None, limit: int = 10,
                       min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """Perform semantic search across conversations, files, and summaries."""
        if not self.enable_embeddings:
            self.logger.warning("Embeddings not available for semantic search")
            return []
        
        if search_types is None:
            search_types = ['conversations', 'files', 'summaries']
        
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        results = []
        cursor = db_conn.cursor()
        
        # Search conversations
        if 'conversations' in search_types:
            cursor.execute('''SELECT conversation_id, content, message_type, timestamp, 
                                   embedding, metadata
                            FROM conversations 
                            WHERE session_id = ? AND embedding IS NOT NULL 
                            AND is_deleted = FALSE''', (session_id,))
            
            for row in cursor.fetchall():
                if row[4]:  # Has embedding
                    similarity = self.calculate_similarity(query_embedding, row[4])
                    if similarity >= min_similarity:
                        results.append({
                            'type': 'conversation',
                            'id': row[0],
                            'content': row[1],
                            'message_type': row[2],
                            'timestamp': row[3],
                            'similarity': similarity,
                            'metadata': row[5]
                        })
        
        # Search files
        if 'files' in search_types:
            cursor.execute('''SELECT file_id, file_name, content, created_at, 
                                   embedding, metadata
                            FROM file_contexts 
                            WHERE session_id = ? AND embedding IS NOT NULL 
                            AND is_deleted = FALSE''', (session_id,))
            
            for row in cursor.fetchall():
                if row[4]:  # Has embedding
                    similarity = self.calculate_similarity(query_embedding, row[4])
                    if similarity >= min_similarity:
                        results.append({
                            'type': 'file',
                            'id': row[0],
                            'name': row[1],
                            'content': row[2],
                            'timestamp': row[3],
                            'similarity': similarity,
                            'metadata': row[5]
                        })
        
        # Search summaries
        if 'summaries' in search_types:
            cursor.execute('''SELECT summary_id, summary_type, summary, created_at, 
                                   embedding, metadata
                            FROM summaries 
                            WHERE session_id = ? AND embedding IS NOT NULL 
                            AND is_deleted = FALSE''', (session_id,))
            
            for row in cursor.fetchall():
                if row[4]:  # Has embedding
                    similarity = self.calculate_similarity(query_embedding, row[4])
                    if similarity >= min_similarity:
                        results.append({
                            'type': 'summary',
                            'id': row[0],
                            'summary_type': row[1],
                            'content': row[2],
                            'timestamp': row[3],
                            'similarity': similarity,
                            'metadata': row[5]
                        })
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
