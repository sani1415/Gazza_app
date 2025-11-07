#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research Tools for Palestine News Articles Dataset
Various analysis and search functions for the combined articles dataset
"""

import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display

class PalestineNewsAnalyzer:
    def __init__(self, json_file_path):
        """Initialize the analyzer with the combined articles dataset"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)
        print(f"Loaded {len(self.articles)} articles for analysis")
    
    def search_by_keywords(self, keywords, case_sensitive=False):
        """Search articles by keywords in title or excerpt"""
        results = []
        keywords_lower = [kw.lower() for kw in keywords] if not case_sensitive else keywords
        
        for article in self.articles:
            title = article.get('title', '').lower() if not case_sensitive else article.get('title', '')
            excerpt = article.get('excerpt', '').lower() if not case_sensitive else article.get('excerpt', '')
            
            if any(keyword in title or keyword in excerpt for keyword in keywords_lower):
                results.append(article)
        
        return results
    
    def get_articles_by_date_range(self, start_date, end_date):
        """Get articles within a specific date range"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        results = []
        for article in self.articles:
            article_date = datetime.strptime(article.get('date', ''), '%Y-%m-%d')
            if start <= article_date <= end:
                results.append(article)
        
        return results
    
    def get_articles_by_type(self, article_type):
        """Get articles by type (post, video, liveblog, episode)"""
        return [article for article in self.articles if article.get('type') == article_type]
    
    def analyze_timeline(self):
        """Analyze article distribution over time"""
        dates = [article.get('date') for article in self.articles if article.get('date')]
        date_counts = Counter(dates)
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(list(date_counts.items()), columns=['date', 'count'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        return df
    
    def get_most_active_days(self, top_n=20):
        """Get the most active days by article count"""
        dates = [article.get('date') for article in self.articles if article.get('date')]
        date_counts = Counter(dates)
        return date_counts.most_common(top_n)
    
    def analyze_content_themes(self, top_n=50):
        """Analyze common themes and keywords in titles"""
        all_titles = ' '.join([article.get('title', '') for article in self.articles])
        
        # Extract Arabic words (simplified approach)
        words = re.findall(r'[\u0600-\u06FF]+', all_titles)
        word_counts = Counter(words)
        
        return word_counts.most_common(top_n)
    
    def get_video_articles(self):
        """Get all video articles with their details"""
        videos = self.get_articles_by_type('video')
        return sorted(videos, key=lambda x: x.get('date', ''), reverse=True)
    
    def get_live_blog_articles(self):
        """Get all live blog articles"""
        liveblogs = self.get_articles_by_type('liveblog')
        return sorted(liveblogs, key=lambda x: x.get('date', ''), reverse=True)
    
    def search_by_url_pattern(self, pattern):
        """Search articles by URL pattern"""
        results = []
        for article in self.articles:
            link = article.get('link', '')
            if re.search(pattern, link):
                results.append(article)
        return results
    
    def get_articles_with_images(self):
        """Get articles that have images"""
        return [article for article in self.articles if article.get('image_url')]
    
    def export_to_csv(self, articles, filename):
        """Export articles to CSV for further analysis"""
        df = pd.DataFrame(articles)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Exported {len(articles)} articles to {filename}")
    
    def generate_wordcloud(self, text_field='title', output_file='wordcloud.png'):
        """Generate a word cloud from article titles or excerpts"""
        text = ' '.join([article.get(text_field, '') for article in self.articles])
        
        # Configure for Arabic text
        arabic_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(arabic_text)
        
        wordcloud = WordCloud(
            font_path='arial.ttf',  # You may need to install Arabic font
            width=800, height=400,
            background_color='white',
            max_words=100
        ).generate(bidi_text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def get_statistics(self):
        """Get comprehensive statistics about the dataset"""
        stats = {
            'total_articles': len(self.articles),
            'date_range': {
                'start': min([article.get('date') for article in self.articles if article.get('date')]),
                'end': max([article.get('date') for article in self.articles if article.get('date')])
            },
            'article_types': Counter([article.get('type') for article in self.articles]),
            'articles_with_images': len(self.get_articles_with_images()),
            'most_common_words': self.analyze_content_themes(20)
        }
        return stats

def main():
    """Example usage of the research tools"""
    print("🔍 PALESTINE NEWS RESEARCH TOOLS")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = PalestineNewsAnalyzer('articles_combined.json')
    
    # Example 1: Search for articles about specific topics
    print("\n1. Searching for articles about 'غزة' (Gaza):")
    gaza_articles = analyzer.search_by_keywords(['غزة'])
    print(f"Found {len(gaza_articles)} articles about Gaza")
    
    # Example 2: Get articles from a specific time period
    print("\n2. Articles from October 2023:")
    oct_2023_articles = analyzer.get_articles_by_date_range('2023-10-01', '2023-10-31')
    print(f"Found {len(oct_2023_articles)} articles from October 2023")
    
    # Example 3: Get video articles
    print("\n3. Video articles:")
    videos = analyzer.get_video_articles()
    print(f"Found {len(videos)} video articles")
    if videos:
        print(f"Latest video: {videos[0]['title']}")
    
    # Example 4: Most active days
    print("\n4. Most active days:")
    active_days = analyzer.get_most_active_days(10)
    for date, count in active_days:
        print(f"  {date}: {count} articles")
    
    # Example 5: Export specific data
    print("\n5. Exporting video articles to CSV...")
    analyzer.export_to_csv(videos[:100], 'video_articles_sample.csv')
    
    # Example 6: Get statistics
    print("\n6. Dataset Statistics:")
    stats = analyzer.get_statistics()
    print(f"Total articles: {stats['total_articles']:,}")
    print(f"Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    print(f"Articles with images: {stats['articles_with_images']:,}")

if __name__ == "__main__":
    main()
