#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTML to HTML Converter
Extracts HTML content from MHTML files and converts quoted-printable encoding
"""

import re
import quopri
import sys
import os

def decode_quoted_printable(text):
    """Decode quoted-printable encoded text"""
    try:
        return quopri.decodestring(text).decode('utf-8', errors='ignore')
    except:
        return text

def extract_html_from_mhtml(mhtml_file_path, output_file_path):
    """Extract HTML content from MHTML file"""
    
    print(f"Reading MHTML file: {mhtml_file_path}")
    
    with open(mhtml_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find the main HTML section
    # Updated pattern to handle different Al Jazeera URL structures
    html_start_pattern = r'Content-Type: text/html.*?Content-Location: https://www\.aljazeera\.net/.*?palestine.*?\n\n'
    html_match = re.search(html_start_pattern, content, re.DOTALL)
    
    if not html_match:
        print("Could not find HTML content section")
        return False
    
    # Extract HTML content starting from DOCTYPE
    html_start = html_match.end()
    html_content = content[html_start:]
    
    # Find the end of the HTML content (look for the next boundary or end of file)
    # The main HTML section should end around line 297155 based on our search
    lines = html_content.split('\n')
    html_lines = []
    
    for i, line in enumerate(lines):
        # Stop when we hit the next MIME boundary or if we've gone too far
        if line.startswith('------MultipartBoundary') or i > 300000:
            break
        html_lines.append(line)
    
    # Join the HTML lines and decode quoted-printable
    raw_html = '\n'.join(html_lines)
    
    print("Decoding quoted-printable content...")
    decoded_html = decode_quoted_printable(raw_html)
    
    # Clean up the HTML
    # Remove any remaining quoted-printable artifacts
    decoded_html = re.sub(r'=\n', '', decoded_html)  # Remove soft line breaks
    decoded_html = re.sub(r'=([0-9A-F]{2})', lambda m: chr(int(m.group(1), 16)), decoded_html)  # Decode hex chars
    
    print(f"Writing HTML file: {output_file_path}")
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(decoded_html)
    
    print(f"Conversion completed successfully!")
    print(f"HTML file saved as: {output_file_path}")
    return True

def main():
    input_file = r"C:/Users/User/Documents/gazza_app/يوميات عزة - 4.mhtml"
    output_file = r"C:\Users\User\Documents\gazza_app\palestine_news_4.html"
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    success = extract_html_from_mhtml(input_file, output_file)
    if success:
        print(f"\n✅ Successfully converted MHTML to HTML!")
        print(f"📁 Output file: {output_file}")
    else:
        print("❌ Conversion failed")

if __name__ == "__main__":
    main()
