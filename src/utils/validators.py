"""
Request validators for API endpoints
"""

from typing import Dict, Any, List
from datetime import datetime


class RequestValidator:
    """Validates incoming API requests"""
    
    REQUIRED_BOT_FIELDS = [
        'tweet_id', 'author_handle', 'tweet_content', 'timestamp'
    ]
    
    OPTIONAL_BOT_FIELDS = [
        'author_id', 'is_reply', 'parent_tweet_id', 'mentioned_bot', 'user_response'
    ]

    def validate_bot_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate bot analysis request data
        
        Args:
            data: Request data dictionary
            
        Returns:
            Validated and cleaned data
            
        Raises:
            ValueError: If validation fails
        """
        if not data:
            raise ValueError("Request body is required")
        
        # Check required fields
        missing_fields = []
        for field in self.REQUIRED_BOT_FIELDS:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate specific fields
        self._validate_timestamp(data['timestamp'])
        self._validate_content_length(data['tweet_content'])
        self._validate_author_handle(data['author_handle'])
        
        # Clean and return data
        return self._clean_request_data(data)
    
    def _validate_timestamp(self, timestamp: str) -> None:
        """Validate timestamp format"""
        try:
            # Try to parse ISO format
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise ValueError("Invalid timestamp format. Use ISO format (e.g., '2025-09-27T12:00:00Z')")
    
    def _validate_content_length(self, content: str) -> None:
        """Validate content length"""
        if len(content) > 500:  # Twitter max is 280, but allow some buffer
            raise ValueError("Tweet content too long (max 500 characters)")
        
        if len(content.strip()) == 0:
            raise ValueError("Tweet content cannot be empty")
    
    def _validate_author_handle(self, handle: str) -> None:
        """Validate Twitter handle format"""
        if not handle.startswith('@'):
            raise ValueError("Author handle must start with '@'")
        
        if len(handle) < 2:
            raise ValueError("Author handle too short")
    
    def _clean_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize request data"""
        cleaned = {}
        
        # Process required fields
        for field in self.REQUIRED_BOT_FIELDS:
            cleaned[field] = str(data[field]).strip()
        
        # Process optional fields
        for field in self.OPTIONAL_BOT_FIELDS:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    cleaned[field] = value.strip()
                else:
                    cleaned[field] = value
            else:
                # Set defaults for optional fields
                if field == 'is_reply':
                    cleaned[field] = False
                elif field == 'parent_tweet_id':
                    cleaned[field] = None
                else:
                    cleaned[field] = ""
        
        return cleaned
