import re
from urllib.parse import urlparse, urlunparse
from typing import List, Optional

class LinkExtractor:
    """
    Robust URL extractor for social media text with NLP-inspired heuristics
    """
    
    def __init__(self):
        # Pre-compile regex patterns for efficiency
        self.url_regex = re.compile(
            r'(?:(?:https?|ftp)://)'  # Protocol
            r'(?:\S+(?::\S*)?@)?'     # User:pass auth
            r'(?:'                    # Domain part
            r'(?!(?:10|127)(?:\.\d{1,3}){3})'
            r'(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})'
            r'(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})'
            r'(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])'
            r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}'
            r'(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))'
            r'|'
            r'(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)'
            r'(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*'
            r'(?:\.(?:[a-z\u00a1-\uffff]{2,}))'
            r')'
            r'(?::\d{2,5})?'          # Port
            r'(?:/[\S]*)?'            # Path
            r'(?:\?\S*)?'             # Query
            r'(?:#\S*)?',             # Fragment
            re.IGNORECASE
        )
        
        self.url_keywords = {
            'http', 'https', 'www', 'visit', 'watch', 
            'link', 'click', 'here', 'goo.gl', 'bit.ly'
        }
        
        self.tlds = {
            '.com', '.org', '.net', '.gov', '.edu',
            '.io', '.co', '.ai', '.ly', '.me'
        }

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL structure"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _normalize_url(self, url: str) -> str:
        """Ensure URLs have proper scheme"""
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def _extract_explicit_urls(self, text: str) -> List[str]:
        """Extract URLs with explicit http(s)://"""
        return [
            url for url in re.findall(self.url_regex, text)
            if self._is_valid_url(url)
        ]

    def _extract_implied_urls(self, text: str) -> List[str]:
        """Find URLs without explicit scheme using NLP heuristics"""
        implied_urls = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Case 1: www.example.com
            if word.startswith('www.') and any(word.endswith(tld) for tld in self.tlds):
                implied_urls.append(self._normalize_url(word))
            
            # Case 2: example.com with trigger words
            elif any(tld in word for tld in self.tlds):
                prev_word = words[i-1].lower() if i > 0 else ""
                if prev_word in self.url_keywords:
                    implied_urls.append(self._normalize_url(word))
        
        return implied_urls

    def extract_urls(self, text: str) -> List[str]:
        """
        Extract all valid URLs from text with NLP heuristics
        
        Args:
            text: Input text (social media post, comment, etc.)
            
        Returns:
            List of found URLs (empty if none found)
        """
        if not text or not isinstance(text, str):
            return []
            
        # Combine both extraction methods
        explicit_urls = self._extract_explicit_urls(text)
        implied_urls = self._extract_implied_urls(text)
        
        # Remove duplicates while preserving order
        seen = set()
        return [
            url for url in explicit_urls + implied_urls
            if not (url in seen or seen.add(url))
        ]


# ======================
# Example Usage
# ======================
if __name__ == "__main__":
    extractor = LinkExtractor()
    
    test_cases = [
        # Your original example
        """Surreal moment! Thank you NET25 for featuring me
        Replay here
        https://youtu.be/b4zGxEg4O9g""",
        
        # Implied URL case
        "Watch my new video on youtube.com/b4zGxEg4O9g",
        
        # Multiple URLs
        "Links: https://example.com and www.test.org",
        
        # No URLs
        "This text contains no links",
        
        # Edge case from OCR
        "Visit our site: examp1e.com (OCR error)",  # Won't match due to typo
    ]
    
    for text in test_cases:
        print(f"\nInput text:\n{text}")
        urls = extractor.extract_urls(text)
        print(f"Extracted URLs: {urls}")