"""
Response formatter for API endpoints
"""

import json
from flask import Response
from src.models.analysis_result import AnalysisResult


class ResponseFormatter:
    """Formats API responses with consistent structure"""
    
    @staticmethod
    def format_response(result: AnalysisResult) -> Response:
        """
        Format successful response with correct JSON order and Unicode support
        
        Args:
            result: Analysis result to format
            
        Returns:
            Flask Response object
        """
        response_data = result.to_dict()
        
        return Response(
            json.dumps(response_data, ensure_ascii=False, indent=None),
            mimetype='application/json',
            status=200
        )
    
    @staticmethod
    def format_error(message: str, status_code: int) -> Response:
        """
        Format error response
        
        Args:
            message: Error message
            status_code: HTTP status code
            
        Returns:
            Flask Response object
        """
        error_data = {
            "status": "error",
            "response_text": message,
            "confidence_score": 0.0,
            "analysis_type": "error"
        }
        
        return Response(
            json.dumps(error_data, ensure_ascii=False, indent=None),
            mimetype='application/json',
            status=status_code
        )
    
    @staticmethod
    def format_validation_error(field_errors: dict) -> Response:
        """
        Format validation error response
        
        Args:
            field_errors: Dictionary of field validation errors
            
        Returns:
            Flask Response object
        """
        error_message = "Validation failed: " + ", ".join(
            f"{field}: {error}" for field, error in field_errors.items()
        )
        
        return ResponseFormatter.format_error(error_message, 400)
