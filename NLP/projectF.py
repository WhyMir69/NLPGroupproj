import json
import os
import re
from urllib.parse import urlparse
from typing import List, Dict

class LinkVerifier:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load or create config file with empty structure"""
        default_config = {
            "facebook_pages": {},
            "verified_domains": [],
            "verified_urls": []
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def is_verified(self, url: str) -> bool:
        """Check if URL is verified"""
        parsed = urlparse(url.lower())
        
        if any(url.lower() == verified.lower() 
               for verified in self.config["verified_urls"]):
            return True
            
        domain = parsed.netloc
        if any(domain.endswith(verified_domain) 
               for verified_domain in self.config["verified_domains"]):
            return True
            
        if 'facebook.com' in domain:
            handle = parsed.path.strip('/')
            return any(handle.lower() == page.lower() 
                      for page in self.config["facebook_pages"].values())
        return False
    
    def extract_links(self, text: str) -> List[str]:
        """Extract all links including Facebook mentions"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F]{2}))+'
        )
        
        # Match capitalized and acronym-like words, including dashes (ABS-CBN, NET25)
        fb_mention_pattern = re.compile(r'\b([A-Z][A-Z0-9\-]{1,})\b')

        links = set()

        # Extract standard URLs
        for url in re.findall(url_pattern, text):
            if self._is_valid_url(url):
                links.add(url)

        # Extract likely Facebook mentions and convert to URLs
        normalized_fb_map = {
            re.sub(r'[^a-z0-9]', '', key.lower()): handle
            for key, handle in self.config["facebook_pages"].items()
        }

        for match in fb_mention_pattern.finditer(text):
            mention = match.group(1)
            norm_mention = re.sub(r'[^a-z0-9]', '', mention.lower())  # remove dashes, case-insensitive
            if norm_mention in normalized_fb_map:
                handle = normalized_fb_map[norm_mention]
                links.add(f"https://www.facebook.com/{handle}")

        return list(links)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

def get_user_input() -> str:
    """Get multi-line input with double-enter termination"""
    print("\nPaste your text (press Enter twice to submit):")
    lines = []
    empty_lines = 0
    
    while empty_lines < 2:
        line = input()
        if line.strip() == "":
            empty_lines += 1
        else:
            empty_lines = 0
        lines.append(line)
    
    return '\n'.join(lines).strip()

def main():
    verifier = LinkVerifier()
    
    print("=== Link Verifier ===")
    print(f"Loaded {len(verifier.config['verified_domains'])} domains and "
          f"{len(verifier.config['facebook_pages'])} Facebook pages")
    
    while True:
        text = get_user_input()
        if not text:
            print("No input provided. Exiting...")
            break
        
        links = verifier.extract_links(text)
        
        if not links:
            print("\nNo links found.")
        else:
            print("\nVerification Results:")
            for link in links:
                status = "✓ VERIFIED" if verifier.is_verified(link) else "✗ UNVERIFIED"
                print(f"{status}: {link}")
            
            all_verified = all(verifier.is_verified(link) for link in links)
            print(f"\nSUMMARY: {'ALL VERIFIED' if all_verified else 'CONTAINS UNVERIFIED LINKS'}")
        
        if input("\nCheck another? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
