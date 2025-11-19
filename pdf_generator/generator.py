from typing import List, Dict, Any
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os

class PDFGenerator:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.env = Environment(loader=FileSystemLoader('pdf_generator/templates'))

    def generate(self, posts: List[Dict[str, Any]], blog_title: str, front_image: str = None, author: str = None):
        template = self.env.get_template('base.html')
        html_content = template.render(posts=posts, blog_title=blog_title, front_image=front_image, author=author)
        
        print(f"Generating PDF to {self.output_file}...")
        HTML(string=html_content).write_pdf(self.output_file)
        print("PDF generation complete.")

