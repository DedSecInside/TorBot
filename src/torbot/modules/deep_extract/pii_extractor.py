"""
Personal Identifiable Information (PII) Extractor
"""

import re
import phonenumbers
from typing import List
from .base import BaseExtractor, ExtractionResult, RegexPatterns, LuhnValidator


class PIIExtractor(BaseExtractor):
    """Extract Personal Identifiable Information from content"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract various types of PII"""
        results = []
        
        # Extract email addresses
        results.extend(self._extract_emails(text, url))
        
        # Extract phone numbers
        results.extend(self._extract_phone_numbers(text, url))
        
        # Extract SSNs
        results.extend(self._extract_ssns(text, url))
        
        # Extract credit card numbers
        results.extend(self._extract_credit_cards(text, url))
        
        # Extract names (basic pattern matching)
        results.extend(self._extract_names(text, url))
        
        # Extract addresses
        results.extend(self._extract_addresses(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_emails(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract email addresses with context"""
        results = []
        
        for match in re.finditer(RegexPatterns.EMAIL, text):
            email = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Determine risk level based on context
            risk_level = 'medium'
            sensitive_keywords = ['admin', 'root', 'support', 'contact', 'info']
            if any(keyword in email.lower() for keyword in sensitive_keywords):
                risk_level = 'high'
            
            results.append(ExtractionResult(
                category='pii',
                confidence=0.9,
                risk_level=risk_level,
                data={
                    'type': 'email',
                    'email': email,
                    'domain': email.split('@')[1] if '@' in email else None
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_phone_numbers(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract phone numbers using phonenumbers library"""
        results = []
        
        # Try to parse phone numbers from text
        try:
            for match in phonenumbers.PhoneNumberMatcher(text, None):
                phone = match.number
                phone_str = phonenumbers.format_number(
                    phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
                
                context = self.get_context(text, match.start, match.end)
                
                results.append(ExtractionResult(
                    category='pii',
                    confidence=0.85,
                    risk_level='high',
                    data={
                        'type': 'phone_number',
                        'number': phone_str,
                        'country_code': phone.country_code,
                        'national_number': phone.national_number,
                        'is_valid': phonenumbers.is_valid_number(phone)
                    },
                    context=context,
                    location=url
                ))
        except Exception as _:
            # Fallback to regex if phonenumbers fails
            for match in re.finditer(RegexPatterns.PHONE, text):
                phone_str = match.group(0)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='pii',
                    confidence=0.7,
                    risk_level='high',
                    data={
                        'type': 'phone_number',
                        'number': phone_str,
                        'is_valid': None
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_ssns(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract Social Security Numbers"""
        results = []
        
        for match in re.finditer(RegexPatterns.SSN, text):
            ssn = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Check if context suggests this is actually an SSN
            ssn_keywords = ['ssn', 'social security', 'ss#', 'social']
            context_lower = context.lower()
            confidence = 0.6
            
            if any(keyword in context_lower for keyword in ssn_keywords):
                confidence = 0.9
            
            results.append(ExtractionResult(
                category='pii',
                confidence=confidence,
                risk_level='critical',
                data={
                    'type': 'ssn',
                    'ssn': ssn,
                    'masked': ssn[:3] + '-XX-' + ssn[-4:]
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_credit_cards(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract and validate credit card numbers"""
        results = []
        
        for match in re.finditer(RegexPatterns.CREDIT_CARD, text):
            card_number = match.group(0)
            
            # Validate using Luhn algorithm
            if not LuhnValidator.validate(card_number):
                continue
            
            context = self.get_context(text, match.start(), match.end())
            
            # Determine card type
            card_type = self._identify_card_type(card_number)
            
            results.append(ExtractionResult(
                category='pii',
                confidence=0.95,
                risk_level='critical',
                data={
                    'type': 'credit_card',
                    'card_type': card_type,
                    'card_number': card_number,
                    'masked': card_number[:4] + 'XXXXXXXX' + card_number[-4:],
                    'luhn_valid': True
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _identify_card_type(self, card_number: str) -> str:
        """Identify credit card type from number"""
        if card_number[0] == '4':
            return 'Visa'
        elif card_number[0] == '5':
            return 'Mastercard'
        elif card_number[:2] in ['34', '37']:
            return 'American Express'
        elif card_number[:2] in ['36', '38'] or card_number[:3] in ['300', '301', '302', '303', '304', '305']:
            return 'Diners Club'
        elif card_number[:4] in ['6011'] or card_number[:2] == '65':
            return 'Discover'
        else:
            return 'Unknown'
    
    def _extract_names(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract potential names (basic pattern matching)"""
        results = []
        
        # Pattern for names (Capital Letter followed by lowercase, 2-3 words)
        name_pattern = r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?)\b'
        
        for match in re.finditer(name_pattern, text):
            name = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Skip common false positives
            skip_words = ['The', 'And', 'But', 'For', 'Nor', 'Yet', 'So']
            if any(word in name for word in skip_words):
                continue
            
            # Check if context suggests this is a name
            name_keywords = ['name', 'contact', 'by', 'author', 'posted by', 'mr', 'ms', 'dr']
            context_lower = context.lower()
            confidence = 0.4
            
            if any(keyword in context_lower for keyword in name_keywords):
                confidence = 0.7
            
            # Only include if confidence is reasonable
            if confidence >= 0.6:
                results.append(ExtractionResult(
                    category='pii',
                    confidence=confidence,
                    risk_level='medium',
                    data={
                        'type': 'name',
                        'name': name
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_addresses(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract physical addresses (basic pattern matching)"""
        results = []
        
        # Pattern for street addresses (simplified)
        address_pattern = r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way)\b'
        
        for match in re.finditer(address_pattern, text):
            address = match.group(0)
            context = self.get_context(text, match.start(), match.end(), 150)
            
            results.append(ExtractionResult(
                category='pii',
                confidence=0.65,
                risk_level='high',
                data={
                    'type': 'address',
                    'address': address
                },
                context=context,
                location=url
            ))
        
        # Pattern for zip codes with context
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        for match in re.finditer(zip_pattern, text):
            zip_code = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Only include if context suggests address
            address_keywords = ['zip', 'address', 'mail', 'shipping', 'location']
            if any(keyword in context.lower() for keyword in address_keywords):
                results.append(ExtractionResult(
                    category='pii',
                    confidence=0.75,
                    risk_level='medium',
                    data={
                        'type': 'zip_code',
                        'zip_code': zip_code
                    },
                    context=context,
                    location=url
                ))
        
        return results

