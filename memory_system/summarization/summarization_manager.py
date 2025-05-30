"""
File: summarization_manager.py
Description: Auto-summarization functionality for conversation management with token limits, time-based, and importance-based triggers

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Auto-summarization functionality."""

import json
import re
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any

from ..core.types import SummaryTrigger


class SummarizationManager:
    """Manages automatic summarization of conversations."""
    
    def __init__(self, db_conn, max_context_tokens: int = 100000, auto_summarize: bool = True):
        self.db_conn = db_conn
        self.max_context_tokens = max_context_tokens
        self.auto_summarize = auto_summarize
        self.logger = logging.getLogger(__name__)
    
    def should_trigger_summary(self, session_id: str) -> Tuple[bool, Optional[SummaryTrigger]]:
        """Check if auto-summarization should be triggered."""
        if not self.auto_summarize:
            return False, None
        
        cursor = self.db_conn.cursor()
        
        # Check token limit trigger
        cursor.execute('SELECT total_tokens FROM sessions WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        if result and result[0] > self.max_context_tokens * 0.8:  # 80% threshold
            return True, SummaryTrigger.TOKEN_LIMIT
        
        # Check time-based trigger (daily summaries)
        cursor.execute('''SELECT COUNT(*) FROM summaries 
                         WHERE session_id = ? AND summary_type = 'auto_daily'
                         AND created_at > datetime('now', '-1 day')''', (session_id,))
        
        if cursor.fetchone()[0] == 0:  # No daily summary in last 24 hours
            cursor.execute('''SELECT COUNT(*) FROM conversations 
                             WHERE session_id = ? AND timestamp > datetime('now', '-1 day')
                             AND is_deleted = FALSE''', (session_id,))
            
            if cursor.fetchone()[0] > 10:  # Enough activity for daily summary
                return True, SummaryTrigger.TIME_BASED
        
        # Check importance threshold trigger
        cursor.execute('''SELECT AVG(
                            CASE WHEN metadata LIKE '%"importance"%' 
                            THEN CAST(json_extract(metadata, '$.importance') AS REAL)
                            ELSE 0.5 END
                         ) FROM conversations 
                         WHERE session_id = ? AND timestamp > datetime('now', '-2 hours')
                         AND is_deleted = FALSE''', (session_id,))
        
        result = cursor.fetchone()
        if result and result[0] and result[0] > 0.8:  # High importance threshold
            return True, SummaryTrigger.IMPORTANCE_THRESHOLD
        
        return False, None

    def generate_auto_summary(self, session_id: str, trigger: SummaryTrigger) -> str:
        """Generate automatic summary based on trigger type."""
        cursor = self.db_conn.cursor()
        
        if trigger == SummaryTrigger.TOKEN_LIMIT:
            # Summarize oldest conversations to make room
            cursor.execute('''SELECT content, message_type, timestamp
                             FROM conversations 
                             WHERE session_id = ? AND is_deleted = FALSE
                             ORDER BY timestamp ASC
                             LIMIT 50''', (session_id,))
            
            conversations = cursor.fetchall()
            summary_content = self._create_conversation_summary(conversations)
            summary_type = "auto_token_limit"
            
        elif trigger == SummaryTrigger.TIME_BASED:
            # Daily summary of recent activity
            cursor.execute('''SELECT content, message_type, timestamp, metadata
                             FROM conversations 
                             WHERE session_id = ? AND timestamp > datetime('now', '-1 day')
                             AND is_deleted = FALSE
                             ORDER BY timestamp DESC''', (session_id,))
            
            conversations = cursor.fetchall()
            summary_content = self._create_daily_summary(conversations)
            summary_type = "auto_daily"
            
        elif trigger == SummaryTrigger.IMPORTANCE_THRESHOLD:
            # Summary of high-importance recent conversations
            cursor.execute('''SELECT content, message_type, timestamp, metadata
                             FROM conversations 
                             WHERE session_id = ? AND timestamp > datetime('now', '-2 hours')
                             AND is_deleted = FALSE
                             ORDER BY timestamp DESC''', (session_id,))
            
            conversations = cursor.fetchall()
            summary_content = self._create_importance_summary(conversations)
            summary_type = "auto_importance"
        
        else:
            return ""
        
        # Create the summary
        summary_id = self._create_summary(
            session_id, summary_type, summary_content,
            importance_score=0.9,  # Auto summaries are important
            expires_hours=168  # Expire after 1 week
        )
        
        self.logger.info(f"Auto-generated summary {summary_id} triggered by {trigger.value}")
        return summary_id

    def _create_summary(self, session_id: str, summary_type: str, summary: str,
                       conversation_id: str = None, token_range: Tuple[int, int] = None,
                       importance_score: float = 0.5, expires_hours: int = None) -> str:
        """Create a summary record."""
        summary_id = str(uuid.uuid4())
        expires_at = None
        
        if expires_hours:
            expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO summaries 
                        (summary_id, session_id, conversation_id, summary_type, summary,
                         token_range_start, token_range_end, importance_score, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (summary_id, session_id, conversation_id, summary_type, summary,
                       token_range[0] if token_range else None,
                       token_range[1] if token_range else None,
                       importance_score, expires_at))
        self.db_conn.commit()
        return summary_id

    def _create_conversation_summary(self, conversations: List[Tuple]) -> str:
        """Create a summary from conversation data."""
        if not conversations:
            return "No conversations to summarize."
        
        user_messages = [conv[0] for conv in conversations if conv[1] == 'user']
        assistant_messages = [conv[0] for conv in conversations if conv[1] == 'assistant']
        
        # Extract key topics (simple keyword extraction)
        all_text = ' '.join([conv[0] for conv in conversations])
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        keywords = [kw[0] for kw in top_keywords]
        
        summary = f"""
        Conversation Summary ({len(conversations)} messages):
        - User messages: {len(user_messages)}
        - Assistant messages: {len(assistant_messages)}
        - Key topics: {', '.join(keywords)}
        - Time range: {conversations[0][2]} to {conversations[-1][2]}
        
        Main discussion points:
        {self._extract_main_points(user_messages[:3])}
        """
        
        return summary.strip()

    def _create_daily_summary(self, conversations: List[Tuple]) -> str:
        """Create a daily activity summary."""
        if not conversations:
            return "No activity today."
        
        # Group by hour for activity pattern
        hourly_activity = {}
        topics = []
        
        for conv in conversations:
            timestamp = datetime.fromisoformat(conv[2].replace('Z', '+00:00'))
            hour = timestamp.hour
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            # Extract topics from metadata if available
            if len(conv) > 3 and conv[3]:
                try:
                    metadata = json.loads(conv[3])
                    if 'topics' in metadata:
                        topics.extend(metadata['topics'])
                except:
                    pass
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
        unique_topics = list(set(topics))
        
        summary = f"""
        Daily Activity Summary:
        - Total messages: {len(conversations)}
        - Peak activity hour: {peak_hour}:00
        - Active topics: {', '.join(unique_topics[:5]) if unique_topics else 'General discussion'}
        - Activity pattern: {len(hourly_activity)} active hours
        """
        
        return summary.strip()

    def _create_importance_summary(self, conversations: List[Tuple]) -> str:
        """Create a summary of high-importance conversations."""
        important_msgs = []
        
        for conv in conversations:
            if len(conv) > 3 and conv[3]:
                try:
                    metadata = json.loads(conv[3])
                    importance = metadata.get('importance', 0.5)
                    if importance > 0.7:
                        important_msgs.append((conv[0][:100], importance))
                except:
                    pass
        
        if not important_msgs:
            return "No high-importance conversations detected."
        
        summary = f"""
        High-Importance Activity Summary:
        - Important messages: {len(important_msgs)}
        - Average importance: {sum(msg[1] for msg in important_msgs) / len(important_msgs):.2f}
        
        Key important discussions:
        """
        
        for msg, importance in important_msgs[:3]:
            summary += f"\n- (Importance: {importance:.2f}) {msg}..."
        
        return summary.strip()

    def _extract_main_points(self, messages: List[str]) -> str:
        """Extract main points from messages (simplified)."""
        if not messages:
            return "No main points identified."
        
        # Simple extraction of sentences with question words or key phrases
        main_points = []
        key_phrases = ['how to', 'what is', 'why', 'when', 'where', 'help with', 'problem', 'issue', 'need']
        
        for msg in messages:
            sentences = msg.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(phrase in sentence.lower() for phrase in key_phrases) and len(sentence) > 20:
                    main_points.append(sentence)
        
        return '\n'.join([f"• {point}" for point in main_points[:3]]) if main_points else "General discussion topics"

    def trigger_auto_summarization(self, session_id: str) -> Optional[str]:
        """Manually trigger auto-summarization check."""
        should_trigger, trigger_type = self.should_trigger_summary(session_id)
        
        if should_trigger:
            return self.generate_auto_summary(session_id, trigger_type)
        
        return None
