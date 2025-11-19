# BlogScraper

Ever wanted to just read your favourite blog on your ereader, so that you don't have to constantly look at a browser or the kinda lame formatting of Substack? Well thanks to the power of vibecoding, you can now with my BlogScraper: a cheeky python tool for scraping blog posts from WordPress and Substack blogs and generating decently formatted PDFs with a nice frontispiece and table of contents.


## Features

- **Multi-Platform Support**: Scrapes both WordPress and Substack blogs
- **Dual PDF Generation**: Creates two versions of your blog compilation:
  - **Images PDF**: Full-featured PDF with all images optimized
  - **Text-Only PDF**: Lightweight version without images for easier reading
- **Smart Content Cleaning**: Automatically removes unwanted elements like:
  - Share buttons and social widgets
  - Subscribe prompts
  - Embedded posts and "grey boxes"
  - Restack/expand buttons
  - Other HTML artifacts
- **Chronological Ordering**: Posts are arranged from oldest to newest
- **Professional Frontispiece**: Customizable cover page with:
  - Blog title (auto-detected or custom)
  - Author name (optional)
  - Cover image (auto-detected from first post or custom)
- **Image Optimization**: Automatically optimizes images for smaller PDF file sizes
- **Table of Contents**: Functional TOC with clickable links to each post

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd blogscraper
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with interactive prompts:

```bash
python main.py
```

You'll be prompted to enter:

- Blog URL
- Blog type (wordpress or substack)

### Advanced Usage with Options

Specify all options via command-line arguments:

```bash
python main.py --url <blog-url> --type <wordpress|substack> [OPTIONS]
```

#### Available Options

- `--url`: The URL of the blog to scrape (required)
- `--type`: Blog platform type - either `wordpress` or `substack` (required)
- `--title`: Custom title for the PDF (optional, defaults to blog name)
- `--author`: Custom author name for the PDF (optional)
- `--image`: Path to a custom image for the frontispiece (optional, auto-detects from first post if not provided)

### Examples

**Scrape a WordPress blog:**

```bash
python main.py --url https://example.wordpress.com --type wordpress
```

**Scrape a Substack blog with custom title and author:**

```bash
python main.py --url https://example.substack.com --type substack --title "My Favorite Blog" --author "John Doe"
```

**Use a custom cover image:**

```bash
python main.py --url https://example.com --type wordpress --image /path/to/cover.jpg
```

## Output

The tool generates two PDF files in the `output/` directory:

1. `<type>_blog_images.pdf` - Full PDF with optimized images
2. `<type>_blog_text_only.pdf` - Text-only version without images

## Project Structure

```
blogscraper/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── scrapers/              # Blog scraper modules
│   ├── __init__.py
│   ├── base_scraper.py    # Base scraper class
│   ├── wordpress.py       # WordPress scraper
│   └── substack.py        # Substack scraper
├── pdf_generator/         # PDF generation modules
│   ├── __init__.py
│   ├── generator.py       # PDF generator
│   ├── image_optimizer.py # Image optimization
│   └── templates/         # HTML templates for PDF
└── output/                # Generated PDFs (gitignored)
```

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `weasyprint` - PDF generation
- `click` - CLI interface
- `jinja2` - Template rendering
- `Pillow` - Image processing

## How It Works

1. **Scraping**: The tool uses platform-specific scrapers to fetch blog posts:

   - WordPress: Scrapes via HTML parsing with pagination support
   - Substack: Uses the Substack API with rate limiting and retry logic
2. **Content Cleaning**: Removes unwanted HTML elements and artifacts while preserving the actual content
3. **Image Processing**: Downloads and optimizes images to reduce PDF file size
4. **PDF Generation**: Uses WeasyPrint to generate professional PDFs with:

   - Custom frontispiece
   - Table of contents
   - Properly formatted posts in chronological order

## Troubleshooting

### Rate Limiting (Substack)

If you encounter rate limiting errors when scraping Substack blogs, the tool automatically:

- Adds random delays between requests (1-3 seconds)
- Retries failed requests up to 3 times
- Waits 30 seconds when rate limits are hit

### Missing Content

If posts appear empty or incomplete:

- Verify the blog URL is correct
- Check that the blog is publicly accessible
- Some blogs may have custom themes that require scraper adjustments

### PDF Generation Errors

If PDF generation fails:

- Ensure all dependencies are installed correctly
- Check that WeasyPrint's system dependencies are installed (see [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation))

## License

This project is provided as-is for personal use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
