"""
File: consolidation_manager.py
Description: Memory consolidation functionality for merging similar conversations, compressing old data, and optimizing stored information

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Memory consolidation functionality for merging and optimizing stored data."""

import uuid
import json
import hashlib
import gzip
import logging
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Tuple


class ConsolidationManager:
    """Manages memory consolidation operations."""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.consolidation_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def start_memory_consolidation(self, session_id: str, job_type: str = "full") -> str:
        """Start a memory consolidation job."""
        job_id = str(uuid.uuid4())
        
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO consolidation_jobs
                        (job_id, session_id, job_type, status, metadata)
                        VALUES (?, ?, ?, ?, ?)''',
                      (job_id, session_id, job_type, "running", 
                       json.dumps({"started_by": "user", "type": job_type})))
        self.db_conn.commit()
        
        # Start consolidation in background
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self._run_consolidation_job, job_id, session_id, job_type)
        
        self.logger.info(f"Started consolidation job {job_id} for session {session_id}")
        return job_id

    def _run_consolidation_job(self, job_id: str, session_id: str, job_type: str):
        """Run the actual consolidation process."""
        try:
            with self.consolidation_lock:
                cursor = self.db_conn.cursor()
                
                # Update job status
                cursor.execute('''UPDATE consolidation_jobs 
                                SET status = 'processing', progress = 0.1 
                                WHERE job_id = ?''', (job_id,))
                self.db_conn.commit()
                
                results = {}
                
                if job_type in ["full", "merge_conversations"]:
                    merged_count = self._merge_similar_conversations(session_id)
                    results["merged_conversations"] = merged_count
                    
                    cursor.execute('''UPDATE consolidation_jobs 
                                    SET progress = 0.3 WHERE job_id = ?''', (job_id,))
                    self.db_conn.commit()
                
                if job_type in ["full", "compress_old"]:
                    compressed_count = self._compress_old_messages(session_id)
                    results["compressed_messages"] = compressed_count
                    
                    cursor.execute('''UPDATE consolidation_jobs 
                                    SET progress = 0.5 WHERE job_id = ?''', (job_id,))
                    self.db_conn.commit()
                
                if job_type in ["full", "merge_knowledge"]:
                    merged_nodes = self._merge_similar_knowledge_nodes(session_id)
                    results["merged_knowledge_nodes"] = merged_nodes
                    
                    cursor.execute('''UPDATE consolidation_jobs 
                                    SET progress = 0.7 WHERE job_id = ?''', (job_id,))
                    self.db_conn.commit()
                
                if job_type in ["full", "optimize_summaries"]:
                    optimized_summaries = self._optimize_summaries(session_id)
                    results["optimized_summaries"] = optimized_summaries
                    
                    cursor.execute('''UPDATE consolidation_jobs 
                                    SET progress = 0.9 WHERE job_id = ?''', (job_id,))
                    self.db_conn.commit()
                
                # Complete the job
                cursor.execute('''UPDATE consolidation_jobs 
                                SET status = 'completed', progress = 1.0, 
                                    completed_at = CURRENT_TIMESTAMP,
                                    result_summary = ?
                                WHERE job_id = ?''', 
                              (json.dumps(results), job_id))
                self.db_conn.commit()
                
                self.logger.info(f"Completed consolidation job {job_id}")
                
        except Exception as e:
            cursor = self.db_conn.cursor()
            cursor.execute('''UPDATE consolidation_jobs 
                            SET status = 'failed', 
                                result_summary = ?
                            WHERE job_id = ?''', 
                          (f"Error: {str(e)}", job_id))
            self.db_conn.commit()
            self.logger.error(f"Consolidation job {job_id} failed: {e}")

    def _merge_similar_conversations(self, session_id: str) -> int:
        """Merge similar conversations to reduce redundancy."""
        cursor = self.db_conn.cursor()
        
        # Find conversations with similar content (using hash or embedding similarity)
        cursor.execute('''SELECT conversation_id, content, content_hash, timestamp
                         FROM conversations 
                         WHERE session_id = ? AND is_deleted = FALSE
                         ORDER BY timestamp''', (session_id,))
        
        conversations = cursor.fetchall()
        merged_count = 0
        similarity_threshold = 0.85
        
        # Group similar conversations
        processed = set()
        
        for i, conv1 in enumerate(conversations):
            if conv1[0] in processed:
                continue
                
            similar_group = [conv1]
            
            for j, conv2 in enumerate(conversations[i+1:], i+1):
                if conv2[0] in processed:
                    continue
                
                # Check similarity using content hash first
                if conv1[2] == conv2[2]:  # Same hash
                    similar_group.append(conv2)
                    processed.add(conv2[0])
                else:
                    # Check content similarity (simple approach)
                    similarity = self._calculate_text_similarity(conv1[1], conv2[1])
                    if similarity > similarity_threshold:
                        similar_group.append(conv2)
                        processed.add(conv2[0])
            
            # If we found similar conversations, merge them
            if len(similar_group) > 1:
                self._merge_conversation_group(similar_group)
                merged_count += len(similar_group) - 1
                processed.add(conv1[0])
        
        return merged_count

    def _merge_conversation_group(self, conversations: List[Tuple]):
        """Merge a group of similar conversations."""
        if len(conversations) < 2:
            return
        
        # Keep the earliest conversation, mark others as deleted
        conversations.sort(key=lambda x: x[3])  # Sort by timestamp
        primary_conv = conversations[0]
        
        cursor = self.db_conn.cursor()
        
        # Create a merged content summary
        merged_metadata = {
            "merged_from": [conv[0] for conv in conversations[1:]],
            "merge_timestamp": datetime.now().isoformat(),
            "original_count": len(conversations)
        }
        
        # Update primary conversation with merged metadata
        cursor.execute('''UPDATE conversations 
                        SET metadata = json_set(COALESCE(metadata, '{}'), '$.merged', ?)
                        WHERE conversation_id = ?''',
                      (json.dumps(merged_metadata), primary_conv[0]))
        
        # Mark other conversations as deleted
        for conv in conversations[1:]:
            cursor.execute('''UPDATE conversations 
                            SET is_deleted = TRUE, 
                                metadata = json_set(COALESCE(metadata, '{}'), '$.merged_into', ?)
                            WHERE conversation_id = ?''',
                          (primary_conv[0], conv[0]))
        
        self.db_conn.commit()

    def _compress_old_messages(self, session_id: str, days_old: int = 7) -> int:
        """Compress old messages to save space."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cursor = self.db_conn.cursor()
        
        # Find old messages that aren't already compressed or highly important
        cursor.execute('''SELECT conversation_id, content, compressed_content
                         FROM conversations 
                         WHERE session_id = ? AND timestamp < ? 
                         AND (compressed_content IS NULL OR length(compressed_content) = 0)
                         AND (metadata IS NULL OR json_extract(metadata, '$.importance') < 0.8)
                         AND is_deleted = FALSE''', 
                      (session_id, cutoff_date))
        
        messages = cursor.fetchall()
        compressed_count = 0
        
        for msg_id, content, existing_compressed in messages:
            try:
                # Compress the content
                compressed_data = gzip.compress(content.encode('utf-8'))
                
                # Only update if compression saves significant space
                if len(compressed_data) < len(content.encode('utf-8')) * 0.8:
                    cursor.execute('''UPDATE conversations 
                                    SET compressed_content = ?,
                                        compression_level = 6,
                                        content = ?
                                    WHERE conversation_id = ?''',
                                  (compressed_data, 
                                   content[:200] + "...[compressed]",  # Keep summary
                                   msg_id))
                    compressed_count += 1
            except Exception as e:
                self.logger.error(f"Error compressing message {msg_id}: {e}")
        
        self.db_conn.commit()
        return compressed_count

    def _merge_similar_knowledge_nodes(self, session_id: str) -> int:
        """Merge similar knowledge nodes."""
        cursor = self.db_conn.cursor()
        
        # Find similar knowledge nodes
        cursor.execute('''SELECT node_id, content, node_type, importance_score
                         FROM knowledge_nodes 
                         WHERE session_id = ? AND is_deleted = FALSE
                         ORDER BY node_type, importance_score DESC''', (session_id,))
        
        nodes = cursor.fetchall()
        merged_count = 0
        processed = set()
        
        for i, node1 in enumerate(nodes):
            if node1[0] in processed:
                continue
                
            similar_group = [node1]
            
            for j, node2 in enumerate(nodes[i+1:], i+1):
                if node2[0] in processed or node1[2] != node2[2]:  # Different types
                    continue
                
                # Check content similarity
                similarity = self._calculate_text_similarity(node1[1], node2[1])
                if similarity > 0.9:  # High threshold for knowledge nodes
                    similar_group.append(node2)
                    processed.add(node2[0])
            
            if len(similar_group) > 1:
                self._merge_knowledge_node_group(similar_group)
                merged_count += len(similar_group) - 1
                processed.add(node1[0])
        
        return merged_count

    def _merge_knowledge_node_group(self, nodes: List[Tuple]):
        """Merge a group of similar knowledge nodes."""
        if len(nodes) < 2:
            return
        
        # Keep the node with highest importance
        nodes.sort(key=lambda x: x[3], reverse=True)  # Sort by importance
        primary_node = nodes[0]
        
        cursor = self.db_conn.cursor()
        
        # Update primary node metadata
        merged_metadata = {
            "merged_from": [node[0] for node in nodes[1:]],
            "merge_timestamp": datetime.now().isoformat(),
            "original_count": len(nodes)
        }
        
        # Update relations to point to primary node
        for node in nodes[1:]:
            # Update source relations
            cursor.execute('''UPDATE knowledge_relations 
                            SET source_node_id = ? 
                            WHERE source_node_id = ?''',
                          (primary_node[0], node[0]))
            
            # Update target relations
            cursor.execute('''UPDATE knowledge_relations 
                            SET target_node_id = ? 
                            WHERE target_node_id = ?''',
                          (primary_node[0], node[0]))
            
            # Mark node as deleted
            cursor.execute('''UPDATE knowledge_nodes 
                            SET is_deleted = TRUE,
                                metadata = json_set(COALESCE(metadata, '{}'), '$.merged_into', ?)
                            WHERE node_id = ?''',
                          (primary_node[0], node[0]))
        
        # Update primary node with merged metadata
        cursor.execute('''UPDATE knowledge_nodes 
                        SET metadata = json_set(COALESCE(metadata, '{}'), '$.merged', ?)
                        WHERE node_id = ?''',
                      (json.dumps(merged_metadata), primary_node[0]))
        
        self.db_conn.commit()

    def _optimize_summaries(self, session_id: str) -> int:
        """Optimize summaries by removing expired and merging overlapping ones."""
        cursor = self.db_conn.cursor()
        optimized_count = 0
        
        # Remove expired summaries
        cursor.execute('''UPDATE summaries 
                         SET is_deleted = TRUE 
                         WHERE session_id = ? AND expires_at < ? AND is_deleted = FALSE''',
                      (session_id, datetime.now()))
        expired_count = cursor.rowcount
        
        # Find overlapping summaries
        cursor.execute('''SELECT summary_id, summary_type, summary, created_at, importance_score
                         FROM summaries 
                         WHERE session_id = ? AND is_deleted = FALSE
                         ORDER BY created_at''', (session_id,))
        
        summaries = cursor.fetchall()
        processed = set()
        
        for i, summary1 in enumerate(summaries):
            if summary1[0] in processed:
                continue
                
            overlapping_group = [summary1]
            
            for j, summary2 in enumerate(summaries[i+1:], i+1):
                if summary2[0] in processed or summary1[1] != summary2[1]:  # Different types
                    continue
                
                # Check if summaries are from similar time periods
                time1 = datetime.fromisoformat(summary1[3])
                time2 = datetime.fromisoformat(summary2[3])
                
                if abs((time2 - time1).total_seconds()) < 3600:  # Within 1 hour
                    overlapping_group.append(summary2)
                    processed.add(summary2[0])
            
            if len(overlapping_group) > 1:
                self._merge_summary_group(overlapping_group)
                optimized_count += len(overlapping_group) - 1
                processed.add(summary1[0])
        
        self.db_conn.commit()
        return optimized_count + expired_count

    def _merge_summary_group(self, summaries: List[Tuple]):
        """Merge a group of overlapping summaries."""
        if len(summaries) < 2:
            return
        
        # Keep the summary with highest importance
        summaries.sort(key=lambda x: x[4], reverse=True)  # Sort by importance
        primary_summary = summaries[0]
        
        cursor = self.db_conn.cursor()
        
        # Combine content
        combined_content = f"{primary_summary[2]}\n\n"
        for summary in summaries[1:]:
            combined_content += f"Additional context: {summary[2]}\n"
        
        # Update primary summary
        cursor.execute('''UPDATE summaries 
                        SET summary = ?,
                            metadata = json_set(COALESCE(metadata, '{}'), '$.merged_from', ?)
                        WHERE summary_id = ?''',
                      (combined_content,
                       json.dumps([s[0] for s in summaries[1:]]),
                       primary_summary[0]))
        
        # Mark other summaries as deleted
        for summary in summaries[1:]:
            cursor.execute('''UPDATE summaries 
                            SET is_deleted = TRUE 
                            WHERE summary_id = ?''', (summary[0],))

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using Jaccard similarity."""
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def get_consolidation_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a consolidation job."""
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT job_type, status, progress, started_at, completed_at, result_summary
                         FROM consolidation_jobs 
                         WHERE job_id = ?''', (job_id,))
        
        result = cursor.fetchone()
        if not result:
            return {"error": "Job not found"}
        
        return {
            "job_id": job_id,
            "job_type": result[0],
            "status": result[1],
            "progress": result[2],
            "started_at": result[3],
            "completed_at": result[4],
            "result_summary": json.loads(result[5]) if result[5] else None
        }
