import os
import shutil
from utils import copy_from_to_dir, generate_page

def main():
    # Define paths
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(project_dir, 'public')
    static_dir = os.path.join(project_dir, 'static')
    content_dir = os.path.join(project_dir, 'content')
    template_path = os.path.join(project_dir, 'template.html')

    # Delete existing public directory if it exists
    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
    
    # Create public directory
    os.makedirs(public_dir, exist_ok=True)

    # Copy static files to public directory
    copy_from_to_dir(static_dir, public_dir)

    # Generate index.html
    index_md_path = os.path.join(content_dir, 'index.md')
    index_html_path = os.path.join(public_dir, 'index.html')
    generate_page(index_md_path, template_path, index_html_path)

if __name__ == "__main__":
    main()