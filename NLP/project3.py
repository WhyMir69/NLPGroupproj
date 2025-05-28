import re
from urllib.parse import urlparse, urlunparse
from typing import List, Dict, Set, Union

class BantAILinkExtractor:
    """Enhanced URL extractor with social media profile detection"""
    
    def __init__(self):
        # URL pattern
        self.url_regex = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Social media mentions and handles
        self.social_regex = re.compile(
            r'(?:^|\s)(@[A-Za-z0-9_]+|#[A-Za-z0-9_]+|[A-Z]{2,}\d+\b)',
            re.IGNORECASE
        )
        
        # Known social media domains and their URL structures
        self.social_platforms = {
            'facebook': {
                'domain': 'facebook.com',
                'url_template': 'https://www.facebook.com/{handle}'
            },
            'twitter': {
                'domain': 'twitter.com',
                'url_template': 'https://twitter.com/{handle}'
            },
            'instagram': {
                'domain': 'instagram.com',
                'url_template': 'https://instagram.com/{handle}'
            }
        }

    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _extract_facebook_id(self, url: str) -> str:
        """Extracts handle from messy Facebook URLs"""
        if 'facebook.com' not in url:
            return None
            
        # Clean URL
        clean_url = url.split('?')[0].split('&')[0]
        if clean_url.endswith('/'):
            clean_url = clean_url[:-1]
            
        # Extract handle (NET25TV in https://www.facebook.com/NET25TV)
        return clean_url.split('/')[-1]

    def _expand_social_mention(self, mention: str) -> str:
        """Convert mentions to full URLs"""
        mention = mention.strip()
        
        # Handle Facebook page names (NET25)
        if mention.isupper() and len(mention) >= 2:
            return self.social_platforms['facebook']['url_template'].format(handle=mention)
            
        # Handle @mentions and #hashtags
        elif mention.startswith('@'):
            platform = 'twitter'  # Default platform
            return self.social_platforms[platform]['url_template'].format(handle=mention[1:])
            
        return None

    def extract_links(self, text: str) -> List[str]:
        """Main extraction method with social media support"""
        if not text:
            return []

        # Extract standard URLs
        urls = []
        for url in re.findall(self.url_regex, text):
            if 'facebook.com' in url:
                # Clean Facebook URLs
                if fb_id := self._extract_facebook_id(url):
                    urls.append(
                        self.social_platforms['facebook']['url_template'].format(handle=fb_id)
                    )
            elif self._is_valid_url(url):
                urls.append(url)

        # Extract and expand social mentions
        for match in self.social_regex.finditer(text):
            mention = match.group(1)
            if expanded := self._expand_social_mention(mention):
                urls.append(expanded)

        return list(set(urls))  # Remove duplicates


def process_text_input(text: str, verified_pages: Set[str]) -> Dict:
    """Processor for text with Facebook page detection"""
    extractor = BantAILinkExtractor()
    found_links = extractor.extract_links(text)
    
    verification = {
        link: any(
            urlparse(link).path.lstrip('/').casefold() == page.casefold()
            for page in verified_pages
        )
        for link in found_links
    }
    
    return {
        'original_text': text,
        'extracted_links': found_links,
        'verification': verification,
        'all_verified': all(verification.values())
    }


# Example Usage
if __name__ == "__main__":
    # Verified Facebook pages (would normally come from your database)
    VERIFIED_PAGES = {
        'NET25TV',  # Matches https://facebook.com/NET25TV
        'OfficialGMA'
    }
    
    print("=== Test with Facebook Link ===")
    test_post = """Surreal moment! Thank you NET25 for featuring me
    Replay here: https://www.facebook.com/NET25TV?__cft__[0]=AZUQHWo..."""
    
    result = process_text_input(test_post, VERIFIED_PAGES)
    print(f"Input: {test_post[:50]}...")
    print("Output:", result)