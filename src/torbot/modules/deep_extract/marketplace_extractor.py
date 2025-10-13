"""
Dark Web Marketplace Intelligence Extractor
"""

import re
from typing import List
from .base import BaseExtractor, ExtractionResult


class MarketplaceExtractor(BaseExtractor):
    """Extract marketplace intelligence including products, vendors, and pricing"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract marketplace-related intelligence"""
        results = []
        
        # Extract product listings
        results.extend(self._extract_product_listings(text, url))
        
        # Extract vendor information
        results.extend(self._extract_vendor_info(text, url))
        
        # Extract pricing information
        results.extend(self._extract_pricing(text, url))
        
        # Extract shipping information
        results.extend(self._extract_shipping_info(text, url))
        
        # Extract escrow mentions
        results.extend(self._extract_escrow_info(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_product_listings(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract product/service listings"""
        results = []
        
        # Product patterns
        product_patterns = [
            r'(?i)(?:product|item|listing)[:\s]+([^\n]{5,100})',
            r'(?i)(?:selling|offering|available)[:\s]+([^\n]{5,100})',
        ]
        
        for pattern in product_patterns:
            for match in re.finditer(pattern, text):
                product_name = match.group(1).strip()
                context = self.get_context(text, match.start(), match.end(), 200)
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.7,
                    risk_level='high',
                    data={
                        'type': 'product_listing',
                        'product_name': product_name
                    },
                    context=context,
                    location=url
                ))
        
        # Category mentions
        categories = [
            'drugs', 'weapons', 'counterfeit', 'fraud', 'hacking',
            'malware', 'exploits', 'data', 'credentials', 'accounts',
            'documents', 'services', 'digital goods'
        ]
        
        for category in categories:
            pattern = r'\b' + re.escape(category) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.65,
                    risk_level='high',
                    data={
                        'type': 'product_category',
                        'category': category.title()
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_vendor_info(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract vendor/seller information"""
        results = []
        
        # Vendor name patterns
        vendor_patterns = [
            r'(?i)vendor[:\s]+([a-zA-Z0-9_-]{3,20})',
            r'(?i)seller[:\s]+([a-zA-Z0-9_-]{3,20})',
            r'(?i)(?:sold|shipped)\s+by[:\s]+([a-zA-Z0-9_-]{3,20})'
        ]
        
        for pattern in vendor_patterns:
            for match in re.finditer(pattern, text):
                vendor_name = match.group(1).strip()
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.8,
                    risk_level='medium',
                    data={
                        'type': 'vendor_name',
                        'vendor': vendor_name
                    },
                    context=context,
                    location=url
                ))
        
        # Vendor reputation/rating
        rating_patterns = [
            r'(?i)(?:rating|reputation|score)[:\s]+(\d+(?:\.\d+)?)\s*(?:/\s*(\d+))?',
            r'(?i)(\d+)\s*(?:stars?|⭐)',
            r'(?i)(\d+)%\s*positive'
        ]
        
        for pattern in rating_patterns:
            for match in re.finditer(pattern, text):
                rating = match.group(1)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.75,
                    risk_level='low',
                    data={
                        'type': 'vendor_rating',
                        'rating': rating
                    },
                    context=context,
                    location=url
                ))
        
        # Sales/transaction count
        sales_patterns = [
            r'(?i)(\d+)\s+(?:sales?|transactions?|orders?)',
            r'(?i)sold[:\s]+(\d+)\s+times?'
        ]
        
        for pattern in sales_patterns:
            for match in re.finditer(pattern, text):
                count = match.group(1)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.7,
                    risk_level='low',
                    data={
                        'type': 'sales_count',
                        'count': int(count)
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_pricing(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract pricing information"""
        results = []
        
        # Cryptocurrency pricing
        crypto_price_patterns = [
            r'(?i)price[:\s]+(\d+(?:\.\d+)?)\s*(btc|bitcoin|eth|ethereum|xmr|monero)',
            r'(?i)(\d+(?:\.\d+)?)\s*(btc|bitcoin|eth|ethereum|xmr|monero)',
            r'(?i)\$(\d+(?:\.\d+)?)\s*(?:usd)?'
        ]
        
        for pattern in crypto_price_patterns:
            for match in re.finditer(pattern, text):
                amount = match.group(1)
                currency = match.group(2) if match.lastindex >= 2 else 'USD'
                context = self.get_context(text, match.start(), match.end())
                
                # Check if context suggests this is a price
                price_keywords = ['price', 'cost', 'pay', 'payment', 'buy', 'purchase']
                if any(keyword in context.lower() for keyword in price_keywords):
                    results.append(ExtractionResult(
                        category='marketplace',
                        confidence=0.8,
                        risk_level='medium',
                        data={
                            'type': 'pricing',
                            'amount': float(amount),
                            'currency': currency.upper()
                        },
                        context=context,
                        location=url
                    ))
        
        # Quantity-based pricing
        quantity_pattern = r'(?i)(\d+)\s*(?:x|pcs?|pieces?|units?)[:\s]+.*?(\d+(?:\.\d+)?)\s*(btc|eth|usd|\$)'
        for match in re.finditer(quantity_pattern, text):
            quantity = match.group(1)
            price = match.group(2)
            currency = match.group(3)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='marketplace',
                confidence=0.75,
                risk_level='medium',
                data={
                    'type': 'quantity_pricing',
                    'quantity': int(quantity),
                    'price': float(price),
                    'currency': currency.upper()
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_shipping_info(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract shipping and delivery information"""
        results = []
        
        # Shipping locations
        shipping_patterns = [
            r'(?i)(?:ships?|shipping|delivery)\s+(?:from|to)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?i)(?:worldwide|international|domestic)\s+shipping',
            r'(?i)ships?\s+to[:\s]+([A-Z]{2,3}(?:\s*,\s*[A-Z]{2,3})*)'
        ]
        
        for pattern in shipping_patterns:
            for match in re.finditer(pattern, text):
                location = match.group(1) if match.lastindex else match.group(0)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.7,
                    risk_level='medium',
                    data={
                        'type': 'shipping_location',
                        'location': location
                    },
                    context=context,
                    location=url
                ))
        
        # Delivery time
        delivery_pattern = r'(?i)(?:delivery|shipping)\s+(?:time|period)[:\s]+(\d+[-\s]?\d*)\s*(days?|weeks?|hours?)'
        for match in re.finditer(delivery_pattern, text):
            time_value = match.group(1)
            time_unit = match.group(2)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='marketplace',
                confidence=0.75,
                risk_level='low',
                data={
                    'type': 'delivery_time',
                    'time_value': time_value,
                    'time_unit': time_unit
                },
                context=context,
                location=url
            ))
        
        # Stealth/discreet shipping mentions
        stealth_pattern = r'(?i)\b(stealth|discreet|hidden|vacuum[- ]sealed)\s+(?:shipping|packaging|delivery)\b'
        for match in re.finditer(stealth_pattern, text):
            method = match.group(1)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='marketplace',
                confidence=0.85,
                risk_level='high',
                data={
                    'type': 'shipping_method',
                    'method': method.lower(),
                    'stealth': True
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_escrow_info(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract escrow and payment protection information"""
        results = []
        
        escrow_patterns = [
            r'(?i)\b(escrow|multisig|2-of-3|multi-signature)\b',
            r'(?i)(?:buyer|purchase)\s+protection',
            r'(?i)(?:dispute|refund)\s+(?:process|policy|available)'
        ]
        
        for pattern in escrow_patterns:
            for match in re.finditer(pattern, text):
                escrow_type = match.group(1) if match.lastindex else 'protection'
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='marketplace',
                    confidence=0.7,
                    risk_level='low',
                    data={
                        'type': 'escrow_method',
                        'method': escrow_type.lower()
                    },
                    context=context,
                    location=url
                ))
        
        # FE (Finalize Early) mentions - often a red flag
        fe_pattern = r'(?i)\b(FE|finalize\s+early)\b'
        for match in re.finditer(fe_pattern, text):
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='marketplace',
                confidence=0.9,
                risk_level='high',
                data={
                    'type': 'payment_risk',
                    'risk_indicator': 'finalize_early',
                    'warning': 'FE increases risk of fraud'
                },
                context=context,
                location=url
            ))
        
        return results

