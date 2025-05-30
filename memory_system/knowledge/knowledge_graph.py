"""
File: knowledge_graph.py
Description: Knowledge graph functionality for tracking relationships between concepts, entities, and extracting knowledge from conversations

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Knowledge graph functionality for relationship tracking."""

import uuid
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from ..core.models import KnowledgeNode, KnowledgeRelation


class KnowledgeGraphManager:
    """Manages knowledge graph operations."""
    
    def __init__(self, db_conn, embedding_manager=None):
        self.db_conn = db_conn
        self.embedding_manager = embedding_manager
        self.logger = logging.getLogger(__name__)
    
    def add_knowledge_node(self, session_id: str, content: str, node_type: str,
                          importance_score: float = 0.5, metadata: Dict[str, Any] = None) -> str:
        """Add a node to the knowledge graph."""
        node_id = str(uuid.uuid4())
        embedding = None
        
        if self.embedding_manager:
            embedding = self.embedding_manager.generate_embedding(content)
        
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO knowledge_nodes
                        (node_id, session_id, content, node_type, importance_score, 
                         embedding, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (node_id, session_id, content, node_type, importance_score,
                       embedding, json.dumps(metadata) if metadata else None))
        self.db_conn.commit()
        self.logger.info(f"Added knowledge node {node_id}")
        return node_id

    def add_knowledge_relation(self, source_node_id: str, target_node_id: str,
                              relation_type: str, confidence: float = 1.0,
                              strength: float = 1.0, metadata: Dict[str, Any] = None) -> str:
        """Add a relation between knowledge nodes."""
        relation_id = str(uuid.uuid4())
        
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO knowledge_relations
                        (relation_id, source_node_id, target_node_id, relation_type,
                         confidence, strength, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (relation_id, source_node_id, target_node_id, relation_type,
                       confidence, strength, json.dumps(metadata) if metadata else None))
        self.db_conn.commit()
        self.logger.info(f"Added knowledge relation {relation_id}")
        return relation_id

    def extract_knowledge_from_conversation(self, session_id: str, conversation_id: str) -> List[str]:
        """Extract knowledge entities and relationships from a conversation."""
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT content FROM conversations WHERE conversation_id = ?', 
                      (conversation_id,))
        
        result = cursor.fetchone()
        if not result:
            return []
        
        content = result[0]
        extracted_nodes = []
        
        # Extract entities (nouns and proper nouns)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        concepts = re.findall(r'\b(?:function|class|method|variable|system|process|algorithm)\b', 
                             content, re.IGNORECASE)
        
        # Add entities as knowledge nodes
        for entity in entities[:5]:  # Limit to avoid spam
            node_id = self.add_knowledge_node(
                session_id, entity, "entity", 
                importance_score=0.6,
                metadata={"source": "auto_extraction", "conversation_id": conversation_id}
            )
            extracted_nodes.append(node_id)
        
        # Add concepts as knowledge nodes
        for concept in set(concepts):  # Remove duplicates
            node_id = self.add_knowledge_node(
                session_id, concept, "concept",
                importance_score=0.7,
                metadata={"source": "auto_extraction", "conversation_id": conversation_id}
            )
            extracted_nodes.append(node_id)
        
        # Create relationships between extracted nodes (co-occurrence)
        for i, node1 in enumerate(extracted_nodes):
            for node2 in extracted_nodes[i+1:]:
                self.add_knowledge_relation(
                    node1, node2, "co_occurs_with",
                    confidence=0.8, strength=0.5,
                    metadata={"source": "auto_extraction"}
                )
        
        return extracted_nodes

    def get_knowledge_graph(self, session_id: str, node_types: List[str] = None,
                           min_importance: float = 0.0) -> Dict[str, Any]:
        """Get knowledge graph for a session."""
        cursor = self.db_conn.cursor()
        
        # Get nodes
        if node_types:
            placeholders = ','.join(['?' for _ in node_types])
            cursor.execute(f'''SELECT node_id, content, node_type, importance_score, metadata
                             FROM knowledge_nodes 
                             WHERE session_id = ? AND node_type IN ({placeholders}) 
                             AND importance_score >= ? AND is_deleted = FALSE''',
                          [session_id] + node_types + [min_importance])
        else:
            cursor.execute('''SELECT node_id, content, node_type, importance_score, metadata
                             FROM knowledge_nodes 
                             WHERE session_id = ? AND importance_score >= ? 
                             AND is_deleted = FALSE''',
                          (session_id, min_importance))
        
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'importance': row[3],
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        
        # Get relations
        node_ids = [node['id'] for node in nodes]
        if node_ids:
            placeholders = ','.join(['?' for _ in node_ids])
            cursor.execute(f'''SELECT relation_id, source_node_id, target_node_id, 
                                    relation_type, confidence, strength, metadata
                             FROM knowledge_relations 
                             WHERE source_node_id IN ({placeholders}) 
                             AND target_node_id IN ({placeholders})
                             AND is_deleted = FALSE''',
                          node_ids + node_ids)
            
            relations = []
            for row in cursor.fetchall():
                relations.append({
                    'id': row[0],
                    'source': row[1],
                    'target': row[2],
                    'type': row[3],
                    'confidence': row[4],
                    'strength': row[5],
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
        else:
            relations = []
        
        return {
            'nodes': nodes,
            'relations': relations,
            'stats': {
                'total_nodes': len(nodes),
                'total_relations': len(relations),
                'node_types': list(set(node['type'] for node in nodes))
            }
        }

    def find_related_concepts(self, session_id: str, concept: str, max_depth: int = 2) -> List[Dict]:
        """Find concepts related to a given concept using the knowledge graph."""
        cursor = self.db_conn.cursor()
        
        # Find the concept node
        cursor.execute('''SELECT node_id FROM knowledge_nodes 
                         WHERE session_id = ? AND content LIKE ? AND is_deleted = FALSE''',
                      (session_id, f'%{concept}%'))
        
        concept_nodes = [row[0] for row in cursor.fetchall()]
        if not concept_nodes:
            return []
        
        related_concepts = []
        visited = set()
        
        def traverse(node_id: str, depth: int):
            if depth > max_depth or node_id in visited:
                return
            
            visited.add(node_id)
            
            # Get directly related nodes
            cursor.execute('''SELECT target_node_id, relation_type, confidence
                             FROM knowledge_relations 
                             WHERE source_node_id = ? AND is_deleted = FALSE
                             UNION
                             SELECT source_node_id, relation_type, confidence
                             FROM knowledge_relations 
                             WHERE target_node_id = ? AND is_deleted = FALSE''',
                          (node_id, node_id))
            
            for related_id, relation_type, confidence in cursor.fetchall():
                if related_id not in visited:
                    # Get node details
                    cursor.execute('''SELECT content, node_type, importance_score
                                     FROM knowledge_nodes 
                                     WHERE node_id = ? AND is_deleted = FALSE''', 
                                  (related_id,))
                    node_data = cursor.fetchone()
                    if node_data:
                        related_concepts.append({
                            'node_id': related_id,
                            'content': node_data[0],
                            'type': node_data[1],
                            'importance': node_data[2],
                            'relation_type': relation_type,
                            'confidence': confidence,
                            'depth': depth + 1
                        })
                        traverse(related_id, depth + 1)
        
        for concept_node in concept_nodes:
            traverse(concept_node, 0)
        
        # Sort by importance and confidence
        related_concepts.sort(key=lambda x: (x['importance'], x['confidence']), reverse=True)
        return related_concepts
