"""
Google Sitemap Ping Script for College VoteHub
This script notifies Google about your sitemap.
"""

import requests
import urllib.parse

# Your sitemap URL
sitemap_url = "https://votehub-3cn2.onrender.com/sitemap.xml"

# Google ping URL
google_ping = f"https://www.google.com/ping?sitemap={urllib.parse.quote(sitemap_url)}"

print("🔔 Pinging Google about your sitemap...")
print(f"Sitemap: {sitemap_url}")

try:
    response = requests.get(google_ping)
    if response.status_code == 200:
        print("✅ Successfully pinged Google!")
        print("Google has been notified about your sitemap.")
        print("Indexing may take 1-7 days.")
    else:
        print(f"⚠️ Response status: {response.status_code}")
        print("You may need to submit manually via Google Search Console.")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nAlternative: Visit this URL in your browser:")
    print(google_ping)

print("\n📝 Next Steps:")
print("1. Wait 1-3 days for Google to crawl your site")
print("2. Check indexing status: search 'site:votehub-3cn2.onrender.com' in Google")
print("3. For faster indexing, use Google Search Console")
