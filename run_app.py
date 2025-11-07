#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup script for Palestine News Web Application
"""

import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to start the application"""
    print("🚀 Starting Palestine News Web Application...")
    print("=" * 50)
    
    # Check if articles_combined.json exists
    if not os.path.exists('articles_combined.json'):
        print("❌ Error: articles_combined.json not found!")
        print("Please make sure you have run the combine_and_deduplicate.py script first.")
        sys.exit(1)
    
    # Check if Flask is installed
    try:
        import flask
        print(f"✅ Flask version: {flask.__version__}")
    except ImportError:
        print("❌ Error: Flask is not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All dependencies found")
    print("🌐 Starting web server...")
    print("📱 The application will open in your browser automatically")
    print("🔗 Or visit: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    # Start the Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == "__main__":
    main()
