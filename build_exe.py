import PyInstaller.__main__
import os
import shutil

def build():
    # Application name
    app_name = "StockParserPro"
    
    # Entry point
    entry_point = "main.py"
    
    # Options
    opts = [
        entry_point,
        '--name=%s' % app_name,
        '--onefile',
        '--windowed',  # No console window
        '--clean',
        '--add-data=src/ui;src/ui',  # Include UI components if needed as resources
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
    ]
    
    print(f"Building {app_name}...")
    PyInstaller.__main__.run(opts)
    print("Build complete. Check the 'dist' folder.")

if __name__ == "__main__":
    # Clean previous builds
    if os.path.exists("build"): shutil.rmtree("build")
    if os.path.exists("dist"): shutil.rmtree("dist")
    
    build()
