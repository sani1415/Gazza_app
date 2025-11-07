#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Specific Research Examples for Palestine News Dataset
Ready-to-use analysis scripts for common research questions
"""

import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import pandas as pd

def load_articles():
    """Load the combined articles dataset"""
    with open('articles_combined.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def research_example_1_timeline_analysis():
    """Example 1: Analyze article frequency over time"""
    print("📅 TIMELINE ANALYSIS")
    print("=" * 40)
    
    articles = load_articles()
    
    # Group by month
    monthly_counts = defaultdict(int)
    for article in articles:
        date = article.get('date', '')
        if date:
            month = date[:7]  # YYYY-MM
            monthly_counts[month] += 1
    
    # Sort by month
    sorted_months = sorted(monthly_counts.items())
    
    print("Articles per month:")
    for month, count in sorted_months:
        print(f"  {month}: {count:,} articles")
    
    # Find peak months
    peak_months = sorted(monthly_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\nPeak months:")
    for month, count in peak_months:
        print(f"  {month}: {count:,} articles")

def research_example_2_content_analysis():
    """Example 2: Analyze content themes and keywords"""
    print("\n🔍 CONTENT THEME ANALYSIS")
    print("=" * 40)
    
    articles = load_articles()
    
    # Common Arabic keywords to search for
    keywords = [
        'غزة', 'الضفة', 'القدس', 'حماس', 'إسرائيل', 'الاحتلال',
        'شهداء', 'جرحى', 'قصف', 'مفاوضات', 'هدنة', 'أسرى'
    ]
    
    keyword_counts = {}
    for keyword in keywords:
        count = sum(1 for article in articles 
                   if keyword in article.get('title', '') or keyword in article.get('excerpt', ''))
        keyword_counts[keyword] = count
    
    print("Keyword frequency in titles and excerpts:")
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {keyword}: {count:,} articles")

def research_example_3_video_analysis():
    """Example 3: Analyze video content specifically"""
    print("\n🎥 VIDEO CONTENT ANALYSIS")
    print("=" * 40)
    
    articles = load_articles()
    videos = [article for article in articles if article.get('type') == 'video']
    
    print(f"Total video articles: {len(videos):,}")
    
    # Group videos by month
    video_monthly = defaultdict(int)
    for video in videos:
        date = video.get('date', '')
        if date:
            month = date[:7]
            video_monthly[month] += 1
    
    print("\nVideo articles per month:")
    for month in sorted(video_monthly.keys()):
        print(f"  {month}: {video_monthly[month]} videos")

def research_example_4_live_blog_analysis():
    """Example 4: Analyze live blog coverage"""
    print("\n📺 LIVE BLOG ANALYSIS")
    print("=" * 40)
    
    articles = load_articles()
    liveblogs = [article for article in articles if article.get('type') == 'liveblog']
    
    print(f"Total live blog entries: {len(liveblogs):,}")
    
    # Find days with most live blog activity
    liveblog_dates = [article.get('date') for article in liveblogs if article.get('date')]
    date_counts = Counter(liveblog_dates)
    
    print("\nDays with most live blog activity:")
    for date, count in date_counts.most_common(10):
        print(f"  {date}: {count} live blog entries")

def research_example_5_export_specific_data():
    """Example 5: Export specific subsets of data"""
    print("\n📤 DATA EXPORT EXAMPLES")
    print("=" * 40)
    
    articles = load_articles()
    
    # Export all video articles
    videos = [article for article in articles if article.get('type') == 'video']
    with open('video_articles.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(videos)} video articles to video_articles.json")
    
    # Export articles from 2024
    articles_2024 = [article for article in articles if article.get('date', '').startswith('2024')]
    with open('articles_2024.json', 'w', encoding='utf-8') as f:
        json.dump(articles_2024, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(articles_2024)} articles from 2024 to articles_2024.json")
    
    # Export live blogs
    liveblogs = [article for article in articles if article.get('type') == 'liveblog']
    with open('live_blog_articles.json', 'w', encoding='utf-8') as f:
        json.dump(liveblogs, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(liveblogs)} live blog articles to live_blog_articles.json")

def research_example_6_search_function():
    """Example 6: Create a search function"""
    print("\n🔍 SEARCH FUNCTION EXAMPLE")
    print("=" * 40)
    
    articles = load_articles()
    
    def search_articles(query, search_in='both'):
        """Search articles by query"""
        results = []
        query_lower = query.lower()
        
        for article in articles:
            title = article.get('title', '').lower()
            excerpt = article.get('excerpt', '').lower()
            
            if search_in == 'title' and query_lower in title:
                results.append(article)
            elif search_in == 'excerpt' and query_lower in excerpt:
                results.append(article)
            elif search_in == 'both' and (query_lower in title or query_lower in excerpt):
                results.append(article)
        
        return results
    
    # Example searches
    print("Searching for 'مفاوضات' (negotiations):")
    negotiations = search_articles('مفاوضات')
    print(f"Found {len(negotiations)} articles about negotiations")
    
    print("\nSearching for 'شهداء' (martyrs):")
    martyrs = search_articles('شهداء')
    print(f"Found {len(martyrs)} articles about martyrs")

def research_example_7_date_range_analysis():
    """Example 7: Analyze specific date ranges"""
    print("\n📊 DATE RANGE ANALYSIS")
    print("=" * 40)
    
    articles = load_articles()
    
    def get_articles_in_range(start_date, end_date):
        """Get articles within a date range"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        results = []
        for article in articles:
            article_date = datetime.strptime(article.get('date', ''), '%Y-%m-%d')
            if start <= article_date <= end:
                results.append(article)
        return results
    
    # Analyze October 7, 2023 period (Al-Aqsa Flood)
    oct_7_period = get_articles_in_range('2023-10-07', '2023-10-14')
    print(f"Articles from October 7-14, 2023: {len(oct_7_period)}")
    
    # Analyze recent period
    recent_period = get_articles_in_range('2025-08-01', '2025-09-02')
    print(f"Articles from August-September 2025: {len(recent_period)}")

def main():
    """Run all research examples"""
    print("🔬 PALESTINE NEWS RESEARCH EXAMPLES")
    print("=" * 50)
    
    research_example_1_timeline_analysis()
    research_example_2_content_analysis()
    research_example_3_video_analysis()
    research_example_4_live_blog_analysis()
    research_example_5_export_specific_data()
    research_example_6_search_function()
    research_example_7_date_range_analysis()
    
    print("\n✅ All research examples completed!")
    print("\n💡 TIPS FOR FURTHER RESEARCH:")
    print("1. Use the search function to find specific topics")
    print("2. Export subsets of data for detailed analysis")
    print("3. Analyze trends over time using date ranges")
    print("4. Focus on specific content types (videos, live blogs)")
    print("5. Use external tools like Excel, Python pandas, or R for advanced analysis")

if __name__ == "__main__":
    main()
