from .base_scraper import BaseScraper
from typing import Iterator, Dict, Any
import requests
from bs4 import BeautifulSoup

class WordPressScraper(BaseScraper):
    def get_posts(self) -> Iterator[Dict[str, Any]]:
        url = self.start_url
        while url:
            print(f"Fetching {url}...")
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error fetching {url}: {e}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all articles
            articles = soup.find_all('article')
            for article in articles:
                title_elem = article.find(class_='entry-title')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.find('a')['href'] if title_elem.find('a') else url
                
                # Fetch individual post page to get full content and avoid truncation
                # Some themes show full content on index, others don't. Safer to fetch.
                # But if the user wants "every post of a blog", fetching each might be slow but accurate.
                # Let's check if the content is already full here. 
                # Usually index pages have "Continue reading" or similar if truncated.
                # For safety and quality, let's fetch the individual page.
                
                yield self._scrape_single_post(link)

            # Pagination
            # Look for "Older posts" link
            # Common classes: .nav-previous a, .older-posts a
            next_page = soup.select_one('.nav-previous a')
            if next_page:
                url = next_page['href']
            else:
                url = None

    def _scrape_single_post(self, url: str) -> Dict[str, Any]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for title
            title_elem = soup.select_one('.entry-title, h1.entry-title, h1.post-title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Fallback to og:title
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    title = meta_title.get('content')
                else:
                    # Fallback to page title
                    page_title = soup.find('title')
                    if page_title:
                        title = page_title.get_text(strip=True).split('–')[0].strip() # Remove blog name if present
                    else:
                        # Fallback to URL slug
                        title = url.split('/')[-2].replace('-', ' ').title()
            
            content_elem = soup.select_one('.entry-content')
            
            # Clean content
            if content_elem:
                # Remove share buttons, likes, etc.
                for fluff in content_elem.select('.sharedaddy, .jp-relatedposts, .wpcnt'):
                    fluff.decompose()
                
                # Unwrap images from links
                for img_link in content_elem.find_all('a'):
                    if img_link.find('img'):
                        img_link.unwrap()

                content = str(content_elem)
            else:
                content = ""
                
            date_elem = soup.select_one('.entry-date')
            date = date_elem.get_text(strip=True) if date_elem else ""

            return {
                'title': title,
                'content': content,
                'date': date,
                'url': url
            }
        except Exception as e:
            print(f"Error scraping post {url}: {e}")
            return {}

