# link_extractor.py

import re
from entity_links import entity_to_url

# 1. Extract explicit URLs using regex
def extract_explicit_urls(text):
    return re.findall(r'https?://\S+', text)

# 2. Match known entities (case-insensitive)
def extract_named_entities(text, known_entities):
    found_entities = []
    for name in known_entities:
        if name.lower() in text.lower():
            found_entities.append(name)
    return found_entities

# 3. Classify explicit URLs
def classify_links(urls):
    result = []
    for url in urls:
        if "youtu" in url:
            result.append({"url": url, "type": "YouTube Video"})
        elif "facebook.com" in url:
            result.append({"url": url, "type": "Facebook Page"})
        elif "twitter.com" in url:
            result.append({"url": url, "type": "Twitter Page"})
        else:
            result.append({"url": url, "type": "Generic URL"})
    return result

# 4. Combine both explicit and inferred links
def extract_links_and_entities(text):
    explicit_urls = extract_explicit_urls(text)
    found_entities = extract_named_entities(text, entity_to_url.keys())

    output = []

    # Add inferred links
    for entity in found_entities:
        kind, url = entity_to_url[entity]
        output.append({
            "entity": entity,
            "type": kind,
            "url": url
        })

    # Add direct (explicit) links
    output.extend(classify_links(explicit_urls))

    return output

# --- Run the extractor ---
if __name__ == "__main__":
    user_input = input("Enter your message: ")
    results = extract_links_and_entities(user_input)

    print("\nExtracted Links and Entities:")
    for item in results:
        print(item)
