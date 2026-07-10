"""
Quick setup verification script
Run this to verify the project structure is correctly set up
"""
import os
import sys

def verify_structure():
    """Verify all required directories and files exist"""
    
    required_items = {
        'files': [
            'app.py',
            'requirements.txt',
            '.env.example',
            'README.md',
            'database/__init__.py',
            'database/db.py',
            'database/models.py',
            'services/__init__.py',
            'auth/__init__.py',
            'utils/__init__.py',
            'reports/__init__.py',
        ],
        'directories': [
            'database',
            'services',
            'auth',
            'utils',
            'reports',
            'uploads',
            'vector_db',
            'sample_docs',
        ]
    }
    
    print("🔍 Verifying Project Structure...")
    print("=" * 50)
    
    # Check files
    missing_files = []
    for file_path in required_items['files']:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing_files.append(file_path)
    
    print()
    
    # Check directories
    missing_dirs = []
    for dir_path in required_items['directories']:
        if os.path.isdir(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - MISSING")
            missing_dirs.append(dir_path)
    
    print("=" * 50)
    
    if not missing_files and not missing_dirs:
        print("✅ All required files and directories are present!")
        print("\n📦 Next Steps:")
        print("1. Create virtual environment: py -m venv venv")
        print("2. Activate it: venv\\Scripts\\activate")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Copy .env.example to .env and add your API key")
        print("5. Run the app: streamlit run app.py")
        return True
    else:
        print("❌ Setup incomplete!")
        if missing_files:
            print(f"\nMissing files: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"\nMissing directories: {', '.join(missing_dirs)}")
        return False

if __name__ == "__main__":
    success = verify_structure()
    sys.exit(0 if success else 1)
