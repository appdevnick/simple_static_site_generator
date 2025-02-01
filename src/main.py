from utils import copy_from_to_dir
import os

def main():
    # Ensure public/ directory exists
    public_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    # Copy static/ contents to public/
    copy_from_to_dir(static_dir, public_dir)

if __name__ == "__main__":
    main()