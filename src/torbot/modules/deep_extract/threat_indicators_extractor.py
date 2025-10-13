"""
Threat Indicators (IoCs) Extractor
"""

import re
from typing import List
from .base import BaseExtractor, ExtractionResult, RegexPatterns


class ThreatIndicatorsExtractor(BaseExtractor):
    """Extract Indicators of Compromise and threat intelligence"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract various threat indicators"""
        results = []
        
        # Extract IP addresses
        results.extend(self._extract_ip_addresses(text, url))
        
        # Extract domains
        results.extend(self._extract_domains(text, url))
        
        # Extract file hashes
        results.extend(self._extract_file_hashes(text, url))
        
        # Extract CVE references
        results.extend(self._extract_cves(text, url))
        
        # Extract malware indicators
        results.extend(self._extract_malware_indicators(text, url))
        
        # Extract C2 infrastructure patterns
        results.extend(self._extract_c2_patterns(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_ip_addresses(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract IPv4 and IPv6 addresses"""
        results = []
        
        # IPv4
        for match in re.finditer(RegexPatterns.IPV4, text):
            ip = match.group(0)
            
            # Skip common false positives
            if ip.startswith('0.') or ip.startswith('255.255.255.'):
                continue
            
            context = self.get_context(text, match.start(), match.end())
            
            # Classify IP type
            ip_type = self._classify_ip_type(ip)
            
            results.append(ExtractionResult(
                category='threat_indicators',
                confidence=0.8,
                risk_level=self._get_ip_risk_level(ip, context),
                data={
                    'type': 'ipv4',
                    'ip_address': ip,
                    'ip_type': ip_type
                },
                context=context,
                location=url
            ))
        
        # IPv6
        for match in re.finditer(RegexPatterns.IPV6, text):
            ip = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='threat_indicators',
                confidence=0.85,
                risk_level='medium',
                data={
                    'type': 'ipv6',
                    'ip_address': ip
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _classify_ip_type(self, ip: str) -> str:
        """Classify IP address type"""
        octets = ip.split('.')
        first_octet = int(octets[0])
        
        # Private ranges
        if first_octet == 10:
            return 'private'
        elif first_octet == 172 and 16 <= int(octets[1]) <= 31:
            return 'private'
        elif first_octet == 192 and int(octets[1]) == 168:
            return 'private'
        elif first_octet == 127:
            return 'loopback'
        else:
            return 'public'
    
    def _get_ip_risk_level(self, ip: str, context: str) -> str:
        """Determine risk level for IP address"""
        context_lower = context.lower()
        
        high_risk_keywords = ['c2', 'command', 'control', 'malware', 'exploit', 'attack']
        if any(keyword in context_lower for keyword in high_risk_keywords):
            return 'high'
        
        ip_type = self._classify_ip_type(ip)
        if ip_type == 'public':
            return 'medium'
        else:
            return 'low'
    
    def _extract_domains(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract domain names (excluding .onion which are handled separately)"""
        results = []
        
        for match in re.finditer(RegexPatterns.DOMAIN, text):
            domain = match.group(0)
            
            # Skip .onion domains and common false positives
            if domain.endswith('.onion') or domain.endswith('.local'):
                continue
            
            # Skip very common domains unless in suspicious context
            common_domains = ['google.com', 'facebook.com', 'twitter.com', 'example.com']
            if domain in common_domains:
                continue
            
            context = self.get_context(text, match.start(), match.end())
            
            # Check for suspicious indicators
            suspicious_keywords = ['phishing', 'fake', 'malicious', 'compromised', 'infected']
            confidence = 0.7
            risk_level = 'medium'
            
            if any(keyword in context.lower() for keyword in suspicious_keywords):
                confidence = 0.9
                risk_level = 'high'
            
            results.append(ExtractionResult(
                category='threat_indicators',
                confidence=confidence,
                risk_level=risk_level,
                data={
                    'type': 'domain',
                    'domain': domain,
                    'tld': domain.split('.')[-1]
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_file_hashes(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract file hashes (MD5, SHA1, SHA256)"""
        results = []
        
        hash_types = [
            (RegexPatterns.MD5, 'MD5', 32),
            (RegexPatterns.SHA1, 'SHA1', 40),
            (RegexPatterns.SHA256, 'SHA256', 64)
        ]
        
        for pattern, hash_type, length in hash_types:
            for match in re.finditer(pattern, text):
                hash_value = match.group(0)
                context = self.get_context(text, match.start(), match.end(), 200)
                
                # Check if context suggests this is a file hash
                file_keywords = ['hash', 'checksum', 'md5', 'sha1', 'sha256', 'file', 'malware', 'sample']
                confidence = 0.5
                
                if any(keyword in context.lower() for keyword in file_keywords):
                    confidence = 0.85
                
                # Only include if confidence is reasonable
                if confidence >= 0.7:
                    results.append(ExtractionResult(
                        category='threat_indicators',
                        confidence=confidence,
                        risk_level='medium',
                        data={
                            'type': 'file_hash',
                            'hash_type': hash_type,
                            'hash': hash_value,
                            'length': length
                        },
                        context=context,
                        location=url
                    ))
        
        return results
    
    def _extract_cves(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract CVE (Common Vulnerabilities and Exposures) references"""
        results = []
        
        for match in re.finditer(RegexPatterns.CVE, text):
            cve = match.group(0)
            context = self.get_context(text, match.start(), match.end(), 250)
            
            # Extract year from CVE
            year = cve.split('-')[1]
            
            # Check for exploit mentions
            exploit_keywords = ['exploit', 'poc', 'proof of concept', '0day', 'zero day']
            risk_level = 'medium'
            confidence = 0.95
            
            if any(keyword in context.lower() for keyword in exploit_keywords):
                risk_level = 'high'
            
            results.append(ExtractionResult(
                category='threat_indicators',
                confidence=confidence,
                risk_level=risk_level,
                data={
                    'type': 'cve',
                    'cve_id': cve,
                    'year': year
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_malware_indicators(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract malware-related indicators"""
        results = []
        
        # Common malware families
        malware_families = [
            'wannacry', 'emotet', 'trickbot', 'ryuk', 'maze', 'conti',
            'ransomware', 'trojan', 'backdoor', 'rootkit', 'keylogger',
            'botnet', 'mirai', 'cobalt strike', 'metasploit'
        ]
        
        for malware in malware_families:
            pattern = r'\b' + re.escape(malware) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context = self.get_context(text, match.start(), match.end(), 200)
                
                results.append(ExtractionResult(
                    category='threat_indicators',
                    confidence=0.85,
                    risk_level='high',
                    data={
                        'type': 'malware_mention',
                        'malware_family': malware.title()
                    },
                    context=context,
                    location=url
                ))
        
        # Suspicious file extensions
        suspicious_extensions = [
            r'\b\w+\.(?:exe|dll|sys|bat|ps1|vbs|js|scr|com|pif|msi)\b'
        ]
        
        for pattern in suspicious_extensions:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                filename = match.group(0)
                context = self.get_context(text, match.start(), match.end())
                
                # Check if context suggests malware
                malware_keywords = ['malware', 'virus', 'trojan', 'payload', 'dropper', 'loader']
                if any(keyword in context.lower() for keyword in malware_keywords):
                    results.append(ExtractionResult(
                        category='threat_indicators',
                        confidence=0.75,
                        risk_level='high',
                        data={
                            'type': 'suspicious_file',
                            'filename': filename,
                            'extension': filename.split('.')[-1]
                        },
                        context=context,
                        location=url
                    ))
        
        return results
    
    def _extract_c2_patterns(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract Command & Control infrastructure patterns"""
        results = []
        
        c2_keywords = [
            r'(?i)c2\s+(?:server|infrastructure|domain|ip)',
            r'(?i)command\s+(?:and|&)\s+control',
            r'(?i)c&c\s+(?:server|infrastructure)',
            r'(?i)callback\s+(?:url|domain|server)',
            r'(?i)exfil(?:tration)?\s+(?:server|domain)'
        ]
        
        for pattern in c2_keywords:
            for match in re.finditer(pattern, text):
                context = self.get_context(text, match.start(), match.end(), 250)
                
                results.append(ExtractionResult(
                    category='threat_indicators',
                    confidence=0.9,
                    risk_level='high',
                    data={
                        'type': 'c2_infrastructure',
                        'indicator_type': 'keyword_match'
                    },
                    context=context,
                    location=url
                ))
        
        return results

