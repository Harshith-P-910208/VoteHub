"""
IndexNow Submission Script for College VoteHub
This script submits your URLs to IndexNow API for instant indexing by Bing and other search engines.
"""

import requests
import json

# Your website URLs to submit
urls = [
    "https://votehub-3cn2.onrender.com/",
    "https://votehub-3cn2.onrender.com/accounts/login/",
    "https://votehub-3cn2.onrender.com/accounts/register/",
    "https://votehub-3cn2.onrender.com/admin/login/",
]

# IndexNow API endpoint
indexnow_url = "https://api.indexnow.org/indexnow"

# Submit each URL
for url in urls:
    payload = {
        "host": "votehub-3cn2.onrender.com",
        "key": "your-key-here",  # You can generate a key or use any random string
        "keyLocation": "https://votehub-3cn2.onrender.com/indexnow-key.txt",
        "urlList": [url]
    }
    
    try:
        response = requests.post(indexnow_url, json=payload)
        if response.status_code == 200:
            print(f"✅ Successfully submitted: {url}")
        else:
            print(f"⚠️ Status {response.status_code} for: {url}")
    except Exception as e:
        print(f"❌ Error submitting {url}: {e}")

print("\n🎉 IndexNow submission complete!")
print("Note: This submits to Bing and other IndexNow partners, not Google.")
print("For Google, you still need to use Google Search Console.")
