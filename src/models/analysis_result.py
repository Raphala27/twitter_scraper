"""
Analysis result models
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class AnalysisResult:
    """Represents the final analysis result"""
    status: str
    response_text: str
    confidence_score: float
    analysis_type: str
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary in exact order for API response"""
        return {
            "status": self.status,
            "response_text": self.response_text,
            "confidence_score": self.confidence_score,
            "analysis_type": self.analysis_type
        }
    
    def is_success(self) -> bool:
        """Check if analysis was successful"""
        return self.status == "success"
    
    def is_error(self) -> bool:
        """Check if analysis had an error"""
        return self.status == "error"

    @classmethod
    def success(cls, response_text: str, confidence_score: float, analysis_type: str = "crypto_sentiment") -> 'AnalysisResult':
        """Create a successful analysis result"""
        return cls(
            status="success",
            response_text=response_text,
            confidence_score=confidence_score,
            analysis_type=analysis_type
        )
    
    @classmethod
    def error(cls, error_message: str) -> 'AnalysisResult':
        """Create an error analysis result"""
        return cls(
            status="error",
            response_text=error_message,
            confidence_score=0.0,
            analysis_type="error"
        )
