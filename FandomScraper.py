import os
import requests
from bs4 import BeautifulSoup
import time

# === CONFIG ===
base_url = "https://arifureta.fandom.com"
start_page = "/wiki/Special:AllPages"
output_dir = "Arifureta_Wiki"
delay = 2  # seconds between requests
max_retries = 3  # number of retries for failed requests

os.makedirs(output_dir, exist_ok=True)

# === HELPERS ===
def clean_filename(name):
    """Sanitize a string to use as a safe filename."""
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip()

def get_with_retries(url):
    """Request a URL with retry logic."""
    for attempt in range(max_retries):
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            print(f"Request failed ({attempt + 1}/{max_retries}) for {url}: {e}")
            time.sleep(5)
    return None

def get_all_article_links(allpages_url):
    """Collect every article URL from the 'AllPages' listing."""
    urls = set()
    next_page = allpages_url

    while next_page:
        print(f"Fetching index: {next_page}")
        r = requests.get(next_page)
        soup = BeautifulSoup(r.text, "html.parser")

        # The AllPages list now uses div.mw-allpages-body and ul > li > a
        all_links = soup.select("div.mw-allpages-body ul li a")

        if not all_links:
            # Fallback for variant layouts
            all_links = soup.select("a[href^='/wiki/']")

        for a in all_links:
            href = a.get("href")
            if href and href.startswith("/wiki/") and not any(x in href for x in ["Special:", "Category:"]):
                urls.add(base_url + href)

        # Try to find pagination link (new layout)
        next_tag = soup.find("a", string="Next page")
        if not next_tag:
            next_tag = soup.find("a", class_="mw-allpages-nav-next")

        next_page = base_url + next_tag["href"] if next_tag else None

        print(f"Collected {len(urls)} pages so far...")
        time.sleep(delay)

    return list(urls)


def scrape_article(url, i):
    """Scrape and save the content of a single Fandom article."""
    r = get_with_retries(url)
    if r is None:
        print(f"Skipping article due to failed request: {url}")
        return

    soup = BeautifulSoup(r.text, "html.parser")
    title_tag = soup.find("h1", class_="page-header__title")
    content = soup.find("div", class_="mw-parser-output")

    if not title_tag or not content:
        print(f"Missing content or title in page: {url}")
        return

    title = title_tag.get_text(strip=True)
    filename = f"{i:04d}_{clean_filename(title)}.txt"
    filepath = os.path.join(output_dir, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"Skipping (already exists): {filename}")
        return

    # Extract relevant text content
    text_elements = content.find_all(["p", "li", "h2", "h3"])
    text = "\n".join(p.get_text(" ", strip=True) for p in text_elements)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\nTITLE: {title}\n\n{text}")
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Error writing file {filename}: {e}")

    time.sleep(delay)

# === MAIN ===
if __name__ == "__main__":
    all_urls = get_all_article_links(base_url + start_page)
    print(f"Found {len(all_urls)} pages")

    for i, url in enumerate(all_urls, start=1):
        scrape_article(url, i)
