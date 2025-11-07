#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Article Extractor for Al Jazeera Palestine News
Extracts articles from HTML file and creates structured data
"""

import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import html

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_date(date_text):
    """Parse date from various formats to standard format"""
    if not date_text:
        return None
    
    # Try multiple date patterns
    patterns = [
        # DD/MM/YYYY format (most common in this data)
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: (int(m.group(3)), int(m.group(2)), int(m.group(1)))),  # year, month, day
        # YYYY-MM-DD format
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),     # year, month, day
        # DD-MM-YYYY format
        (r'(\d{1,2})-(\d{1,2})-(\d{4})', lambda m: (int(m.group(3)), int(m.group(2)), int(m.group(1)))), # year, month, day
        # YYYY/MM/DD format
        (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))), # year, month, day
    ]
    
    for pattern, date_parser in patterns:
        date_match = re.search(pattern, date_text)
        if date_match:
            try:
                year, month, day = date_parser(date_match)
                return datetime(year, month, day).strftime('%Y-%m-%d')
            except (ValueError, IndexError):
                continue
    
    return None

def extract_articles(html_file_path):
    """Extract articles from HTML file"""
    
    print(f"Reading HTML file: {html_file_path}")
    
    with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    articles = []
    
    # Find all article elements
    article_elements = soup.find_all('article', class_='gc')
    
    print(f"Found {len(article_elements)} articles")
    
    for i, article in enumerate(article_elements):
        try:
            # Extract title
            title_elem = article.find('h3', class_='gc__title')
            title = ""
            link = ""
            if title_elem:
                link_elem = title_elem.find('a')
                if link_elem:
                    link = link_elem.get('href', '')
                    span_elem = link_elem.find('span')
                    if span_elem:
                        title = clean_text(span_elem.get_text())
            
            # Extract excerpt
            excerpt_elem = article.find('div', class_='gc__excerpt')
            excerpt = ""
            if excerpt_elem:
                p_elem = excerpt_elem.find('p')
                if p_elem:
                    excerpt = clean_text(p_elem.get_text())
            
            # Extract date - improved logic to handle different date formats
            date_text = ""
            
            # Method 1: Look for screen-reader-text with "Published On"
            date_elem = article.find('span', class_='screen-reader-text')
            if date_elem and "Published On" in date_elem.get_text():
                date_text = date_elem.get_text()
            
            # Method 2: Look for time elements with datetime attribute
            if not date_text:
                time_elem = article.find('time')
                if time_elem:
                    datetime_attr = time_elem.get('datetime', '')
                    if datetime_attr:
                        date_text = f"Published On {datetime_attr}"
            
            # Method 3: Look for date in URL pattern (extract from link)
            if not date_text and link:
                # Extract date from URL like /2024/7/16/
                url_date_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', link)
                if url_date_match:
                    year, month, day = url_date_match.groups()
                    date_text = f"Published On {day}/{month}/{year}"
            
            # Method 4: Look for any element containing date patterns
            if not date_text:
                # Search all text in the article for date patterns
                article_text = article.get_text()
                date_patterns = [
                    r'(\d{1,2}/\d{1,2}/\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
                    r'(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD
                    r'(\d{1,2}-\d{1,2}-\d{4})'   # DD-MM-YYYY or MM-DD-YYYY
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, article_text)
                    if match:
                        date_text = f"Published On {match.group(1)}"
                        break
            
            # Extract image
            img_elem = article.find('img', class_='gc__image')
            image_url = ""
            if img_elem:
                image_url = img_elem.get('src', '')
            
            # Extract article type
            article_class = article.get('class', [])
            article_type = "post"
            if 'gc--type-video' in article_class:
                article_type = "video"
            elif 'gc--type-liveblog' in article_class:
                article_type = "liveblog"
            elif 'gc--type-episode' in article_class:
                article_type = "episode"
            
            # Parse date
            parsed_date = parse_date(date_text)
            
            # Only include articles with valid data
            if title and link:
                article_data = {
                    'id': i + 1,
                    'title': title,
                    'excerpt': excerpt,
                    'link': link,
                    'date': parsed_date,
                    'date_text': date_text,
                    'image_url': image_url,
                    'type': article_type,
                    'source': 'Al Jazeera'
                }
                articles.append(article_data)
                
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            continue
    
    # Sort articles by date (newest first)
    articles.sort(key=lambda x: x['date'] or '1900-01-01', reverse=True)
    
    print(f"Successfully extracted {len(articles)} articles")
    return articles

def save_articles_to_json(articles, output_file):
    """Save articles to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Articles saved to: {output_file}")

def main():
    input_file = r"C:\Users\User\Documents\gazza_app\palestine_news_1.html"
    output_file = r"C:\Users\User\Documents\gazza_app\articles_data_1.json"
    
    try:
        articles = extract_articles(input_file)
        save_articles_to_json(articles, output_file)
        
        # Print some statistics
        print(f"\n📊 Statistics:")
        print(f"Total articles: {len(articles)}")
        
        # Count by type
        type_counts = {}
        for article in articles:
            article_type = article['type']
            type_counts[article_type] = type_counts.get(article_type, 0) + 1
        
        print(f"Article types:")
        for article_type, count in type_counts.items():
            print(f"  - {article_type}: {count}")
        
        # Count by date
        date_counts = {}
        for article in articles:
            date = article['date']
            if date:
                date_counts[date] = date_counts.get(date, 0) + 1
        
        print(f"Articles by date:")
        for date in sorted(date_counts.keys(), reverse=True):
            print(f"  - {date}: {date_counts[date]} articles")
        
        print(f"\n✅ Article extraction completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
