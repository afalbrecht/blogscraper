import os
import requests
from PIL import Image
from io import BytesIO
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ImageOptimizer:
    def __init__(self, output_dir='optimized_images', max_width=1000, quality=80):
        self.output_dir = output_dir
        self.max_width = max_width
        self.quality = quality
        os.makedirs(self.output_dir, exist_ok=True)

    def optimize_html_content(self, html_content: str, base_url: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
                
            # Handle relative URLs
            full_url = urljoin(base_url, src)
            
            # Generate a unique filename based on URL
            hash_name = hashlib.md5(full_url.encode()).hexdigest()
            local_filename = f"{hash_name}.jpg"
            local_path = os.path.join(self.output_dir, local_filename)
            
            # Check if already optimized
            if not os.path.exists(local_path):
                try:
                    self._download_and_optimize(full_url, local_path)
                except Exception as e:
                    print(f"Failed to optimize image {full_url}: {e}")
                    continue
            
            # Update img src to point to local file
            # WeasyPrint needs absolute path or file:// URI
            abs_path = os.path.abspath(local_path)
            img['src'] = f"file://{abs_path}"
            
            # Remove srcset to force using the optimized image
            if img.has_attr('srcset'):
                del img['srcset']
                
        return str(soup)

    def _download_and_optimize(self, url: str, output_path: str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        
        # Convert to RGB (handle PNG transparency by making white background or just dropping alpha)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            bg = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            bg.paste(image, mask=image.split()[3])
            image = bg
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Resize if too large
        if image.width > self.max_width:
            ratio = self.max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
            
        # Save as JPEG with optimization
        image.save(output_path, 'JPEG', quality=self.quality, optimize=True)
