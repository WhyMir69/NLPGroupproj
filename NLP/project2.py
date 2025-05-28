import re
from urllib.parse import urlparse
from typing import List, Dict, Set, Union

class BantAILinkExtractor:
    """Core URL extraction engine for BantAI project"""
    
    def __init__(self):
        self.url_regex = re.compile(
            r'(?:(?:https?|ftp)://)'
            r'(?:\S+(?::\S*)?@)?'
            r'(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)'
            r'(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*'
            r'(?:\.(?:[a-z\u00a1-\uffff]{2,}))'
            r'(?::\d{2,5})?'
            r'(?:/[\S]*)?'
            r'(?:\?\S*)?'
            r'(?:#\S*)?',
            re.IGNORECASE
        )
        self.url_keywords = {'http', 'https', 'www', 'visit', 'watch', 'link', 'click'}
        self.common_tlds = {'.com', '.org', '.net', '.io', '.co', '.ai', '.ly'}

    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def _fix_ocr_errors(self, url: str) -> str:
        """Corrects common OCR misreads"""
        corrections = {
            ' ': '',    # Remove spaces
            '\\': '/',  # Fix backslashes
            '1': 'l',   # Common character misreads
            '0': 'o',
            '|': 'l',
            ' ': ''
        }
        for wrong, right in corrections.items():
            url = url.replace(wrong, right)
        return url

    def extract_urls(self, text: str, is_ocr_output: bool = False) -> List[str]:
        """Main extraction method"""
        if not text:
            return []

        # Extract standard URLs
        found_urls = list(set(re.findall(self.url_regex, text)))
        
        # Extract implied URLs (without http://)
        words = re.split(r'\s+|[,;!?]\s*', text)
        for i, word in enumerate(words):
            if any(tld in word for tld in self.common_tlds):
                if i > 0 and words[i-1].lower() in self.url_keywords:
                    found_urls.append(word)

        # Process and validate
        valid_urls = []
        for url in found_urls:
            url = self._normalize_url(url)
            if is_ocr_output:
                url = self._fix_ocr_errors(url)
            if self._is_valid_url(url):
                valid_urls.append(url)

        return valid_urls


def process_text_input(text: str, verified_domains: Set[str]) -> Dict[str, Union[str, List, Dict]]:
    """Use Case 1: Direct text input processing"""
    extractor = BantAILinkExtractor()
    urls = extractor.extract_urls(text)
    
    verification = {url: any(urlparse(url).netloc.endswith(d) for d in verified_domains)
                   for url in urls}
    
    return {
        'original_text': text,
        'extracted_urls': urls,
        'verification': verification,
        'all_verified': all(verification.values())
    }


def process_ocr_output(ocr_text: str, verified_domains: Set[str]) -> Dict[str, Union[str, List, Dict]]:
    """Use Case 3: OCR-extracted text processing"""
    extractor = BantAILinkExtractor()
    urls = extractor.extract_urls(ocr_text, is_ocr_output=True)
    
    verification = {url: any(urlparse(url).netloc.endswith(d) for d in verified_domains)
                   for url in urls}
    
    return {
        'original_text': ocr_text,
        'corrected_urls': urls,
        'verification': verification,
        'needs_review': not all(verification.values())
    }


# Example Usage
if __name__ == "__main__":
    # Sample verified domains (would normally come from your database)
    VERIFIED_DOMAINS = {'youtu.be', 'example.com', 'trustedsite.org'}
    
    print("=== Text Input Test ===")
    text_input = """Check this out: https://youtu.be/b4zGxEg4O9g
    Also visit example.com"""
    print(process_text_input(text_input, VERIFIED_DOMAINS))
    
    print("\n=== OCR Input Test ===")
    ocr_input = """Visit our channe1:
    https://youtu.be/b4zGxEg4O9g
    (Note OCR errors)"""
    print(process_ocr_output(ocr_input, VERIFIED_DOMAINS))