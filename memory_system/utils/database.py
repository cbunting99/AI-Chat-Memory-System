"""
File: database.py
Description: Database utilities and setup for the memory system including table creation, indexing, and connection management

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

import sqlite3
import logging
from typing import Any


class DatabaseManager:
    """Handles database initialization and common operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.logger = logging.getLogger(__name__)
        
    def create_tables(self):
        """Create all necessary database tables."""
        cursor = self.conn.cursor()
        
        # Enhanced sessions table with metadata
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            session_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_messages INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            metadata TEXT,
            is_archived BOOLEAN DEFAULT FALSE
        )''')

        # Enhanced conversations table with embeddings
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            session_id TEXT,
            content TEXT NOT NULL,
            content_hash TEXT,
            message_type TEXT NOT NULL,
            role TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            parent_id TEXT,
            thread_id TEXT,
            tokens INTEGER,
            importance_score REAL DEFAULT 0.5,
            embedding BLOB,
            compressed_content BLOB,
            compression_level INTEGER DEFAULT 0,
            metadata TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )''')

        # File contexts table
        cursor.execute('''CREATE TABLE IF NOT EXISTS file_contexts (
            file_id TEXT PRIMARY KEY,
            session_id TEXT,
            file_name TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT,
            file_path TEXT,
            mime_type TEXT,
            file_size INTEGER,
            encoding TEXT DEFAULT 'utf-8',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_modified DATETIME,
            embedding BLOB,
            metadata TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )''')

        # Enhanced summaries table
        cursor.execute('''CREATE TABLE IF NOT EXISTS summaries (
            summary_id TEXT PRIMARY KEY,
            session_id TEXT,
            conversation_id TEXT,
            summary_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            token_range_start INTEGER,
            token_range_end INTEGER,
            importance_score REAL DEFAULT 0.5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            embedding BLOB,
            metadata TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )''')

        # Media contents table for multi-modal support
        cursor.execute('''CREATE TABLE IF NOT EXISTS media_contents (
            content_id TEXT PRIMARY KEY,
            session_id TEXT,
            media_type TEXT NOT NULL,
            content BLOB,
            content_text TEXT,
            file_path TEXT,
            encoding TEXT,
            file_size INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            embedding BLOB,
            metadata TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )''')

        # Knowledge nodes table
        cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_nodes (
            node_id TEXT PRIMARY KEY,
            session_id TEXT,
            content TEXT NOT NULL,
            node_type TEXT NOT NULL,
            importance_score REAL DEFAULT 0.5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            embedding BLOB,
            metadata TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )''')

        # Knowledge relations table
        cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_relations (
            relation_id TEXT PRIMARY KEY,
            source_node_id TEXT NOT NULL,
            target_node_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            strength REAL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes (node_id),
            FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (node_id)
        )''')

        # Consolidation jobs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS consolidation_jobs (
            job_id TEXT PRIMARY KEY,
            session_id TEXT,
            job_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            progress REAL DEFAULT 0.0,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            result_summary TEXT,
            metadata TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )''')

        self.conn.commit()
        self.logger.info("Database tables created successfully")

    def create_indexes(self):
        """Create database indexes for performance."""
        cursor = self.conn.cursor()
        
        # Core indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session_timestamp ON conversations(session_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_hash ON conversations(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_type ON conversations(message_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_importance ON conversations(importance_score)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_session ON file_contexts(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_hash ON file_contexts(content_hash)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_session ON summaries(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_type ON summaries(summary_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_expires ON summaries(expires_at)')
        
        # New feature indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_media_session_type ON media_contents(session_id, media_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_session ON knowledge_nodes(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_type ON knowledge_nodes(node_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_relations_source ON knowledge_relations(source_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_relations_target ON knowledge_relations(target_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consolidation_session ON consolidation_jobs(session_id)')
        
        self.conn.commit()
        self.logger.info("Database indexes created successfully")

    def close(self):
        """Close database connection."""
        self.conn.close()
        self.logger.info("Database connection closed")
