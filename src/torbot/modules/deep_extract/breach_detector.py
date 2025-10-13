"""
Data Breach Detection Extractor
"""

import re
from typing import List, Dict
from .base import BaseExtractor, ExtractionResult


class BreachDetector(BaseExtractor):
    """Detect and analyze data breach dumps and credential leaks"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Detect data breaches and credential dumps"""
        results = []
        
        # Detect breach announcements
        results.extend(self._detect_breach_announcements(text, url))
        
        # Detect credential dumps
        results.extend(self._detect_credential_dumps(text, url))
        
        # Detect database leaks
        results.extend(self._detect_database_leaks(text, url))
        
        # Detect combo lists
        results.extend(self._detect_combo_lists(text, url))
        
        # Estimate breach size
        results.extend(self._estimate_breach_size(text, url))
        
        self.results.extend(results)
        return results
    
    def _detect_breach_announcements(self, text: str, url: str) -> List[ExtractionResult]:
        """Detect breach announcements and posts"""
        results = []
        
        breach_keywords = [
            r'(?i)\b(?:database|db|data)\s+(?:breach|leak|dump|hacked|compromised)\b',
            r'(?i)\b(?:breach|leak)\s+(?:of|from)\s+([A-Z][a-zA-Z0-9\s]{2,30})\b',
            r'(?i)\bhacked\s+database\b',
            r'(?i)\bdata\s+dump\b',
            r'(?i)\bstolen\s+(?:database|data|credentials)\b'
        ]
        
        for pattern in breach_keywords:
            for match in re.finditer(pattern, text):
                context = self.get_context(text, match.start(), match.end(), 250)
                
                # Try to extract company/target name
                target = match.group(1) if match.lastindex else None
                
                results.append(ExtractionResult(
                    category='data_breach',
                    confidence=0.85,
                    risk_level='critical',
                    data={
                        'type': 'breach_announcement',
                        'target': target,
                        'indicator': match.group(0)
                    },
                    context=context,
                    location=url
                ))
        
        # Specific breach format patterns
        breach_format_patterns = [
            r'(?i)(?:database|dump):\s*([^\n]{10,100})',
            r'(?i)source:\s*([^\n]{5,100})',
            r'(?i)leaked\s+from:\s*([^\n]{5,100})'
        ]
        
        for pattern in breach_format_patterns:
            for match in re.finditer(pattern, text):
                source_info = match.group(1).strip()
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='data_breach',
                    confidence=0.8,
                    risk_level='high',
                    data={
                        'type': 'breach_source',
                        'source': source_info
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _detect_credential_dumps(self, text: str, url: str) -> List[ExtractionResult]:
        """Detect credential dump patterns"""
        results = []
        
        # Count email:password patterns
        email_pass_pattern = r'(?m)^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s:]+$'
        matches = list(re.finditer(email_pass_pattern, text))
        
        if len(matches) >= 5:  # If we find multiple credential pairs
            # Get first and last match for context
            first_match = matches[0]
            last_match = matches[-1]
            
            context = self.get_context(
                text, 
                first_match.start(), 
                min(last_match.end(), first_match.start() + 500),
                100
            )
            
            # Extract sample credentials (first 3)
            samples = [matches[i].group(0) for i in range(min(3, len(matches)))]
            
            results.append(ExtractionResult(
                category='data_breach',
                confidence=0.95,
                risk_level='critical',
                data={
                    'type': 'credential_dump',
                    'format': 'email:password',
                    'estimated_count': len(matches),
                    'samples': samples
                },
                context=context,
                location=url
            ))
        
        # Count username:password patterns
        user_pass_pattern = r'(?m)^[a-zA-Z0-9_-]{3,20}:[^\s:]+$'
        matches = list(re.finditer(user_pass_pattern, text))
        
        if len(matches) >= 10:  # Higher threshold for username:password
            first_match = matches[0]
            context = self.get_context(text, first_match.start(), first_match.start() + 500)
            
            samples = [matches[i].group(0) for i in range(min(3, len(matches)))]
            
            results.append(ExtractionResult(
                category='data_breach',
                confidence=0.85,
                risk_level='critical',
                data={
                    'type': 'credential_dump',
                    'format': 'username:password',
                    'estimated_count': len(matches),
                    'samples': samples
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _detect_database_leaks(self, text: str, url: str) -> List[ExtractionResult]:
        """Detect database dump patterns"""
        results = []
        
        # SQL dump indicators
        sql_patterns = [
            r'(?i)(?:INSERT INTO|CREATE TABLE|DROP TABLE)',
            r'(?i)(?:mysql|postgresql|mongodb|mssql)\s+dump',
            r'(?i)\.sql\s+(?:file|dump|backup)'
        ]
        
        for pattern in sql_patterns:
            matches = list(re.finditer(pattern, text))
            if matches:
                first_match = matches[0]
                context = self.get_context(text, first_match.start(), first_match.end(), 200)
                
                results.append(ExtractionResult(
                    category='data_breach',
                    confidence=0.9,
                    risk_level='high',
                    data={
                        'type': 'database_dump',
                        'dump_type': 'SQL',
                        'indicator_count': len(matches)
                    },
                    context=context,
                    location=url
                ))
                break  # Only report once per type
        
        # JSON database dumps
        if text.count('"password"') >= 5 or text.count('"email"') >= 5:
            # Look for JSON array of user objects
            json_user_pattern = r'\{\s*"(?:email|username|user)"[^}]{10,200}"password"[^}]{5,100}\}'
            matches = list(re.finditer(json_user_pattern, text, re.IGNORECASE))
            
            if len(matches) >= 3:
                first_match = matches[0]
                context = self.get_context(text, first_match.start(), first_match.end(), 150)
                
                results.append(ExtractionResult(
                    category='data_breach',
                    confidence=0.85,
                    risk_level='high',
                    data={
                        'type': 'database_dump',
                        'dump_type': 'JSON',
                        'record_count': len(matches)
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _detect_combo_lists(self, text: str, url: str) -> List[ExtractionResult]:
        """Detect combo lists (credential lists from multiple sources)"""
        results = []
        
        combo_keywords = [
            r'(?i)\bcombo\s+list\b',
            r'(?i)\bcombos\b.*\b(?:million|thousand|k)\b',
            r'(?i)\bmixed\s+(?:credentials|combos)\b',
            r'(?i)\b(?:private|fresh)\s+combos\b'
        ]
        
        for pattern in combo_keywords:
            for match in re.finditer(pattern, text):
                context = self.get_context(text, match.start(), match.end(), 250)
                
                # Try to extract size
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:million|mil|m|thousand|k)', context, re.IGNORECASE)
                estimated_size = None
                if size_match:
                    num = float(size_match.group(1))
                    unit = size_match.group(2).lower()
                    if 'm' in unit:
                        estimated_size = int(num * 1000000)
                    elif 'k' in unit:
                        estimated_size = int(num * 1000)
                
                results.append(ExtractionResult(
                    category='data_breach',
                    confidence=0.9,
                    risk_level='critical',
                    data={
                        'type': 'combo_list',
                        'estimated_size': estimated_size
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _estimate_breach_size(self, text: str, url: str) -> List[ExtractionResult]:
        """Estimate the size of data breaches mentioned"""
        results = []
        
        size_patterns = [
            r'(?i)(\d+(?:\.\d+)?)\s*(million|billion|thousand|mil|m|k|gb|mb)\s+(?:records?|users?|accounts?|credentials?|passwords?|emails?)',
            r'(?i)(?:contains|includes|total)[:\s]+(\d+(?:\.\d+)?)\s*(million|billion|thousand|mil|m|k)\s+(?:records?|entries?)',
        ]
        
        for pattern in size_patterns:
            for match in re.finditer(pattern, text):
                number = float(match.group(1))
                unit = match.group(2).lower()
                context = self.get_context(text, match.start(), match.end())
                
                # Convert to actual count
                multiplier = 1
                if 'billion' in unit or 'b' == unit:
                    multiplier = 1000000000
                elif 'million' in unit or 'm' in unit:
                    multiplier = 1000000
                elif 'thousand' in unit or 'k' in unit:
                    multiplier = 1000
                
                estimated_count = int(number * multiplier)
                
                # Determine risk level based on size
                risk_level = 'medium'
                if estimated_count >= 1000000:
                    risk_level = 'critical'
                elif estimated_count >= 100000:
                    risk_level = 'high'
                
                results.append(ExtractionResult(
                    category='data_breach',
                    confidence=0.85,
                    risk_level=risk_level,
                    data={
                        'type': 'breach_size',
                        'estimated_records': estimated_count,
                        'original_value': f"{number} {unit}"
                    },
                    context=context,
                    location=url
                ))
        
        return results

