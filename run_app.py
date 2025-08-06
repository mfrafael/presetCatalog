"""
Simple launcher for XMP Preset Manager
"""

import os
import sys
print("Starting XMP Preset Manager...")
print(f"Current directory: {os.getcwd()}")
print(f"Python version: {sys.version}")

try:
    # Add current directory to path if needed
    if '' not in sys.path:
        sys.path.append('')
        
    # Import and run the app
    from main import main
    print("Imports successful, launching app...")
    main()
except ImportError as e:
    print(f"Import error: {str(e)}")
    print("Make sure PySide6 is installed. Run: pip install PySide6")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error launching app: {str(e)}")
    input("Press Enter to exit...")
