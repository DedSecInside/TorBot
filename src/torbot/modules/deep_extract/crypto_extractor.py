"""
Cryptocurrency Address Extractor and Tracker
"""

import re
from typing import List
from .base import BaseExtractor, ExtractionResult, RegexPatterns


class CryptoExtractor(BaseExtractor):
    """Extract cryptocurrency addresses and related information"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract various cryptocurrency addresses"""
        results = []
        
        # Extract Bitcoin addresses
        results.extend(self._extract_bitcoin(text, url))
        
        # Extract Ethereum addresses
        results.extend(self._extract_ethereum(text, url))
        
        # Extract Monero addresses
        results.extend(self._extract_monero(text, url))
        
        # Extract Litecoin addresses
        results.extend(self._extract_litecoin(text, url))
        
        # Extract other cryptocurrency mentions
        results.extend(self._extract_crypto_keywords(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_bitcoin(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract Bitcoin addresses"""
        results = []
        
        for match in re.finditer(RegexPatterns.BITCOIN, text):
            address = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Validate Bitcoin address format more strictly
            if self._validate_bitcoin_address(address):
                results.append(ExtractionResult(
                    category='cryptocurrency',
                    confidence=0.9,
                    risk_level='high',
                    data={
                        'type': 'bitcoin',
                        'address': address,
                        'currency': 'BTC',
                        'address_type': self._get_bitcoin_type(address)
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address format"""
        # Basic validation - starts with 1, 3, or bc1
        if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
            return False
        
        # Length check
        if address.startswith('bc1'):  # Bech32
            return 42 <= len(address) <= 62
        else:  # Base58
            return 26 <= len(address) <= 35
        
        return True
    
    def _get_bitcoin_type(self, address: str) -> str:
        """Determine Bitcoin address type"""
        if address.startswith('1'):
            return 'P2PKH (Legacy)'
        elif address.startswith('3'):
            return 'P2SH (SegWit)'
        elif address.startswith('bc1'):
            return 'Bech32 (Native SegWit)'
        return 'Unknown'
    
    def _extract_ethereum(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract Ethereum addresses"""
        results = []
        
        for match in re.finditer(RegexPatterns.ETHEREUM, text):
            address = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='cryptocurrency',
                confidence=0.9,
                risk_level='high',
                data={
                    'type': 'ethereum',
                    'address': address,
                    'currency': 'ETH',
                    'checksum_validated': False  # Could add EIP-55 validation
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_monero(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract Monero addresses"""
        results = []
        
        for match in re.finditer(RegexPatterns.MONERO, text):
            address = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='cryptocurrency',
                confidence=0.85,
                risk_level='high',
                data={
                    'type': 'monero',
                    'address': address,
                    'currency': 'XMR',
                    'privacy_coin': True
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_litecoin(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract Litecoin addresses"""
        results = []
        
        for match in re.finditer(RegexPatterns.LITECOIN, text):
            address = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='cryptocurrency',
                confidence=0.8,
                risk_level='high',
                data={
                    'type': 'litecoin',
                    'address': address,
                    'currency': 'LTC'
                },
                context=context,
                location=url
            ))
        
        return results
    
    def _extract_crypto_keywords(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract cryptocurrency-related keywords and contexts"""
        results = []
        
        # Payment request patterns
        payment_patterns = [
            (r'(?i)send\s+(\d+(?:\.\d+)?)\s*(btc|bitcoin|eth|ethereum|xmr|monero)', 0.7),
            (r'(?i)price[:\s]+(\d+(?:\.\d+)?)\s*(btc|bitcoin|eth|ethereum|xmr|monero)', 0.75),
            (r'(?i)payment[:\s]+(\d+(?:\.\d+)?)\s*(btc|bitcoin|eth|ethereum|xmr|monero)', 0.8),
        ]
        
        for pattern, confidence in payment_patterns:
            for match in re.finditer(pattern, text):
                amount = match.group(1)
                currency = match.group(2)
                context = self.get_context(text, match.start(), match.end(), 150)
                
                results.append(ExtractionResult(
                    category='cryptocurrency',
                    confidence=confidence,
                    risk_level='medium',
                    data={
                        'type': 'payment_request',
                        'amount': amount,
                        'currency': currency.upper(),
                    },
                    context=context,
                    location=url
                ))
        
        # Wallet mentions
        wallet_pattern = r'(?i)wallet[:\s]+([a-zA-Z0-9]{20,})'
        for match in re.finditer(wallet_pattern, text):
            wallet_id = match.group(1)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='cryptocurrency',
                confidence=0.6,
                risk_level='medium',
                data={
                    'type': 'wallet_mention',
                    'wallet_id': wallet_id
                },
                context=context,
                location=url
            ))
        
        # Exchange mentions
        exchanges = [
            'binance', 'coinbase', 'kraken', 'bitstamp', 'bitfinex', 
            'huobi', 'okex', 'kucoin', 'gemini', 'bittrex'
        ]
        
        for exchange in exchanges:
            pattern = r'\b' + exchange + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='cryptocurrency',
                    confidence=0.5,
                    risk_level='low',
                    data={
                        'type': 'exchange_mention',
                        'exchange': exchange.title()
                    },
                    context=context,
                    location=url
                ))
        
        return results

