"""
Credential and Authentication Data Extractor
"""

import re
from typing import List
from .base import BaseExtractor, ExtractionResult, RegexPatterns


class CredentialsExtractor(BaseExtractor):
    """Extract credentials and authentication data from content"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract various types of credentials"""
        results = []
        
        # Extract username:password pairs
        results.extend(self._extract_username_password_pairs(text, url))
        
        # Extract API keys
        results.extend(self._extract_api_keys(text, url))
        
        # Extract JWT tokens
        results.extend(self._extract_jwt_tokens(text, url))
        
        # Extract password hashes
        results.extend(self._extract_password_hashes(text, url))
        
        # Extract session tokens
        results.extend(self._extract_session_tokens(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_username_password_pairs(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract username:password combinations"""
        results = []
        
        # Pattern 1: username:password format
        pattern1 = r'(?m)^([a-zA-Z0-9._%+-]+):([^\s:]+)$'
        for match in re.finditer(pattern1, text):
            username, password = match.groups()
            
            # Skip if it looks like a URL or ratio
            if '/' in username or '/' in password:
                continue
            
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.85,
                risk_level='critical',
                data={
                    'type': 'username_password',
                    'username': username,
                    'password': password,
                    'format': 'username:password'
                },
                context=context,
                location=url
            ))
        
        # Pattern 2: email:password format
        pattern2 = r'(' + RegexPatterns.EMAIL + r'):([^\s:]+)'
        for match in re.finditer(pattern2, text):
            email = match.group(1)
            password = match.group(2)
            
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.9,
                risk_level='critical',
                data={
                    'type': 'email_password',
                    'email': email,
                    'password': password,
                    'format': 'email:password'
                },
                context=context,
                location=url
            ))
        
        # Pattern 3: Labeled credentials
        pattern3 = r'(?i)(?:username|user|login|email)[\s:=]+([^\s:]+)[\s\n\r]{0,10}(?:password|pass|pwd)[\s:=]+([^\s\n\r]+)'
        for match in re.finditer(pattern3, text):
            username = match.group(1).strip()
            password = match.group(2).strip()
            
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.8,
                risk_level='critical',
                data={
                    'type': 'labeled_credentials',
                    'username': username,
                    'password': password,
                    'format': 'labeled'
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_api_keys(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract API keys and tokens"""
        results = []
        
        # AWS Access Keys
        for match in re.finditer(RegexPatterns.API_KEY_AWS, text):
            key = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.95,
                risk_level='critical',
                data={
                    'type': 'aws_access_key',
                    'key': key,
                    'provider': 'AWS'
                },
                context=context,
                location=url
            ))
        
        # GitHub tokens
        github_pattern = r'\bgh[pousr]_[A-Za-z0-9_]{36,}\b'
        for match in re.finditer(github_pattern, text):
            key = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.95,
                risk_level='critical',
                data={
                    'type': 'github_token',
                    'key': key,
                    'provider': 'GitHub'
                },
                context=context,
                location=url
            ))
        
        # Slack tokens
        slack_pattern = r'\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}\b'
        for match in re.finditer(slack_pattern, text):
            key = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.95,
                risk_level='critical',
                data={
                    'type': 'slack_token',
                    'key': key,
                    'provider': 'Slack'
                },
                context=context,
                location=url
            ))
        
        # Generic API keys (look for common keywords)
        api_key_patterns = [
            r'(?i)api[_-]?key[\s:=]+([a-zA-Z0-9_-]{20,})',
            r'(?i)apikey[\s:=]+([a-zA-Z0-9_-]{20,})',
            r'(?i)access[_-]?token[\s:=]+([a-zA-Z0-9_-]{20,})',
        ]
        
        for pattern in api_key_patterns:
            for match in re.finditer(pattern, text):
                key = match.group(1)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='credentials',
                    confidence=0.7,
                    risk_level='high',
                    data={
                        'type': 'generic_api_key',
                        'key': key,
                        'provider': 'Unknown'
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_jwt_tokens(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract JWT tokens"""
        results = []
        
        for match in re.finditer(RegexPatterns.JWT_TOKEN, text):
            token = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.9,
                risk_level='high',
                data={
                    'type': 'jwt_token',
                    'token': token[:50] + '...' if len(token) > 50 else token
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_password_hashes(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract password hashes"""
        results = []
        
        # Look for hashes in common formats
        hash_patterns = [
            (RegexPatterns.MD5, 'MD5', 0.6),
            (RegexPatterns.SHA1, 'SHA1', 0.65),
            (RegexPatterns.SHA256, 'SHA256', 0.7),
        ]
        
        for pattern, hash_type, confidence in hash_patterns:
            # Look for hashes with password-related context
            for match in re.finditer(pattern, text):
                hash_value = match.group(0)
                context = self.get_context(text, match.start(), match.end(), 200)
                
                # Check if context suggests this is a password hash
                password_keywords = ['password', 'passwd', 'pwd', 'hash', 'credential']
                if any(keyword in context.lower() for keyword in password_keywords):
                    results.append(ExtractionResult(
                        category='credentials',
                        confidence=confidence + 0.2,
                        risk_level='high',
                        data={
                            'type': 'password_hash',
                            'hash_type': hash_type,
                            'hash': hash_value
                        },
                        context=context,
                        location=url
                    ))
        
        # Bcrypt hashes
        bcrypt_pattern = r'\$2[ayb]\$[0-9]{2}\$[A-Za-z0-9./]{53}'
        for match in re.finditer(bcrypt_pattern, text):
            hash_value = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='credentials',
                confidence=0.95,
                risk_level='high',
                data={
                    'type': 'password_hash',
                    'hash_type': 'bcrypt',
                    'hash': hash_value
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_session_tokens(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract session identifiers and tokens"""
        results = []
        
        session_patterns = [
            r'(?i)session[_-]?id[\s:=]+([a-zA-Z0-9_-]{20,})',
            r'(?i)phpsessid=([a-zA-Z0-9]{26,})',
            r'(?i)jsessionid=([a-zA-Z0-9]{32,})',
            r'(?i)asp\.net_sessionid=([a-zA-Z0-9]{24,})',
        ]
        
        for pattern in session_patterns:
            for match in re.finditer(pattern, text):
                session_id = match.group(1) if match.lastindex else match.group(0)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='credentials',
                    confidence=0.75,
                    risk_level='medium',
                    data={
                        'type': 'session_token',
                        'session_id': session_id
                    },
                    context=context,
                    location=url
                ))
        
        return results

