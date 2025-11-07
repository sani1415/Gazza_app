#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Palestine News Research Web Application
Beautiful web interface for researching the Palestine news dataset
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import os
import requests
from bs4 import BeautifulSoup
import time
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn

app = Flask(__name__)

# Add custom filter for number formatting
@app.template_filter('number_format')
def number_format(value):
    """Format number with commas"""
    return f"{value:,}"

# Add template function for type labels
@app.template_global()
def getTypeLabel(article_type):
    """Convert article type to Arabic label"""
    type_labels = {
        'post': 'مقال',
        'video': 'فيديو',
        'liveblog': 'بث مباشر',
        'episode': 'حلقة',
        'gallery': 'معرض صور'
    }
    return type_labels.get(article_type, article_type)

class NewsAnalyzer:
    def __init__(self, json_file_path):
        """Initialize the analyzer with the combined articles dataset"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)
        print(f"Loaded {len(self.articles)} articles for web analysis")
        self.content_cache = {}  # Cache for fetched article content
    
    def search_articles(self, query, search_type='all', content_type='all', date_from=None, date_to=None):
        """Search articles with multiple filters"""
        results = []
        query_lower = query.lower() if query else ""
        
        for article in self.articles:
            # Text search
            if query:
                title = article.get('title', '').lower()
                excerpt = article.get('excerpt', '').lower()
                
                if search_type == 'title' and query_lower not in title:
                    continue
                elif search_type == 'excerpt' and query_lower not in excerpt:
                    continue
                elif search_type == 'all' and query_lower not in title and query_lower not in excerpt:
                    continue
            
            # Content type filter
            if content_type != 'all' and article.get('type') != content_type:
                continue
            
            # Date range filter
            if date_from and article.get('date', '') < date_from:
                continue
            if date_to and article.get('date', '') > date_to:
                continue
            
            results.append(article)
        
        return results
    
    def get_statistics(self):
        """Get comprehensive statistics"""
        dates = [article.get('date') for article in self.articles if article.get('date')]
        types = [article.get('type') for article in self.articles]
        
        return {
            'total_articles': len(self.articles),
            'date_range': {
                'start': min(dates) if dates else None,
                'end': max(dates) if dates else None
            },
            'article_types': dict(Counter(types)),
            'articles_with_images': len([a for a in self.articles if a.get('image_url')])
        }
    
    def get_timeline_data(self):
        """Get timeline data for charts"""
        monthly_counts = defaultdict(int)
        for article in self.articles:
            date = article.get('date', '')
            if date:
                month = date[:7]  # YYYY-MM
                monthly_counts[month] += 1
        
        return sorted(monthly_counts.items())
    
    def get_keyword_analysis(self, keywords):
        """Analyze keyword frequency"""
        keyword_counts = {}
        for keyword in keywords:
            count = sum(1 for article in self.articles 
                       if keyword in article.get('title', '') or keyword in article.get('excerpt', ''))
            keyword_counts[keyword] = count
        return keyword_counts
    
    def fetch_article_content(self, article_url):
        """Fetch full article content from Al Jazeera website"""
        # Check cache first
        if article_url in self.content_cache:
            return self.content_cache[article_url]
        
        try:
            # Add headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(article_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main article content
            content_selectors = [
                '.wysiwyg--all-content',  # Al Jazeera main content
                '.article-body',         # Alternative content class
                '.post-content',         # Another alternative
                'article .content',      # Generic article content
                '.entry-content',        # WordPress style
            ]
            
            article_content = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    article_content = content_element
                    break
            
            if not article_content:
                # Fallback: try to find any div with substantial text content
                content_divs = soup.find_all('div', string=lambda text: text and len(text.strip()) > 200)
                if content_divs:
                    article_content = content_divs[0]
            
            if article_content:
                # Clean up the content
                # Remove unwanted elements
                for unwanted in article_content.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    unwanted.decompose()
                
                # Extract text and format it
                content_text = article_content.get_text(separator='\n', strip=True)
                
                # Clean up extra whitespace
                content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
                content_text = content_text.strip()
                
                # Cache the result
                self.content_cache[article_url] = content_text
                return content_text
            else:
                return "عذراً، لم يتم العثور على محتوى المقال الكامل."
                
        except requests.RequestException as e:
            print(f"Error fetching article content: {e}")
            return "عذراً، حدث خطأ في تحميل محتوى المقال."
        except Exception as e:
            print(f"Error parsing article content: {e}")
            return "عذراً، حدث خطأ في معالجة محتوى المقال."
    
    def create_word_document(self, articles, date, include_content=False):
        """Create a Word document with articles from a specific date"""
        doc = Document()
        
        # Set document direction to RTL
        doc.styles['Normal'].font.name = 'Arial'
        doc.styles['Normal'].font.size = Inches(0.12)
        
        # Add title
        title = doc.add_heading(f'أخبار فلسطين - {self.format_date_arabic(date)}', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add summary
        summary = doc.add_paragraph(f'عدد المقالات: {len(articles)} مقال')
        summary.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add separator
        doc.add_paragraph('=' * 50)
        
        # Add articles
        for i, article in enumerate(articles, 1):
            # Article number and title
            article_heading = doc.add_heading(f'{i}. {article.get("title", "بدون عنوان")}', level=1)
            article_heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Article metadata
            metadata = doc.add_paragraph()
            metadata.add_run(f'نوع المحتوى: {getTypeLabel(article.get("type", "post"))}').bold = True
            metadata.add_run(f' | تاريخ النشر: {article.get("date", "غير محدد")}')
            metadata.add_run(f' | المصدر: {article.get("source", "الجزيرة نت")}')
            metadata.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Article excerpt
            if article.get('excerpt'):
                excerpt_heading = doc.add_heading('ملخص المقال:', level=2)
                excerpt_heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                
                excerpt_para = doc.add_paragraph(article['excerpt'])
                excerpt_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Full content if requested
            if include_content and article.get('link'):
                content_heading = doc.add_heading('المحتوى الكامل:', level=2)
                content_heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                
                try:
                    full_content = self.fetch_article_content(article['link'])
                    if full_content and not full_content.startswith('عذراً'):
                        # Split content into paragraphs
                        paragraphs = full_content.split('\n')
                        for para in paragraphs:
                            if para.strip():
                                content_para = doc.add_paragraph(para.strip())
                                content_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    else:
                        no_content = doc.add_paragraph('لم يتم العثور على المحتوى الكامل')
                        no_content.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                except Exception as e:
                    error_para = doc.add_paragraph(f'خطأ في تحميل المحتوى: {str(e)}')
                    error_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Article link (only show if not including full content)
            if not include_content:
                link_para = doc.add_paragraph()
                link_para.add_run('رابط المقال الأصلي: ').bold = True
                link_para.add_run(article.get('link', 'غير متوفر'))
                link_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Add separator between articles
            if i < len(articles):
                doc.add_paragraph('-' * 50)
                doc.add_paragraph()  # Empty line
        
        # Add footer
        doc.add_paragraph()
        footer = doc.add_paragraph(f'تم إنشاء هذا التقرير في: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        return doc
    
    def format_date_arabic(self, date_str):
        """Format date in Arabic"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            arabic_months = [
                'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
            ]
            return f"{date_obj.day} {arabic_months[date_obj.month - 1]} {date_obj.year}"
        except:
            return date_str

