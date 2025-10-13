"""
Communication Methods Extractor
"""

import re
from typing import List
from .base import BaseExtractor, ExtractionResult, RegexPatterns


class CommunicationExtractor(BaseExtractor):
    """Extract communication methods and contact information"""
    
    def extract(self, text: str, url: str = "") -> List[ExtractionResult]:
        """Extract various communication methods"""
        results = []
        
        # Extract PGP keys
        results.extend(self._extract_pgp_keys(text, url))
        
        # Extract messaging app IDs
        results.extend(self._extract_messaging_ids(text, url))
        
        # Extract email addresses (for communication)
        results.extend(self._extract_contact_emails(text, url))
        
        # Extract IRC channels
        results.extend(self._extract_irc_channels(text, url))
        
        self.results.extend(results)
        return results
    
    def _extract_pgp_keys(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract PGP public keys and fingerprints"""
        results = []
        
        # PGP key blocks
        pgp_block_pattern = r'-----BEGIN PGP (?:PUBLIC|PRIVATE) KEY BLOCK-----(.*?)-----END PGP (?:PUBLIC|PRIVATE) KEY BLOCK-----'
        for match in re.finditer(pgp_block_pattern, text, re.DOTALL):
            key_content = match.group(1).strip()
            context = self.get_context(text, match.start(), match.end(), 100)
            
            key_type = 'PUBLIC' if 'PUBLIC KEY' in match.group(0) else 'PRIVATE'
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.95,
                risk_level='high' if key_type == 'PRIVATE' else 'medium',
                data={
                    'type': 'pgp_key_block',
                    'key_type': key_type,
                    'key_preview': key_content[:100] + '...' if len(key_content) > 100 else key_content
                },
                context=context,
                location=url
            ))
        
        # PGP fingerprints
        for match in re.finditer(RegexPatterns.PGP_FINGERPRINT, text):
            fingerprint = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Check if context suggests this is a PGP fingerprint
            pgp_keywords = ['pgp', 'fingerprint', 'key', 'gpg', 'encryption']
            if any(keyword in context.lower() for keyword in pgp_keywords):
                results.append(ExtractionResult(
                    category='communication',
                    confidence=0.85,
                    risk_level='medium',
                    data={
                        'type': 'pgp_fingerprint',
                        'fingerprint': fingerprint
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_messaging_ids(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract messaging app identifiers"""
        results = []
        
        # Telegram
        for match in re.finditer(RegexPatterns.TELEGRAM, text):
            telegram_id = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Clean up the ID
            clean_id = telegram_id.replace('@', '').replace('t.me/', '')
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.9,
                risk_level='medium',
                data={
                    'type': 'telegram',
                    'username': clean_id,
                    'full_handle': telegram_id
                },
                context=context,
                location=url
            ))
        
        # Wickr
        for match in re.finditer(RegexPatterns.WICKR, text):
            wickr_id = match.group(1) if match.lastindex else match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.85,
                risk_level='medium',
                data={
                    'type': 'wickr',
                    'username': wickr_id
                },
                context=context,
                location=url
            ))
        
        # Signal
        signal_pattern = r'(?i)signal[:\s]+([+\d\s()-]{10,20})'
        for match in re.finditer(signal_pattern, text):
            signal_number = match.group(1).strip()
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.8,
                risk_level='medium',
                data={
                    'type': 'signal',
                    'phone_number': signal_number
                },
                context=context,
                location=url
            ))
        
        # Session
        session_pattern = r'(?i)session\s+id[:\s]+([a-f0-9]{64,66})'
        for match in re.finditer(session_pattern, text):
            session_id = match.group(1)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.85,
                risk_level='medium',
                data={
                    'type': 'session',
                    'session_id': session_id
                },
                context=context,
                location=url
            ))
        
        # Jabber/XMPP
        jabber_pattern = r'\b([a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)*xmpp\.[a-zA-Z]{2,}|[a-zA-Z0-9._%+-]+@jabber\.[a-zA-Z0-9.-]+)\b'
        for match in re.finditer(jabber_pattern, text):
            jabber_id = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.85,
                risk_level='medium',
                data={
                    'type': 'jabber',
                    'jabber_id': jabber_id
                },
                context=context,
                location=url
            ))
        
        # Discord
        discord_pattern = r'(?i)discord[:\s]+([a-zA-Z0-9_]{2,32}#\d{4})'
        for match in re.finditer(discord_pattern, text):
            discord_id = match.group(1)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.9,
                risk_level='low',
                data={
                    'type': 'discord',
                    'username': discord_id
                },
                context=context,
                location=url
            ))
        
        # Matrix
        matrix_pattern = r'@[a-zA-Z0-9._=-]+:[a-zA-Z0-9.-]+'
        for match in re.finditer(matrix_pattern, text):
            matrix_id = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Check if context suggests Matrix
            if 'matrix' in context.lower():
                results.append(ExtractionResult(
                    category='communication',
                    confidence=0.8,
                    risk_level='medium',
                    data={
                        'type': 'matrix',
                        'user_id': matrix_id
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_contact_emails(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract email addresses used for contact"""
        results = []
        
        contact_patterns = [
            r'(?i)contact[:\s]+(' + RegexPatterns.EMAIL + r')',
            r'(?i)email[:\s]+(' + RegexPatterns.EMAIL + r')',
            r'(?i)reach\s+(?:me|us)\s+at[:\s]+(' + RegexPatterns.EMAIL + r')'
        ]
        
        for pattern in contact_patterns:
            for match in re.finditer(pattern, text):
                email = match.group(1)
                context = self.get_context(text, match.start(), match.end())
                
                results.append(ExtractionResult(
                    category='communication',
                    confidence=0.9,
                    risk_level='medium',
                    data={
                        'type': 'contact_email',
                        'email': email,
                        'purpose': 'contact'
                    },
                    context=context,
                    location=url
                ))
        
        return results
    
    def _extract_irc_channels(self, text: str, url: str) -> List[ExtractionResult]:
        """Extract IRC channels and servers"""
        results = []
        
        # IRC channel format
        irc_channel_pattern = r'#[a-zA-Z0-9_-]{2,50}'
        for match in re.finditer(irc_channel_pattern, text):
            channel = match.group(0)
            context = self.get_context(text, match.start(), match.end())
            
            # Check if context suggests IRC
            irc_keywords = ['irc', 'channel', 'chat', 'server']
            if any(keyword in context.lower() for keyword in irc_keywords):
                results.append(ExtractionResult(
                    category='communication',
                    confidence=0.75,
                    risk_level='low',
                    data={
                        'type': 'irc_channel',
                        'channel': channel
                    },
                    context=context,
                    location=url
                ))
        
        # IRC server format
        irc_server_pattern = r'(?i)irc[:\s]+([a-zA-Z0-9.-]+(?::\d+)?)'
        for match in re.finditer(irc_server_pattern, text):
            server = match.group(1)
            context = self.get_context(text, match.start(), match.end())
            
            results.append(ExtractionResult(
                category='communication',
                confidence=0.8,
                risk_level='low',
                data={
                    'type': 'irc_server',
                    'server': server
                },
                context=context,
                location=url
            ))
        
        return results

