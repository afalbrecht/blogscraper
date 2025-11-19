import click
from scrapers.wordpress import WordPressScraper
from scrapers.substack import SubstackScraper
from pdf_generator.generator import PDFGenerator
from pdf_generator.image_optimizer import ImageOptimizer
from bs4 import BeautifulSoup
import os
import hashlib
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@click.command()
@click.option('--url', prompt='Blog URL', help='The URL of the blog to scrape.')
@click.option('--type', prompt='Blog Type (wordpress/substack)', type=click.Choice(['wordpress', 'substack'], case_sensitive=False), help='The type of the blog.')
@click.option('--image', help='Path to a custom image for the frontispiece.', default=None)
@click.option('--title', help='Custom title for the PDF.', default=None)
@click.option('--author', help='Custom author for the PDF.', default=None)
def main(url, type, image, title, author):
    """Scrape a blog and generate a PDF."""
    click.echo(f"Scraping {url} as {type}...")
    
    if type == 'wordpress':
        scraper = WordPressScraper(url)
    else:
        # For Substack, check for authentication credentials in environment
        session_cookies = {}
        substack_sid = os.getenv('SUBSTACK_SID')
        substack_lli = os.getenv('SUBSTACK_LLI')
        
        if substack_sid and substack_lli:
            session_cookies = {
                'substack.sid': substack_sid,
                'substack.lli': substack_lli
            }
        
        scraper = SubstackScraper(url, session_cookies=session_cookies)

    
    posts = list(scraper.get_posts())
    posts = [p for p in posts if p and p.get('content')] # Filter empty posts and ensure content exists
    posts.reverse() # Make chronological (Oldest -> Newest)
    click.echo(f"Found {len(posts)} valid posts.")
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine blog title if not provided
    blog_title = title if title else (posts[0]['title'] if posts else "Blog Posts")
    
    # Determine author for filename
    pdf_author = author if author else "Unknown"
    
    # Sanitize title and author for filename
    def sanitize_filename(text):
        # Remove or replace characters that are invalid in filenames
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace spaces with underscores
        text = text.replace(' ', '_')
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        # Trim underscores from start/end
        text = text.strip('_')
        # Limit length to avoid filesystem issues
        return text[:100]
    
    safe_title = sanitize_filename(blog_title)
    safe_author = sanitize_filename(pdf_author)
    
    # Get first image from any post for frontispiece if available
    front_image = image
    if not front_image and posts:
        for post in posts:
            # Simple check for img tag in post content
            content = post.get('content')
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                img = soup.find('img')
                if img:
                    front_image = img.get('src')
                    break
    
    # --- Generate Optimized PDF (with images) ---
    click.echo("Optimizing images for PDF...")
    optimizer = ImageOptimizer()
    optimized_posts = []
    for post in posts:
        # Create a copy to avoid modifying original for text-only version
        post_copy = post.copy()
        if post_copy.get('content'):
            post_copy['content'] = optimizer.optimize_html_content(post_copy['content'], url)
        optimized_posts.append(post_copy)
        
    # Optimize front image if it's a URL
    optimized_front_image = front_image
    if front_image and front_image.startswith('http'):
        # We can reuse the optimizer's download logic manually or just let it be if it's just one image
        # But for consistency, let's optimize it too.
        try:
            # Hacky way to use the internal method, or we could expose it.
            # Let's just use the optimizer instance
            import hashlib
            hash_name = hashlib.md5(front_image.encode()).hexdigest()
            local_path = os.path.join(optimizer.output_dir, f"front_{hash_name}.jpg")
            if not os.path.exists(local_path):
                optimizer._download_and_optimize(front_image, local_path)
            optimized_front_image = f"file://{os.path.abspath(local_path)}"
        except Exception as e:
            print(f"Failed to optimize front image: {e}")

    images_pdf = os.path.join(output_dir, f"{safe_title}_{safe_author}_with_images.pdf")
    generator = PDFGenerator(images_pdf)
    generator.generate(optimized_posts, blog_title, optimized_front_image, author)
    click.echo(f"Generated {images_pdf}")

    # --- Generate Text-Only PDF ---
    click.echo("Generating text-only PDF...")
    text_only_posts = []
    for post in posts:
        post_copy = post.copy()
        if post_copy.get('content'):
            # Remove images
            soup = BeautifulSoup(post_copy['content'], 'html.parser')
            for img in soup.find_all('img'):
                img.decompose()
            for figure in soup.find_all('figure'): # Also remove figures if they contain images
                figure.decompose()
            post_copy['content'] = str(soup)
        text_only_posts.append(post_copy)
    
    # For text-only, we might still want the frontispiece? 
    # User said "one with images and one without". Usually text-only implies NO images at all.
    # But maybe the cover is okay? Let's assume NO images for strict text-only.
    
    text_only_pdf = os.path.join(output_dir, f"{safe_title}_{safe_author}_without_images.pdf")
    generator = PDFGenerator(text_only_pdf)
    generator.generate(text_only_posts, blog_title, None, author) # No front image
    click.echo(f"Generated {text_only_pdf}")
    
    # Clean up temporary optimized images
    import shutil
    if os.path.exists(optimizer.output_dir):
        shutil.rmtree(optimizer.output_dir)
        click.echo("Cleaned up temporary optimized images.")

if __name__ == '__main__':
    main()
