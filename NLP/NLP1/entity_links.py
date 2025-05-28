# entity_links.py

# --- Categorized dictionaries ---

facebook_entities = {
    "NET25": "https://www.facebook.com/NET25TV",
    "GMA News": "https://www.facebook.com/gmanews"
}

twitter_entities = {
    "NASA": "https://twitter.com/NASA"
}

youtube_entities = {
    "YouTube": "https://www.youtube.com"
}

generic_entities = {
    "Google": "https://www.google.com"
}

# --- Unified dictionary with types ---
entity_to_url = {}

for name, url in facebook_entities.items():
    entity_to_url[name] = ("Facebook Page", url)

for name, url in twitter_entities.items():
    entity_to_url[name] = ("Twitter Page", url)

for name, url in youtube_entities.items():
    entity_to_url[name] = ("YouTube Channel", url)

for name, url in generic_entities.items():
    entity_to_url[name] = ("Generic Resource", url)
