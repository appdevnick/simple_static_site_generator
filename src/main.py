import os
import shutil
from pathlib import Path
from utils import copy_from_to_dir, generate_pages_recursive

def main():
    # Define paths
    project_dir = Path(__file__).parent.parent
    public_dir = project_dir / 'public'
    static_dir = project_dir / 'static'
    content_dir = project_dir / 'content'
    template_path = project_dir / 'template.html'

    # Delete existing public directory if it exists
    if public_dir.exists():
        shutil.rmtree(public_dir)
    
    # Create public directory
    public_dir.mkdir(exist_ok=True)

    # Copy static files to public directory
    copy_from_to_dir(static_dir, public_dir)

    # Generate pages recursively from content to public
    generate_pages_recursive(content_dir, template_path, public_dir)

if __name__ == '__main__':
    main()