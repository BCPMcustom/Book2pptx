import sys
import os
import zipfile
import glob
from parser.markdown_parser import (TableParser, HTMLTableRenderer, MarkdownParser)
from renderer.pptx_renderer import PowerPointRenderer
from pathlib import Path

def main():
    # sys.argv[0] is always the script name ('book2pptx.py')
    # sys.argv[1] will be the first argument passed ('path_to_markdown.md')
    if len(sys.argv) < 2:
        print("Error: Please provide a file path.")
        print("Usage: python3 book2pptx.py <path_to_markdown.md>")
        sys.exit(1)
        
    zip_file_input = sys.argv[1]
    print(f"Starting book2pptx script with archive: {zip_file_input}")


    # 1. Establish where our assets directory lives relative to this main file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")


    # -------------------------------------------------------------------------
    # STEP 1: Unzip the contents of argv[1] into /assets/
    # -------------------------------------------------------------------------
    print(f"Extracting {zip_file_input} into /assets/...")
    try:
        with zipfile.ZipFile(zip_file_input, 'r') as zip_ref:
            zip_ref.extractall(ASSETS_DIR)
    except FileNotFoundError:
        print(f"Error: Could not find the zip file at '{zip_file_input}'")
        sys.exit(1)
    except zipfile.BadZipFile:
        print(f"Error: '{zip_file_input}' is not a valid zip archive.")
        sys.exit(1)

 
    # -------------------------------------------------------------------------
    # STEP 2: Search /assets/ for the only .md file
    # -------------------------------------------------------------------------
    # glob looks specifically inside the assets folder for any file ending in .md
    
    md_search_pattern = os.path.join(ASSETS_DIR, "*.md")
    found_md_files = glob.glob(md_search_pattern)
    
    if not found_md_files:
        print("Error: No .md file found inside the extracted assets archive.")
        sys.exit(1)
        
    # Grab the target file (assuming there's exactly one as planned)
    searchResult = found_md_files[0]

    # -------------------------------------------------------------------------
    # STEP 3: Set input_path = "searchResult"
    # -------------------------------------------------------------------------
    
    input_path = searchResult
    print(f"Zip extraction complete. Found target markdown: {input_path}")
    print(f"Processing {input_path} through markdown_parser...")
    
    try:
        # 4. Instantiate your parser and pass the user's terminal variable into it
        parser = MarkdownParser()
        presentation = parser.parse(input_path)
        renderer = PowerPointRenderer()
        finalPPTX = renderer.render(presentation)
        new_filename = str(Path(zip_file_input).with_suffix('.pptx'))
        finalPPTX.save(new_filename)
        
        print("Finished processing successfully!")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)    

    print("Cleaning /assets/ folder...")

    for filename in os.listdir(ASSETS_DIR):
        file_path = os.path.join(ASSETS_DIR, filename)
    
        try:
            # Check if it is a file and delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    print("SUCCESS!!!")

if __name__ == "__main__":
    main()
