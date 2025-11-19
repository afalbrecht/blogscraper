from .base_scraper import BaseScraper
from typing import Iterator, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
import random

class SubstackScraper(BaseScraper):
    def get_posts(self) -> Iterator[Dict[str, Any]]:
        offset = 0
        limit = 12
        base_api_url = self.start_url.rstrip('/') + '/api/v1/archive'
        
        while True:
            print(f"Fetching posts from offset {offset}...")
            params = {
                'sort': 'new',
                'search': '',
                'offset': offset,
                'limit': limit
            }
            
            try:
                # Add delay
                time.sleep(random.uniform(1, 3))
                response = requests.get(base_api_url, params=params)
                
                if response.status_code == 429:
                    print("Rate limit hit. Sleeping for 30 seconds...")
                    time.sleep(30)
                    continue
                    
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Error fetching API: {e}")
                break
            
            if not data:
                break
                
            for post in data:
                post_url = post.get('canonical_url')
                if not post_url:
                    slug = post.get('slug')
                    if slug:
                        post_url = f"{self.start_url.rstrip('/')}/p/{slug}"
                
                if post_url:
                    yield self._scrape_single_post(post_url)
            
            if len(data) < limit:
                break
                
            offset += limit

    def _scrape_single_post(self, url: str) -> Dict[str, Any]:
        print(f"Fetching {url}...")
        retries = 3
        while retries > 0:
            try:
                time.sleep(random.uniform(1, 3))
                response = requests.get(url)
                
                if response.status_code == 429:
                    print(f"Rate limit hit for {url}. Sleeping for 30 seconds...")
                    time.sleep(30)
                    retries -= 1
                    continue
                
                response.raise_for_status()
                break
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return {}
        
        if retries == 0:
            print(f"Failed to fetch {url} after retries.")
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_elem = soup.select_one('h1.post-title, h1.pencraft-title')
        title = title_elem.get_text(strip=True) if title_elem else "No Title"
        
        content_elem = soup.select_one('div.available-content, div.body, div.markup')
        
        if content_elem:
            # Clean fluff
            # Remove share buttons, subscribe widgets, button wrappers
            # Also remove "grey box" links (embedded posts/restacks)
            # Common classes: .embedded-post-wrap, .embedded-post, .tweet-embed, .instagram-media
            # New additions: .image-link-expand, .caption-is-link, .image-link
            for fluff in content_elem.select('.share-dialog, .subscribe-widget, .button-wrapper, .embedded-post-wrap, .embedded-post, .tweet-embed, .instagram-media, .image-link-expand, .caption-is-link'):
                fluff.decompose()
            
            # Remove elements that look like restack buttons (often just links with icons)
            # Sometimes they are in `a` tags with specific classes or SVG children
            # Also remove buttons with aria-label="Link" or specific classes
            for btn in content_elem.find_all('button'):
                if btn.get('aria-label') == 'Link' or 'restack-image' in btn.get('class', []) or 'view-image' in btn.get('class', []):
                    btn.decompose()
            
            # Unwrap images from links
            # The user wants images to not be hyperlinks
            for img_link in content_elem.find_all('a'):
                if img_link.find('img'):
                    img_link.unwrap()
            
            # Remove empty links that might be left over (often the "grey boxes" are links wrapping nothing or SVGs)
            for link in content_elem.find_all('a'):
                if not link.get_text(strip=True) and not link.find('img'):
                    link.decompose()

            content = str(content_elem)
        else:
            content = ""
        
        date_elem = soup.select_one('div.post-date, div.pencraft-subtitle')
        date = date_elem.get_text(strip=True) if date_elem else ""

        return {
            'title': title,
            'content': content,
            'date': date,
            'url': url
        }

