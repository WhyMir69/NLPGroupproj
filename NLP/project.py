import re
import requests
from urllib.parse import urlparse

# List of trusted domains
TRUSTED_DOMAINS = ['youtube.com', 'youtu.be', 'facebook.com', 'net25.tv']

def extract_links(text):
    url_pattern = r'(https?://[^\s]+)'
    return re.findall(url_pattern, text)

def is_trusted_domain(url):
    domain = urlparse(url).netloc
    return any(trusted in domain for trusted in TRUSTED_DOMAINS)

def is_link_active(url):
    try:
        # Try HEAD request first
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code in [200, 301, 302]:
            return True
        # Fallback to GET if HEAD fails
        response = requests.get(url, allow_redirects=True, timeout=5)
        return response.status_code in [200, 301, 302]
    except requests.RequestException:
        return False

# === Input from user ===
print("Paste your post (press Enter twice to finish):")
lines = []
while True:
    line = input()
    if line.strip() == "":
        break
    lines.append(line)

post = "\n".join(lines)

# === Process ===
extracted_links = extract_links(post)

# Show all extracted links
print("\n📋 All Extracted Links:")
for link in extracted_links:
    print(f"- {link}")

print("\n🔍 Link Verification Results:\n")

for link in extracted_links:
    print(f"🔗 Found link: {link}")
    
    if is_trusted_domain(link):
        print("✅ Trusted domain.")
    else:
        print("❌ Untrusted or suspicious domain.")
    
    if is_link_active(link):
        print("✅ Link is active.\n")
    else:
        print("❌ Link is broken or unreachable.\n")
