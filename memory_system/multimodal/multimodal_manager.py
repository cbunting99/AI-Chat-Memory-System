"""
File: multimodal_manager.py
Description: Multi-modal content processing support for images, audio, video, and documents with metadata extraction

Copyright (c) 2025 Chris Bunting
Licensed under the MIT License.
"""

"""Multi-modal content processing support."""

import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Union

from ..core.types import MediaType

# Multi-modal support imports
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class MultiModalManager:
    """Manages multi-modal content processing."""
    
    def __init__(self, db_conn, embedding_manager=None):
        self.db_conn = db_conn
        self.embedding_manager = embedding_manager
        self.logger = logging.getLogger(__name__)
    
    def add_media_content(self, session_id: str, content: Union[str, bytes], 
                         media_type: MediaType, file_path: str = None,
                         encoding: str = None, metadata: Dict[str, Any] = None) -> str:
        """Add media content to the system."""
        content_id = str(uuid.uuid4())
        
        # Process the content based on type
        processed_metadata = self._process_media_content(content, media_type, file_path)
        if metadata:
            processed_metadata.update(metadata)
        
        # Generate text representation for embeddings
        content_text = self._extract_text_representation(content, media_type, processed_metadata)
        embedding = None
        if self.embedding_manager and content_text:
            embedding = self.embedding_manager.generate_embedding(content_text)
        
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO media_contents
                        (content_id, session_id, media_type, content, content_text,
                         file_path, encoding, file_size, embedding, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (content_id, session_id, media_type.value,
                       content if isinstance(content, bytes) else content.encode('utf-8'),
                       content_text, file_path, encoding,
                       len(content) if content else 0,
                       embedding, json.dumps(processed_metadata)))
        self.db_conn.commit()
        
        self.logger.info(f"Added media content {content_id} of type {media_type.value}")
        return content_id
    
    def _process_media_content(self, content: Union[str, bytes], media_type: MediaType, 
                              file_path: str = None) -> Dict[str, Any]:
        """Process media content and extract metadata."""
        metadata = {"processed_at": "now", "media_type": media_type.value}
        
        try:
            if media_type == MediaType.IMAGE:
                return self._process_image_content(content, file_path)
            elif media_type == MediaType.AUDIO:
                return self._process_audio_content(content, file_path)
            elif media_type == MediaType.VIDEO:
                return self._process_video_content(content, file_path)
            elif media_type == MediaType.DOCUMENT:
                return self._process_document_content(content, file_path)
            elif media_type == MediaType.CODE:
                return self._process_code_content(content)
            else:  # TEXT
                return {"text_length": len(str(content)), "type": "text"}
        except Exception as e:
            self.logger.error(f"Error processing {media_type.value} content: {e}")
            return metadata
    
    def _process_image_content(self, content: Union[str, bytes], file_path: str = None) -> Dict[str, Any]:
        """Process image content and extract metadata."""
        metadata = {"type": "image"}
        
        if not PILLOW_AVAILABLE:
            metadata["error"] = "PIL not available for image processing"
            return metadata
        
        try:
            if file_path:
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode,
                        "size_bytes": len(content) if isinstance(content, bytes) else 0
                    })
            else:
                # Handle in-memory image data
                metadata["size_bytes"] = len(content) if isinstance(content, bytes) else 0
                
        except Exception as e:
            metadata["error"] = f"Image processing error: {e}"
        
        return metadata
    
    def _process_audio_content(self, content: Union[str, bytes], file_path: str = None) -> Dict[str, Any]:
        """Process audio content and extract features."""
        metadata = {"type": "audio"}
        
        if not AUDIO_AVAILABLE:
            metadata["error"] = "librosa not available for audio processing"
            return metadata
        
        try:
            if file_path:
                y, sr = librosa.load(file_path)
                metadata.update({
                    "duration": len(y) / sr,
                    "sample_rate": sr,
                    "samples": len(y),
                    "size_bytes": len(content) if isinstance(content, bytes) else 0
                })
                
                # Extract basic audio features
                metadata["tempo"] = float(librosa.beat.tempo(y=y, sr=sr)[0])
                metadata["zero_crossing_rate"] = float(librosa.feature.zero_crossing_rate(y).mean())
            else:
                metadata["size_bytes"] = len(content) if isinstance(content, bytes) else 0
                
        except Exception as e:
            metadata["error"] = f"Audio processing error: {e}"
        
        return metadata
    
    def _process_video_content(self, content: Union[str, bytes], file_path: str = None) -> Dict[str, Any]:
        """Process video content (basic metadata extraction)."""
        return {
            "type": "video",
            "size_bytes": len(content) if isinstance(content, bytes) else 0,
            "file_path": file_path,
            "note": "Advanced video processing requires additional dependencies"
        }
    
    def _process_document_content(self, content: Union[str, bytes], file_path: str = None) -> Dict[str, Any]:
        """Process document content."""
        text_content = content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
        
        return {
            "type": "document",
            "text_length": len(text_content),
            "word_count": len(text_content.split()),
            "line_count": text_content.count('\n') + 1,
            "size_bytes": len(content) if isinstance(content, bytes) else len(text_content.encode('utf-8'))
        }
    
    def _process_code_content(self, content: Union[str, bytes]) -> Dict[str, Any]:
        """Process code content."""
        text_content = content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
        
        # Simple code analysis
        lines = text_content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        return {
            "type": "code",
            "total_lines": len(lines),
            "code_lines": len(code_lines),
            "comment_lines": len(comment_lines),
            "size_bytes": len(text_content.encode('utf-8'))        }
    
    def _extract_text_representation(self, content: Union[str, bytes], media_type: MediaType, 
                                   metadata: Dict[str, Any]) -> str:
        """Extract text representation for embedding generation."""
        if media_type == MediaType.TEXT:
            return content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
        elif media_type == MediaType.CODE:
            return content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
        elif media_type == MediaType.DOCUMENT:
            return content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
        elif media_type == MediaType.IMAGE:
            # Create description from metadata
            if 'width' in metadata and 'height' in metadata:
                return f"Image {metadata['width']}x{metadata['height']} {metadata.get('format', 'unknown format')}"
            return "Image content"
        elif media_type == MediaType.AUDIO:
            # Create description from metadata
            if 'duration' in metadata:
                duration = metadata['duration']
                if isinstance(duration, (int, float)):
                    return f"Audio content {duration:.2f} seconds"
                else:
                    return f"Audio content {duration}"
            return "Audio content"
        elif media_type == MediaType.VIDEO:
            return "Video content"
        else:
            return str(content)[:500]  # Fallback
    
    def search_media_content(self, session_id: str, media_types: List[MediaType] = None,
                           query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search media content."""
        cursor = self.db_conn.cursor()
        
        conditions = ["session_id = ?", "is_deleted = FALSE"]
        params = [session_id]
        
        if media_types:
            type_conditions = ' OR '.join(['media_type = ?' for _ in media_types])
            conditions.append(f"({type_conditions})")
            params.extend([mt.value for mt in media_types])
        
        if query:
            conditions.append("(content_text LIKE ? OR metadata LIKE ?)")
            params.extend([f'%{query}%', f'%{query}%'])
        
        sql = f'''SELECT content_id, media_type, content_text, file_path, 
                        created_at, metadata
                 FROM media_contents 
                 WHERE {' AND '.join(conditions)}
                 ORDER BY created_at DESC
                 LIMIT ?'''
        params.append(limit)
        
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'content_id': row[0],
                'media_type': row[1],
                'content_text': row[2],
                'file_path': row[3],
                'created_at': row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            })
        
        return results
