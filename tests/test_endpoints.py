"""
Tests for API endpoints
"""

import json
from unittest.mock import Mock, patch

from src.api.endpoints import BotAnalysisEndpoint
from src.core.crypto_analyzer import CryptoAnalyzer
from src.models.analysis_result import AnalysisResult


class TestBotAnalysisEndpoint:
    """Test suite for bot analysis endpoint"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_analyzer = Mock(spec=CryptoAnalyzer)
        self.endpoint = BotAnalysisEndpoint(self.mock_analyzer)
    
    def test_analyze_success(self):
        """Test successful analysis request"""
        # Setup mock
        mock_result = AnalysisResult.success(
            response_text="Great analysis!",
            confidence_score=85.0
        )
        self.mock_analyzer.analyze_tweet.return_value = mock_result
        
        # Create mock request
        with patch('src.api.endpoints.request') as mock_request:
            mock_request.get_json.return_value = {
                'tweet_id': '123',
                'author_handle': '@testuser',
                'tweet_content': 'Bitcoin to the moon!',
                'timestamp': '2025-09-27T12:00:00Z'
            }
            
            # Execute
            response = self.endpoint.analyze()
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['status'] == 'success'
            assert response_data['response_text'] == 'Great analysis!'
            assert response_data['confidence_score'] == 85.0
    
    def test_analyze_validation_error(self):
        """Test request validation error"""
        # Create mock request with missing required field
        with patch('src.api.endpoints.request') as mock_request:
            mock_request.get_json.return_value = {
                'tweet_id': '123',
                # Missing required fields
            }
            
            # Execute
            response = self.endpoint.analyze()
            
            # Assert
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert response_data['status'] == 'error'
    
    def test_analyze_internal_error(self):
        """Test internal server error handling"""
        # Setup mock to raise exception
        self.mock_analyzer.analyze_tweet.side_effect = Exception("Internal error")
        
        # Create mock request
        with patch('src.api.endpoints.request') as mock_request:
            mock_request.get_json.return_value = {
                'tweet_id': '123',
                'author_handle': '@testuser',
                'tweet_content': 'Bitcoin test',
                'timestamp': '2025-09-27T12:00:00Z'
            }
            
            # Execute
            response = self.endpoint.analyze()
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data)
            assert response_data['status'] == 'error'
