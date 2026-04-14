#!/usr/bin/env python3
"""
Hermes Lite Memory System - Permanent storage for conversations, preferences, and learned information
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

class MemorySystem:
    """Manages persistent memory for Hermes Lite agent"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to ~/.hermes-lite/data/
            self.data_dir = Path.home() / ".hermes-lite" / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self.conversations_db = self.data_dir / "conversations.db"
        self.preferences_db = self.data_dir / "preferences.db"
        self.knowledge_db = self.data_dir / "knowledge.db"
        
        self._init_databases()
    
    def _init_databases(self):
        """Initialize SQLite databases for different types of memory"""
        
        # Conversations database
        with sqlite3.connect(self.conversations_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_input TEXT,
                    agent_response TEXT,
                    model_used TEXT,
                    tokens_used INTEGER
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)
            """)
        
        # Preferences database
        with sqlite3.connect(self.preferences_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)
        
        # Knowledge database (learned facts, skills effectiveness, etc.)
        with sqlite3.connect(self.knowledge_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category_key ON knowledge(category, key)
            """)
            
            # Skills effectiveness tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_performance (
                    skill_name TEXT PRIMARY KEY,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    avg_rating REAL DEFAULT 0.0
                )
            """)
    
    def save_conversation(self, user_input: str, agent_response: str, 
                         model_used: str = "", tokens_used: int = 0):
        """Save a conversation exchange to permanent memory"""
        with sqlite3.connect(self.conversations_db) as conn:
            conn.execute("""
                INSERT INTO conversations (timestamp, user_input, agent_response, model_used, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                user_input,
                agent_response,
                model_used,
                tokens_used
            ))
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation exchanges"""
        with sqlite3.connect(self.conversations_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search conversations for specific content"""
        with sqlite3.connect(self.conversations_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversations 
                WHERE user_input LIKE ? OR agent_response LIKE ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def save_preference(self, key: str, value: str):
        """Save a user preference"""
        with sqlite3.connect(self.preferences_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO preferences (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now().isoformat()))
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get a user preference"""
        with sqlite3.connect(self.preferences_db) as conn:
            cursor = conn.execute("""
                SELECT value FROM preferences WHERE key = ?
            """, (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def save_knowledge(self, category: str, key: str, value: str, 
                      confidence: float = 1.0, source: str = ""):
        """Save a piece of learned knowledge"""
        with sqlite3.connect(self.knowledge_db) as conn:
            # Check if already exists
            existing = conn.execute("""
                SELECT id, confidence FROM knowledge 
                WHERE category = ? AND key = ?
            """, (category, key)).fetchone()
            
            if existing:
                # Update existing knowledge (weighted average of confidence)
                old_id, old_confidence = existing
                new_confidence = (old_confidence + confidence) / 2
                conn.execute("""
                    UPDATE knowledge 
                    SET value = ?, confidence = ?, source = ?, updated_at = ?
                    WHERE id = ?
                """, (value, new_confidence, source, datetime.now().isoformat(), old_id))
            else:
                # Insert new knowledge
                conn.execute("""
                    INSERT INTO knowledge (category, key, value, confidence, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (category, key, value, confidence, source, 
                     datetime.now().isoformat(), datetime.now().isoformat()))
    
    def get_knowledge(self, category: str, key: str = None) -> List[Dict]:
        """Get knowledge items"""
        with sqlite3.connect(self.knowledge_db) as conn:
            conn.row_factory = sqlite3.Row
            if key:
                cursor = conn.execute("""
                    SELECT * FROM knowledge 
                    WHERE category = ? AND key = ?
                    ORDER BY confidence DESC, updated_at DESC
                """, (category, key))
            else:
                cursor = conn.execute("""
                    SELECT * FROM knowledge 
                    WHERE category = ?
                    ORDER BY confidence DESC, updated_at DESC
                """, (category,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_skill_performance(self, skill_name: str, success: bool, rating: float = None):
        """Update performance metrics for a skill"""
        with sqlite3.connect(self.knowledge_db) as conn:
            # Get current stats
            current = conn.execute("""
                SELECT success_count, failure_count, avg_rating 
                FROM skill_performance WHERE skill_name = ?
            """, (skill_name,)).fetchone()
            
            if current:
                success_count, failure_count, avg_rating = current
                new_success = success_count + (1 if success else 0)
                new_failure = failure_count + (0 if success else 1)
                
                # Update average rating if provided
                if rating is not None:
                    total_ratings = new_success + new_failure
                    if total_ratings > 0:
                        new_avg = ((avg_rating * (success_count + failure_count)) + rating) / total_ratings
                    else:
                        new_avg = 0.0
                else:
                    new_avg = avg_rating
                
                conn.execute("""
                    UPDATE skill_performance 
                    SET success_count = ?, failure_count = ?, avg_rating = ?, last_used = ?
                    WHERE skill_name = ?
                """, (new_success, new_failure, new_avg, datetime.now().isoformat(), skill_name))
            else:
                # Insert new skill record
                success_count = 1 if success else 0
                failure_count = 0 if success else 1
                avg_rating = rating if rating is not None else 0.0
                conn.execute("""
                    INSERT INTO skill_performance (skill_name, success_count, failure_count, avg_rating, last_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (skill_name, success_count, failure_count, avg_rating, datetime.now().isoformat()))
    
    def get_skill_performance(self, skill_name: str = None) -> List[Dict]:
        """Get skill performance metrics"""
        with sqlite3.connect(self.knowledge_db) as conn:
            conn.row_factory = sqlite3.Row
            if skill_name:
                cursor = conn.execute("""
                    SELECT * FROM skill_performance WHERE skill_name = ?
                """, (skill_name,))
                result = cursor.fetchone()
                return [dict(result)] if result else []
            else:
                cursor = conn.execute("""
                    SELECT * FROM skill_performance ORDER BY (success_count + failure_count) DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Remove old data to prevent unbounded growth"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        with sqlite3.connect(self.conversations_db) as conn:
            conn.execute("DELETE FROM conversations WHERE timestamp < ?", (cutoff_date,))
        
        # Keep preferences and knowledge indefinitely (they're valuable)
        # But we could add cleanup for low-confidence knowledge if needed

# Global memory instance
memory_system = MemorySystem()