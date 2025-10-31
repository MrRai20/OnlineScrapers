import requests
from bs4 import BeautifulSoup
import time
import os

# ============================
# CONFIGURATION
# ============================

# Create a folder for saved chapters
output_folder = "PocketHunting_Wiki"
os.makedirs(output_folder, exist_ok=True)

# Base URL options (FreeWebNovel uses inconsistent structures)
base_urls = [
    "",
    "https://pocket-hunting-dimension.fandom.com/wiki/Lu_Ze/Techniques",
    ""
]

# CSS selectors that match chapter text blocks
content_selectors = [
    "div#chapter-content",
    "div.chapter-content",
    "div#content",
    "div.text-left",
    "div.txt"
]

# Common junk phrases to remove
junk_phrases = [
    "Prev Chapter", "Next Chapter", "Add to Library", "Comments",
    "Freewebnovel.Com", "Privacy Policy", "Read Books Online",
    "Your Library", "Latest Novels", "Genres", "Login", "Signup",
    "Read more chapters at FreeWebNovel.Com"
]

# ============================
# SCRAPER LOGIC
# ============================

def clean_text(raw_text):
    """Removes junk phrases and trims empty lines."""
    for phrase in junk_phrases:
        raw_text = raw_text.replace(phrase, "")
    # Remove excessive line breaks
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return "\n".join(lines)

def fetch_chapter(chapter_number):
    """Tries all URL patterns and selector patterns until it finds valid content."""
    for base in base_urls:
        url = base.format(chapter_number)
        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException:
            continue

        if response.status_code == 200 and "Page Not Found" not in response.text:
            soup = BeautifulSoup(response.text, "html.parser")

            # Try all known selectors
            for sel in content_selectors:
                content_div = soup.select_one(sel)
                if content_div and len(content_div.get_text()) > 400:
                    text = clean_text(content_div.get_text(separator="\n", strip=True))
                    return text, url

            # Fallback: pick the largest div by text length
            divs = soup.find_all("div")
            if divs:
                content_div = max(divs, key=lambda d: len(d.get_text()))
                if len(content_div.get_text()) > 400:
                    text = clean_text(content_div.get_text(separator="\n", strip=True))
                    return text, url
    return None, None

# ============================
# MAIN LOOP
# ============================

start_chapter = 3
end_chapter = 3  # adjust to scrape more later

for i in range(start_chapter, end_chapter + 1):
    print(f"⏳ Fetching Chapter {i}...")

    text, found_url = fetch_chapter(i)
    if text:
        with open(os.path.join(output_folder, f"chapter_{i}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Chapter {i} saved from {found_url}")
    else:
        print(f"⚠️ Chapter {i} not found on any known pattern.")

    time.sleep(2)  # delay to avoid pinging server too fast

print("\n🎉 DONE! All chapters saved in:", os.path.abspath(output_folder))