# Initialize analyzer
analyzer = NewsAnalyzer('articles_combined.json')

@app.route('/')
def index():
    """Main page"""
    stats = analyzer.get_statistics()
    timeline_data = analyzer.get_timeline_data()
    return render_template('index.html', stats=stats, timeline_data=timeline_data)

@app.route('/search')
def search():
    """Search page"""
    return render_template('search.html')

@app.route('/headlines')
def headlines():
    """Headlines by date page"""
    return render_template('headlines.html')

@app.route('/api/search')
def api_search():
    """API endpoint for searching articles"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    content_type = request.args.get('content_type', 'all')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    results = analyzer.search_articles(query, search_type, content_type, date_from, date_to)
    
    # Pagination
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]
    
    return jsonify({
        'articles': paginated_results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/statistics')
def api_statistics():
    """API endpoint for statistics"""
    return jsonify(analyzer.get_statistics())

@app.route('/api/timeline')
def api_timeline():
    """API endpoint for timeline data"""
    return jsonify(analyzer.get_timeline_data())

@app.route('/api/keywords')
def api_keywords():
    """API endpoint for keyword analysis"""
    keywords = request.args.get('keywords', '').split(',')
    keywords = [k.strip() for k in keywords if k.strip()]
    if keywords:
        return jsonify(analyzer.get_keyword_analysis(keywords))
    return jsonify({})

@app.route('/api/headlines')
def api_headlines():
    """API endpoint for headlines by date"""
    date = request.args.get('date', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Filter articles by date
    filtered_articles = []
    for article in analyzer.articles:
        if article.get('date') == date:
            filtered_articles.append({
                'id': article.get('id'),
                'title': article.get('title'),
                'link': article.get('link'),
                'type': article.get('type'),
                'date': article.get('date')
            })
    
    # Pagination
    total = len(filtered_articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = filtered_articles[start:end]
    
    return jsonify({
        'articles': paginated_results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/article/<int:article_id>/content')
def api_article_content(article_id):
    """API endpoint to fetch full article content"""
    article = next((a for a in analyzer.articles if a.get('id') == article_id), None)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    article_url = article.get('link')
    if not article_url:
        return jsonify({'error': 'Article URL not found'}), 404
    
    content = analyzer.fetch_article_content(article_url)
    return jsonify({'content': content})

@app.route('/api/export/word')
def api_export_word():
    """API endpoint to export articles to Word document"""
    date = request.args.get('date', '')
    include_content = request.args.get('include_content', 'false').lower() == 'true'
    
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    # Get articles for the specified date
    articles = []
    for article in analyzer.articles:
        if article.get('date') == date:
            articles.append(article)
    
    if not articles:
        return jsonify({'error': 'No articles found for the specified date'}), 404
    
    try:
        # Create Word document
        doc = analyzer.create_word_document(articles, date, include_content)
        
        # Save to temporary file
        filename = f"palestine_news_{date.replace('-', '_')}.docx"
        temp_path = os.path.join('temp', filename)
        
        # Create temp directory if it doesn't exist
        os.makedirs('temp', exist_ok=True)
        
        doc.save(temp_path)
        
        return send_file(temp_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"Error creating Word document: {e}")
        return jsonify({'error': 'Failed to create Word document'}), 500

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Article detail page"""
    article = next((a for a in analyzer.articles if a.get('id') == article_id), None)
    if not article:
        return "Article not found", 404
    return render_template('article_detail.html', article=article)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
