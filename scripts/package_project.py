import os
import zipfile
import datetime
from pathlib import Path

def package_project():
    # Define project root (parent of 'scripts')
    base_dir = Path(__file__).resolve().parent.parent
    project_name = base_dir.name
    
    # Create timestamped zip name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{project_name}_backup_{timestamp}.zip"
    zip_path = base_dir / zip_filename
    
    # Directories to exclude
    EXCLUDE_DIRS = {
        'venv', 
        '__pycache__', 
        '.git', 
        '.idea', 
        '.vscode',
        'media', # Optional: usually user data, can be large, but maybe user wants it? 
                 # Let's KEEP media as it's part of the demo state, 
                 # but usually one excludes it for code distribution. 
                 # For "downloadable folder" matching current state, I should probably KEEP it.
                 # I will keep media.
        'logs'   # Maybe keep logs? sure.
    }
    
    EXCLUDE_EXTENSIONS = {'.pyc'}
    
    print(f"📦 Packaging project into: {zip_filename}")
    print(f"   Source: {base_dir}")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(base_dir):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                # Check relative path to avoid zipping the zip itself if it's in the root
                rel_root = os.path.relpath(root, base_dir)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    # Skip the zip file itself and any other zips to prevent recursion/duplication
                    if file.endswith('.zip'):
                        continue
                        
                    if any(file.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                        continue
                        
                    # Add file to zip
                    # print(f"   Adding {rel_path}")
                    zipf.write(file_path, rel_path)
                    
        print(f"\n✅ Success! Project packaged.")
        print(f"📍 Location: {zip_path}")
        print(f"📦 Size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"\n❌ Error packaging project: {e}")

if __name__ == "__main__":
    package_project()
