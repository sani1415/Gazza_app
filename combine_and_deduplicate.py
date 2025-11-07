#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combine and Deduplicate Articles from Multiple JSON Files
Combines all articles_data_*.json files and removes duplicates based on title and link
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def load_articles_from_file(file_path):
    """Load articles from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} articles from {file_path}")
        return articles
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def deduplicate_articles(all_articles):
    """Remove duplicate articles based on title and link"""
    seen_articles = {}
    unique_articles = []
    duplicates_removed = 0
    
    for article in all_articles:
        # Create a unique key based on title and link
        key = f"{article.get('title', '')}_{article.get('link', '')}"
        
        if key not in seen_articles:
            seen_articles[key] = article
            unique_articles.append(article)
        else:
            duplicates_removed += 1
            # Keep the article with more complete data (prefer non-null dates, longer excerpts)
            existing = seen_articles[key]
            if (article.get('date') and not existing.get('date')) or \
               (len(article.get('excerpt', '')) > len(existing.get('excerpt', ''))):
                # Replace with better version
                seen_articles[key] = article
                unique_articles = [a for a in unique_articles if a != existing]
                unique_articles.append(article)
    
    print(f"Removed {duplicates_removed} duplicate articles")
    return unique_articles

def analyze_articles(articles):
    """Analyze the combined articles dataset"""
    print(f"\n📊 COMBINED DATASET ANALYSIS")
    print(f"=" * 50)
    print(f"Total unique articles: {len(articles)}")
    
    # Count by type
    type_counts = defaultdict(int)
    for article in articles:
        article_type = article.get('type', 'unknown')
        type_counts[article_type] += 1
    
    print(f"\nArticle types:")
    for article_type, count in sorted(type_counts.items()):
        print(f"  - {article_type}: {count:,}")
    
    # Date analysis
    dates = [article.get('date') for article in articles if article.get('date')]
    if dates:
        dates.sort()
        print(f"\nDate range: {dates[0]} to {dates[-1]}")
        
        # Count by year
        year_counts = defaultdict(int)
        for date in dates:
            year = date.split('-')[0]
            year_counts[year] += 1
        
        print(f"\nArticles by year:")
        for year in sorted(year_counts.keys()):
            print(f"  - {year}: {year_counts[year]:,} articles")
    
    # Count articles with missing data
    missing_dates = sum(1 for article in articles if not article.get('date'))
    missing_excerpts = sum(1 for article in articles if not article.get('excerpt'))
    missing_images = sum(1 for article in articles if not article.get('image_url'))
    
    print(f"\nData completeness:")
    print(f"  - Articles with dates: {len(articles) - missing_dates:,} ({((len(articles) - missing_dates)/len(articles)*100):.1f}%)")
    print(f"  - Articles with excerpts: {len(articles) - missing_excerpts:,} ({((len(articles) - missing_excerpts)/len(articles)*100):.1f}%)")
    print(f"  - Articles with images: {len(articles) - missing_images:,} ({((len(articles) - missing_images)/len(articles)*100):.1f}%)")
    
    return {
        'total_articles': len(articles),
        'type_counts': dict(type_counts),
        'date_range': f"{dates[0]} to {dates[-1]}" if dates else "No dates",
        'year_counts': dict(year_counts),
        'missing_dates': missing_dates,
        'missing_excerpts': missing_excerpts,
        'missing_images': missing_images
    }

def main():
    """Main function to combine and deduplicate all JSON files"""
    print("🔄 COMBINING AND DEDUPLICATING ARTICLES")
    print("=" * 50)
    
    # Find all articles_data_*.json files
    json_files = []
    for i in range(1, 7):  # Check files 1-6
        file_path = f"articles_data_{i}.json"
        if os.path.exists(file_path):
            json_files.append(file_path)
    
    print(f"Found {len(json_files)} JSON files to process:")
    for file_path in json_files:
        print(f"  - {file_path}")
    
    # Load all articles
    all_articles = []
    for file_path in json_files:
        articles = load_articles_from_file(file_path)
        all_articles.extend(articles)
    
    print(f"\nTotal articles before deduplication: {len(all_articles):,}")
    
    # Remove duplicates
    unique_articles = deduplicate_articles(all_articles)
    
    # Reassign IDs
    for i, article in enumerate(unique_articles, 1):
        article['id'] = i
    
    # Analyze the combined dataset
    analysis = analyze_articles(unique_articles)
    
    # Save combined file
    output_file = "articles_combined.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ SUCCESS!")
    print(f"Combined dataset saved to: {output_file}")
    print(f"Final unique articles: {len(unique_articles):,}")
    print(f"Duplicates removed: {len(all_articles) - len(unique_articles):,}")
    
    # Save analysis summary
    summary_file = "dataset_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
