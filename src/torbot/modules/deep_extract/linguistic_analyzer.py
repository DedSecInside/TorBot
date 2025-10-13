"""
Linguistic Analysis and Attribution Extractor
"""

import re
from typing import List, Dict
from collections import Counter
from .base import BaseExtractor, ExtractionResult


class LinguisticAnalyzer(BaseExtractor):
    """Analyze language patterns for threat actor attribution"""
    
    # Dark web slang and terminology
    DARKWEB_SLANG = {
        'opsec': 'operational security',
        'doxx': 'reveal personal information',
        'swat': 'fake emergency call',
        'rat': 'remote access trojan',
        'fe': 'finalize early',
        'pgp': 'pretty good privacy',
        'dnm': 'darknet market',
        'clearnet': 'regular internet',
        'honeypot': 'trap/sting operation',
        'fud': 'fully undetectable',
        'crypter': 'encryption tool',
        'loader': 'malware loader',
        'stub': 'malware component',
        'botnet': 'network of infected computers',
        'c2': 'command and control',
        'exploit': 'security vulnerability tool',
        'zero day': 'undisclosed vulnerability',
        'phish': 'fraudulent attempt',
        'carding': 'credit card fraud',
        'dump': 'stolen data',
        'fullz': 'complete identity information',
        'bins': 'bank identification numbers',
        'cvv': 'card verification value',
        'sock': 'socks proxy',
        'vpn': 'virtual private network',
        'tor': 'the onion router',
        'tails': 'security-focused os',
        'whonix': 'privacy-focused os',
        'kali': 'penetration testing os',
        'metasploit': 'exploitation framework',
    }
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Perform linguistic analysis"""
        results = []
        
        # Detect dark web slang
        results.extend(self._detect_slang(text, url))
        
        # Analyze technical sophistication
        results.extend(self._analyze_technical_sophistication(text, url))
        
        # Detect language patterns
        results.extend(self._detect_language_patterns(text, url))
        
        # Analyze communication style
        results.extend(self._analyze_communication_style(text, url))
        
        self.results.extend(results)
        return results
    
    def _detect_slang(self, text: str, url: str) -> List[ExtractionResult]:
        """Detect dark web slang and terminology"""
        results = []
        text_lower = text.lower()
        
        found_terms = []
        for term, meaning in self.DARKWEB_SLANG.items():
            # Look for whole word matches
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower):
                found_terms.append({
                    'term': term,
                    'meaning': meaning
                })
        
        if found_terms:
            # Calculate confidence based on number of terms
            confidence = min(0.5 + (len(found_terms) * 0.05), 0.95)
            
            # Get context for first term
            first_term = found_terms[0]['term']
            match = re.search(r'\b' + re.escape(first_term) + r'\b', text_lower)
            if match:
                context = self.get_context(text, match.start(), match.end(), 150)
            else:
                context = text[:200]
            
            results.append(ExtractionResult(
                category='linguistic_analysis',
                confidence=confidence,
                risk_level='medium',
                data={
                    'type': 'darkweb_slang',
                    'terms_found': found_terms,
                    'term_count': len(found_terms)
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _analyze_technical_sophistication(self, text: str, url: str) -> List[ExtractionResult]:
        """Analyze technical sophistication of content"""
        results = []
        
        # Technical indicators
        technical_terms = {
            'high': [
                'zero-day', '0day', 'exploit', 'vulnerability', 'payload',
                'shellcode', 'buffer overflow', 'sql injection', 'xss',
                'cryptography', 'encryption', 'obfuscation', 'polymorphic',
                'reverse engineering', 'assembly', 'kernel', 'rootkit'
            ],
            'medium': [
                'malware', 'trojan', 'virus', 'phishing', 'social engineering',
                'brute force', 'dictionary attack', 'ddos', 'botnet',
                'proxy', 'vpn', 'anonymous', 'tor', 'bitcoin'
            ],
            'low': [
                'hack', 'password', 'login', 'account', 'username',
                'free', 'download', 'easy', 'simple', 'tutorial'
            ]
        }
        
        text_lower = text.lower()
        
        scores = {'high': 0, 'medium': 0, 'low': 0}
        found_terms = {'high': [], 'medium': [], 'low': []}
        
        for level, terms in technical_terms.items():
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                count = len(re.findall(pattern, text_lower))
                if count > 0:
                    scores[level] += count
                    found_terms[level].append(term)
        
        # Calculate sophistication level
        total_score = scores['high'] * 3 + scores['medium'] * 2 + scores['low']
        
        if total_score > 0:
            sophistication_level = 'low'
            if scores['high'] >= 3:
                sophistication_level = 'high'
            elif scores['high'] >= 1 or scores['medium'] >= 5:
                sophistication_level = 'medium'
            
            results.append(ExtractionResult(
                category='linguistic_analysis',
                confidence=0.75,
                risk_level='medium',
                data={
                    'type': 'technical_sophistication',
                    'level': sophistication_level,
                    'high_terms': found_terms['high'][:5],
                    'medium_terms': found_terms['medium'][:5],
                    'score_breakdown': scores
                },
                context=text[:300],
                location=url
            ))
        
        return results
    
    def _detect_language_patterns(self, text: str, url: str) -> List[ExtractionResult]:
        """Detect language patterns that might indicate geographic origin"""
        results = []
        
        # British vs American English indicators
        british_spellings = ['colour', 'honour', 'favourite', 'centre', 'defence', 'organisation']
        american_spellings = ['color', 'honor', 'favorite', 'center', 'defense', 'organization']
        
        british_count = sum(1 for word in british_spellings if word in text.lower())
        american_count = sum(1 for word in american_spellings if word in text.lower())
        
        if british_count > 0 or american_count > 0:
            variant = 'British English' if british_count > american_count else 'American English'
            confidence = 0.6 + (abs(british_count - american_count) * 0.1)
            confidence = min(confidence, 0.9)
            
            results.append(ExtractionResult(
                category='linguistic_analysis',
                confidence=confidence,
                risk_level='low',
                data={
                    'type': 'english_variant',
                    'variant': variant,
                    'indicators': {
                        'british': british_count,
                        'american': american_count
                    }
                },
                context=text[:200],
                location=url
            ))
        
        # Common non-English phrases that appear in English text
        foreign_patterns = [
            (r'\b(?:bonjour|merci|oui|non)\b', 'French'),
            (r'\b(?:hola|gracias|por favor|sí|no)\b', 'Spanish'),
            (r'\b(?:hallo|danke|bitte|ja|nein)\b', 'German'),
            (r'\b(?:привет|спасибо|да|нет)\b', 'Russian'),
            (r'\b(?:你好|谢谢)\b', 'Chinese'),
        ]
        
        for pattern, language in foreign_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    context = self.get_context(text, match.start(), match.end())
                    
                    results.append(ExtractionResult(
                        category='linguistic_analysis',
                        confidence=0.7,
                        risk_level='low',
                        data={
                            'type': 'foreign_language_indicator',
                            'language': language
                        },
                        context=context,
                        location=url
                    ))
        
        return results
    
    def _analyze_communication_style(self, text: str, url: str) -> List[ExtractionResult]:
        """Analyze communication style and professionalism"""
        results = []
        
        # Count various style indicators
        indicators = {
            'professional': 0,
            'casual': 0,
            'aggressive': 0
        }
        
        # Professional indicators
        professional_terms = [
            'please', 'thank you', 'regards', 'sincerely', 'professional',
            'service', 'quality', 'guarantee', 'support', 'customer'
        ]
        
        # Casual indicators
        casual_terms = [
            'lol', 'btw', 'imo', 'tbh', 'af', 'gonna', 'wanna',
            'yeah', 'nah', 'dude', 'bro', 'guys'
        ]
        
        # Aggressive indicators
        aggressive_terms = [
            'fuck', 'shit', 'damn', 'idiot', 'stupid', 'scam',
            'warning', 'threat', 'revenge', 'attack', 'destroy'
        ]
        
        text_lower = text.lower()
        
        indicators['professional'] = sum(1 for term in professional_terms if term in text_lower)
        indicators['casual'] = sum(1 for term in casual_terms if term in text_lower)
        indicators['aggressive'] = sum(1 for term in aggressive_terms if term in text_lower)
        
        if sum(indicators.values()) >= 2:
            # Determine dominant style
            dominant_style = max(indicators, key=indicators.get)
            
            # Calculate confidence
            total = sum(indicators.values())
            confidence = 0.5 + (indicators[dominant_style] / total * 0.4)
            
            results.append(ExtractionResult(
                category='linguistic_analysis',
                confidence=confidence,
                risk_level='low',
                data={
                    'type': 'communication_style',
                    'style': dominant_style,
                    'indicators': indicators
                },
                context=text[:250],
                location=url
            ))
        
        return results

