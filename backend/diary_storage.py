"""
Diary Storage Module for CogniDiary
Handles saving and retrieving diary entries as text files
"""

import os
import json
import logging
from datetime import datetime
import glob
import re

logger = logging.getLogger(__name__)

class DiaryStorage:
    def __init__(self, storage_directory="diary_entries"):
        """
        Initialize diary storage system
        
        Args:
            storage_directory: Directory to store diary entries
        """
        self.storage_directory = storage_directory
        self.ensure_storage_directory()
        logger.info(f"Diary storage initialized: {self.storage_directory}")
    
    def ensure_storage_directory(self):
        """Create storage directory if it doesn't exist"""
        try:
            os.makedirs(self.storage_directory, exist_ok=True)
            logger.info(f"Storage directory ready: {self.storage_directory}")
        except Exception as e:
            logger.error(f"Failed to create storage directory: {e}")
            raise
    
    def save_entry(self, title, text, mood="Not detected", timestamp=None):
        """
        Save a diary entry to a text file
        
        Args:
            title: Entry title
            text: Entry content
            mood: Detected mood
            timestamp: Entry timestamp (ISO format)
            
        Returns:
            dict: Save result with success status and filename
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            # Parse timestamp for filename
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Create filename with date and time
            filename = f"entry_{dt.strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(self.storage_directory, filename)
            
            # Prepare entry content
            entry_content = self._format_entry(title, text, mood, timestamp)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(entry_content)
            
            logger.info(f"Diary entry saved: {filename}")
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'size': len(entry_content)
            }
            
        except Exception as e:
            logger.error(f"Error saving diary entry: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_entry(self, title, text, mood, timestamp):
        """Format diary entry content for text file"""
        # Parse timestamp for readable format
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            formatted_date = timestamp
        
        # Create formatted entry
        separator = "=" * 60
        entry_lines = [
            separator,
            f"COGNIDIARY ENTRY",
            separator,
            f"Title: {title}",
            f"Date: {formatted_date}",
            f"Mood: {mood}",
            separator,
            "",
            text,
            "",
            separator,
            f"Entry saved automatically by CogniDiary",
            ""
        ]
        
        return "\n".join(entry_lines)
    
    def get_all_entries(self):
        """
        Get list of all diary entries with metadata
        
        Returns:
            list: List of entry metadata dictionaries
        """
        try:
            entries = []
            
            # Find all text files in storage directory
            pattern = os.path.join(self.storage_directory, "entry_*.txt")
            entry_files = glob.glob(pattern)
            
            for filepath in sorted(entry_files, reverse=True):  # Most recent first
                try:
                    entry_metadata = self._extract_entry_metadata(filepath)
                    if entry_metadata:
                        entries.append(entry_metadata)
                except Exception as e:
                    logger.warning(f"Could not process entry file {filepath}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(entries)} diary entries")
            return entries
            
        except Exception as e:
            logger.error(f"Error retrieving entries: {str(e)}")
            return []
    
    def _extract_entry_metadata(self, filepath):
        """Extract metadata from a diary entry file"""
        try:
            filename = os.path.basename(filepath)
            file_stats = os.stat(filepath)
            
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title, date, and mood from content
            lines = content.split('\n')
            title = "Untitled Entry"
            date = ""
            mood = "Not detected"
            entry_text = ""
            
            for i, line in enumerate(lines):
                if line.startswith("Title: "):
                    title = line.replace("Title: ", "").strip()
                elif line.startswith("Date: "):
                    date = line.replace("Date: ", "").strip()
                elif line.startswith("Mood: "):
                    mood = line.replace("Mood: ", "").strip()
                elif line.strip() == "=" * 60 and i > 5:  # Find content start
                    # Extract actual entry text (skip header and footers)
                    content_start = i + 2
                    content_end = -3  # Remove footer lines
                    entry_text = "\n".join(lines[content_start:content_end]).strip()
                    break
            
            # Extract word count
            word_count = len(entry_text.split()) if entry_text else 0
            
            return {
                'filename': filename,
                'filepath': filepath,
                'title': title,
                'date': date,
                'mood': mood,
                'word_count': word_count,
                'file_size': file_stats.st_size,
                'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'preview': entry_text[:200] + "..." if len(entry_text) > 200 else entry_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {filepath}: {e}")
            return None
    
    def get_entry_by_filename(self, filename):
        """
        Get full content of a specific diary entry
        
        Args:
            filename: Name of the entry file
            
        Returns:
            dict: Entry content and metadata
        """
        try:
            filepath = os.path.join(self.storage_directory, filename)
            
            if not os.path.exists(filepath):
                return {
                    'success': False,
                    'error': 'Entry file not found'
                }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = self._extract_entry_metadata(filepath)
            
            return {
                'success': True,
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error reading entry {filename}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_entries(self, query):
        """
        Search diary entries by text content
        
        Args:
            query: Search query string
            
        Returns:
            list: Matching entries
        """
        try:
            matching_entries = []
            all_entries = self.get_all_entries()
            
            query_lower = query.lower().strip()
            
            for entry in all_entries:
                # Search in title and preview content
                if (query_lower in entry['title'].lower() or 
                    query_lower in entry['preview'].lower() or
                    query_lower in entry['mood'].lower()):
                    
                    # Get full content for better search
                    full_entry = self.get_entry_by_filename(entry['filename'])
                    if full_entry['success']:
                        entry['match_score'] = self._calculate_match_score(
                            full_entry['content'], query_lower
                        )
                        matching_entries.append(entry)
            
            # Sort by match score (descending)
            matching_entries.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            logger.info(f"Found {len(matching_entries)} entries matching '{query}'")
            return matching_entries
            
        except Exception as e:
            logger.error(f"Error searching entries: {str(e)}")
            return []
    
    def _calculate_match_score(self, content, query):
        """Calculate relevance score for search results"""
        content_lower = content.lower()
        query_words = query.split()
        
        score = 0
        for word in query_words:
            score += content_lower.count(word)
        
        return score
    
    def get_entries_by_mood(self, mood):
        """
        Get all entries with a specific mood
        
        Args:
            mood: Mood to filter by
            
        Returns:
            list: Entries with matching mood
        """
        try:
            all_entries = self.get_all_entries()
            mood_entries = [entry for entry in all_entries 
                          if entry['mood'].lower() == mood.lower()]
            
            logger.info(f"Found {len(mood_entries)} entries with mood '{mood}'")
            return mood_entries
            
        except Exception as e:
            logger.error(f"Error filtering by mood: {str(e)}")
            return []
    
    def get_entries_by_date_range(self, start_date, end_date):
        """
        Get entries within a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            list: Entries within date range
        """
        try:
            all_entries = self.get_all_entries()
            filtered_entries = []
            
            for entry in all_entries:
                try:
                    # Extract date from filename
                    filename = entry['filename']
                    date_match = re.search(r'entry_(\d{8})_', filename)
                    if date_match:
                        entry_date = date_match.group(1)  # YYYYMMDD format
                        entry_date_formatted = f"{entry_date[:4]}-{entry_date[4:6]}-{entry_date[6:8]}"
                        
                        if start_date <= entry_date_formatted <= end_date:
                            filtered_entries.append(entry)
                            
                except Exception as e:
                    logger.warning(f"Could not process date for entry {entry['filename']}: {e}")
                    continue
            
            logger.info(f"Found {len(filtered_entries)} entries between {start_date} and {end_date}")
            return filtered_entries
            
        except Exception as e:
            logger.error(f"Error filtering by date range: {str(e)}")
            return []
    
    def delete_entry(self, filename):
        """
        Delete a diary entry
        
        Args:
            filename: Name of the entry file to delete
            
        Returns:
            dict: Delete result
        """
        try:
            filepath = os.path.join(self.storage_directory, filename)
            
            if not os.path.exists(filepath):
                return {
                    'success': False,
                    'error': 'Entry file not found'
                }
            
            os.remove(filepath)
            logger.info(f"Diary entry deleted: {filename}")
            
            return {
                'success': True,
                'message': f'Entry {filename} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting entry {filename}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_storage_stats(self):
        """Get statistics about diary storage"""
        try:
            entries = self.get_all_entries()
            
            total_entries = len(entries)
            total_words = sum(entry['word_count'] for entry in entries)
            total_size = sum(entry['file_size'] for entry in entries)
            
            # Mood distribution
            mood_counts = {}
            for entry in entries:
                mood = entry['mood']
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            return {
                'success': True,
                'total_entries': total_entries,
                'total_words': total_words,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'mood_distribution': mood_counts,
                'storage_directory': self.storage_directory
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_available(self):
        """Check if diary storage is available"""
        try:
            return os.path.exists(self.storage_directory) and os.access(self.storage_directory, os.W_OK)
        except:
            return False