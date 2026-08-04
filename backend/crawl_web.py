# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import os

# # --- CONFIG ---
# START_URL       = "https://www.srivasaviengg.ac.in"  # Replace with your college site
# MAX_PAGES       = 50       # Limit to avoid infinite crawling
# ALLOWED_DOMAIN  = "srivasaviengg.ac.in"  # Restrict to your college domain
# SAVE_DIR        = "web_pages"  # Folder to save crawled HTML/text

# visited = set()
# to_visit = [START_URL]

# os.makedirs(SAVE_DIR, exist_ok=True)

# def is_valid(url):
#     parsed = urlparse(url)
#     return parsed.netloc.endswith(ALLOWED_DOMAIN)

# def clean_text(html):
#     soup = BeautifulSoup(html, "html.parser")
#     for script in soup(["script", "style", "noscript"]):
#         script.decompose()
#     return soup.get_text(separator="\n", strip=True)

# def save_text(url, text):
#     filename = urlparse(url).path.strip("/").replace("/", "_") or "index"
#     filepath = os.path.join(SAVE_DIR, f"{filename}.txt")
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(text)

# def crawl():
#     count = 0
#     while to_visit and count < MAX_PAGES:
#         url = to_visit.pop(0)
#         if url in visited or not is_valid(url):
#             continue

#         try:
#             print(f"🌐 Crawling: {url}")
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()
#             visited.add(url)

#             text = clean_text(response.text)
#             save_text(url, text)
#             count += 1

#             soup = BeautifulSoup(response.text, "html.parser")
#             for link in soup.find_all("a", href=True):
#                 full_url = urljoin(url, link["href"])
#                 if is_valid(full_url) and full_url not in visited:
#                     to_visit.append(full_url)

#         except Exception as e:
#             print(f"⚠️ Failed to crawl {url}: {e}")

#     print(f"\n✅ Crawled {count} pages.")

# if __name__ == "__main__":
#     crawl()


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

# --- CONFIG ---
START_URL       = "https://www.srivasaviengg.ac.in" 
MAX_PAGES       = 500  # ✅ FIX: Increased limit to cover more of the site
ALLOWED_DOMAIN  = "srivasaviengg.ac.in" 
SAVE_DIR        = "web_page"  # Folder to save crawled HTML/text
PDF_LINKS_FILE  = "found_pdf_links.txt"

visited = set()
to_visit = [START_URL]

os.makedirs(SAVE_DIR, exist_ok=True)

def is_valid(url):
    """Check if the URL belongs to the allowed domain."""
    parsed = urlparse(url)
    # Check if netloc ends with the allowed domain (handles subdomains)
    return parsed.netloc.endswith(ALLOWED_DOMAIN)

def clean_text(html):
    """Extracts and cleans text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts, styles, and other non-content elements
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    return soup.get_text(separator="\n", strip=True)

def save_text(url, text):
    """Saves the cleaned text to a .txt file."""
    # Use the path to create a filename (safe replacement for / is _)
    filename = urlparse(url).path.strip("/").replace("/", "_").replace(".", "_") or "index"
    filepath = os.path.join(SAVE_DIR, f"{filename}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

def crawl():
    """Performs the BFS web crawl, saving text and extracting PDF links."""
    count = 0
    pdf_link_tracker = set()
    
    # Check for existing PDF links to avoid re-writing the same file
    if os.path.exists(PDF_LINKS_FILE):
        with open(PDF_LINKS_FILE, 'r', encoding='utf-8') as f:
            pdf_link_tracker.update(f.read().splitlines())
            print(f"Found {len(pdf_link_tracker)} existing PDF links to avoid duplicates.")


    while to_visit and count < MAX_PAGES:
        url = to_visit.pop(0)
        
        # Skip if already visited or invalid domain
        if url in visited or not is_valid(url):
            continue

        try:
            print(f"🌐 Crawling ({count+1}/{MAX_PAGES}): {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            visited.add(url)

            # 1. Save Text
            text = clean_text(response.text)
            save_text(url, text)
            count += 1

            soup = BeautifulSoup(response.text, "html.parser")
            
            # 2. Extract Links and PDFs
            new_pdf_links = []
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                
                # Check for PDF links
                if full_url.lower().endswith('.pdf'):
                    if is_valid(full_url) and full_url not in pdf_link_tracker:
                        new_pdf_links.append(full_url)
                        pdf_link_tracker.add(full_url)
                    continue 

                # Check for HTML pages to visit next
                if is_valid(full_url) and full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)
            
            # 3. Save new PDF links found on this page
            if new_pdf_links:
                with open(PDF_LINKS_FILE, "a", encoding="utf-8") as f:
                    for pdf_url in new_pdf_links:
                        f.write(pdf_url + "\n")
                print(f"   📑 Found {len(new_pdf_links)} new PDF link(s).")

            # Be a good web citizen
            time.sleep(0.5) 

        except Exception as e:
            print(f"⚠️ Failed to crawl {url}: {e}")

    print(f"\n✅ Crawling complete. Total {count} web pages crawled.")
    print(f"✅ All discovered PDF links saved to {PDF_LINKS_FILE}. You must download these files manually and place them in the 'pdfs' folder before running ingest.py.")

if __name__ == "__main__":
    crawl()