"""
Base classes and utilities for deep content extraction
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime


@dataclass
class ExtractionResult:
    """Container for extracted intelligence data"""
    
    category: str  # Type of extraction (credentials, pii, crypto, etc.)
    confidence: float  # Confidence score (0.0 to 1.0)
    risk_level: str  # low, medium, high, critical
    data: Dict[str, Any]  # The actual extracted data
    context: Optional[str] = None  # Surrounding context
    location: Optional[str] = None  # Location in page (URL, line number, etc.)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'category': self.category,
            'confidence': self.confidence,
            'risk_level': self.risk_level,
            'data': self.data,
            'context': self.context,
            'location': self.location,
            'timestamp': self.timestamp.isoformat()
        }


class BaseExtractor(ABC):
    """Base class for all content extractors"""
    
    def __init__(self):
        self.results: List[ExtractionResult] = []
    
    @abstractmethod
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """
        Extract intelligence from text content
        
        Args:
            text: The text content to analyze
            url: The source URL (optional)
            
        Returns:
            List of ExtractionResult objects
        """
        pass
    
    def get_context(self, text: str, match_start: int, match_end: int, 
                   context_chars: int = 100) -> str:
        """
        Extract surrounding context for a match
        
        Args:
            text: Full text content
            match_start: Start position of match
            match_end: End position of match
            context_chars: Number of characters to include on each side
            
        Returns:
            Context string
        """
        start = max(0, match_start - context_chars)
        end = min(len(text), match_end + context_chars)
        context = text[start:end]
        
        # Clean up context
        context = context.replace('\n', ' ').replace('\r', ' ')
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context
    
    def calculate_risk_level(self, data_type: str, confidence: float) -> str:
        """
        Calculate risk level based on data type and confidence
        
        Args:
            data_type: Type of sensitive data found
            confidence: Confidence score
            
        Returns:
            Risk level string
        """
        critical_types = ['password', 'ssn', 'credit_card', 'api_key', 'private_key']
        high_types = ['email', 'phone', 'bitcoin', 'credential_dump']
        medium_types = ['onion_link', 'ip_address', 'hash']
        
        if data_type in critical_types and confidence > 0.7:
            return 'critical'
        elif data_type in high_types and confidence > 0.6:
            return 'high'
        elif data_type in medium_types and confidence > 0.5:
            return 'medium'
        else:
            return 'low'


class RegexPatterns:
    """Common regex patterns for extraction"""
    
    # Email patterns
    EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Cryptocurrency addresses
    BITCOIN = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
    ETHEREUM = r'\b0x[a-fA-F0-9]{40}\b'
    MONERO = r'\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b'
    LITECOIN = r'\b[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}\b'
    
    # Onion links
    ONION_V2 = r'\b[a-z2-7]{16}\.onion\b'
    ONION_V3 = r'\b[a-z2-7]{56}\.onion\b'
    
    # Network indicators
    IPV4 = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    IPV6 = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    DOMAIN = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    
    # PII
    PHONE = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    SSN = r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'
    CREDIT_CARD = r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b'
    
    # Credentials
    USERNAME_PASSWORD = r'(?i)(?:username|user|login|email)[\s:=]+([^\s:]+)[\s\n\r]*(?:password|pass|pwd)[\s:=]+([^\s\n\r]+)'
    API_KEY_AWS = r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'
    API_KEY_GENERIC = r'\b[a-zA-Z0-9_-]{32,}\b'
    JWT_TOKEN = r'\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b'
    
    # Hashes
    MD5 = r'\b[a-fA-F0-9]{32}\b'
    SHA1 = r'\b[a-fA-F0-9]{40}\b'
    SHA256 = r'\b[a-fA-F0-9]{64}\b'
    
    # Communication
    PGP_KEY = r'-----BEGIN PGP (?:PUBLIC|PRIVATE) KEY BLOCK-----'
    PGP_FINGERPRINT = r'\b[0-9A-F]{40}\b'
    JABBER = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\s|$)'
    TELEGRAM = r'(?:@|t\.me/)[a-zA-Z0-9_]{5,32}'
    WICKR = r'(?i)wickr(?:\s*:?\s*|me\s*:?\s*)([a-zA-Z0-9_-]{5,20})'
    
    # CVE
    CVE = r'\bCVE-\d{4}-\d{4,7}\b'


class LuhnValidator:
    """Luhn algorithm for credit card validation"""
    
    @staticmethod
    def validate(number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm
        
        Args:
            number: Credit card number string
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Remove any spaces or dashes
            number = number.replace(' ', '').replace('-', '')
            
            if not number.isdigit():
                return False
            
            # Luhn algorithm
            total = 0
            reverse_digits = number[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n
            
            return total % 10 == 0
        except (ValueError, AttributeError):
            return False

