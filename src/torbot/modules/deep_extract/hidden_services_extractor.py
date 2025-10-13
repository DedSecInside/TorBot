"""
Hidden Services Intelligence Extractor
"""

import re
from typing import List, Dict
from .base import BaseExtractor, ExtractionResult, RegexPatterns


class HiddenServicesExtractor(BaseExtractor):
    """Extract and classify hidden service (.onion) links"""
    
    # Service type keywords for classification
    SERVICE_KEYWORDS = {
        'marketplace': ['market', 'shop', 'store', 'buy', 'sell', 'vendor', 'product', 'cart', 'price'],
        'forum': ['forum', 'board', 'discussion', 'thread', 'post', 'reply', 'topic', 'community'],
        'hosting': ['host', 'hosting', 'server', 'vps', 'dedicated', 'upload', 'file'],
        'email': ['mail', 'email', 'inbox', 'message', 'webmail'],
        'wiki': ['wiki', 'encyclopedia', 'article', 'knowledge'],
        'blog': ['blog', 'news', 'article', 'post'],
        'paste': ['paste', 'pastebin', 'snippet'],
        'search': ['search', 'index', 'directory', 'engine'],
        'chat': ['chat', 'irc', 'messenger', 'talk'],
        'financial': ['bank', 'bitcoin', 'crypto', 'wallet', 'exchange', 'atm'],
        'social': ['social', 'network', 'profile', 'friend'],
        'darknet': ['darknet', 'deep web', 'anonymous', 'privacy'],
    }
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract hidden service links and information"""
        results = []
        
        # Extract v2 onion links
        results.extend(self._extract_onion_links(text, url, RegexPatterns.ONION_V2, 'v2'))
        
        # Extract v3 onion links
        results.extend(self._extract_onion_links(text, url, RegexPatterns.ONION_V3, 'v3'))
        
        # Extract service descriptions and metadata
        results.extend(self._extract_service_metadata(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_onion_links(self, text: str, url: str, pattern: str, version: str) -> List[ExtractionResult]:
        """Extract onion links with classification"""
        results = []
        
        for match in re.finditer(pattern, text):
            onion_address = match.group(0)
            context = self.get_context(text, match.start(), match.end(), 200)
            
            # Classify service type based on context
            service_type, confidence_adjustment = self._classify_service(context)
            
            # Calculate trust score (basic heuristic)
            trust_score = self._calculate_trust_score(context, onion_address)
            
            base_confidence = 0.95 if version == 'v3' else 0.9
            
            results.append(ExtractionResult(
                category='hidden_services',
                confidence=base_confidence + confidence_adjustment,
                risk_level=self._determine_risk_level(service_type),
                data={
                    'type': 'onion_link',
                    'address': onion_address,
                    'full_url': f'http://{onion_address}',
                    'version': version,
                    'service_type': service_type,
                    'trust_score': trust_score
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _classify_service(self, context: str) -> tuple:
        """Classify hidden service based on context"""
        context_lower = context.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.SERVICE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in context_lower)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return 'unknown', 0.0
        
        # Get category with highest score
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        
        # Confidence adjustment based on match strength
        confidence_adjustment = min(0.1 * max_score, 0.3)
        
        return best_category, confidence_adjustment
    
    def _calculate_trust_score(self, context: str, address: str) -> float:
        """Calculate basic trust score for hidden service"""
        score = 0.5  # Base score
        
        context_lower = context.lower()
        
        # Positive indicators
        positive_keywords = ['verified', 'trusted', 'official', 'secure', 'reputation', 'reviews']
        score += 0.05 * sum(1 for keyword in positive_keywords if keyword in context_lower)
        
        # Negative indicators
        negative_keywords = ['scam', 'fake', 'phishing', 'warning', 'unsafe', 'malware', 'virus']
        score -= 0.1 * sum(1 for keyword in negative_keywords if keyword in context_lower)
        
        # Clamp score between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _determine_risk_level(self, service_type: str) -> str:
        """Determine risk level based on service type"""
        high_risk_types = ['marketplace', 'financial', 'darknet']
        medium_risk_types = ['forum', 'chat', 'paste', 'hosting']
        
        if service_type in high_risk_types:
            return 'high'
        elif service_type in medium_risk_types:
            return 'medium'
        else:
            return 'low'
    
    def _extract_service_metadata(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract hidden service metadata and descriptions"""
        results = []
        
        # Extract service titles
        title_patterns = [
            r'<title>([^<]{5,100})</title>',
            r'(?i)service name[:\s]+([^\n]{5,50})',
            r'(?i)site name[:\s]+([^\n]{5,50})'
        ]
        
        for pattern in title_patterns:
            for match in re.finditer(pattern, text):
                title = match.group(1).strip()
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='hidden_services',
                    confidence=0.8,
                    risk_level='low',
                    data={
                        'type': 'service_title',
                        'title': title
                    },
                    context=context,
                    location=url
                ))
        
        # Extract service descriptions
        desc_patterns = [
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']{10,200})["\']',
            r'(?i)description[:\s]+([^\n]{10,200})',
            r'(?i)about[:\s]+([^\n]{10,200})'
        ]
        
        for pattern in desc_patterns:
            for match in re.finditer(pattern, text):
                description = match.group(1).strip()
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='hidden_services',
                    confidence=0.75,
                    risk_level='low',
                    data={
                        'type': 'service_description',
                        'description': description
                    },
                    context=context,
                    location=url
                ))
        
        # Extract onion directory listings
        directory_pattern = r'(?i)(?:directory|index|list)[:\s]*\n((?:[a-z2-7]{16,56}\.onion[^\n]*\n){3,})'
        for match in re.finditer(directory_pattern, text):
            listing = match.group(1)
            context = self.get_context(text, match.start(), match.end(), 300)
            
            # Count links in listing
            onion_count = len(re.findall(r'[a-z2-7]{16,56}\.onion', listing))
            
            results.append(ExtractionResult(
                category='hidden_services',
                confidence=0.85,
                risk_level='medium',
                data={
                    'type': 'directory_listing',
                    'link_count': onion_count,
                    'listing_preview': listing[:200]
                },
                context=context,
                location=url
            ))
        
        return results

