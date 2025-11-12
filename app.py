#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Palestine News Research Web Application
Beautiful web interface for researching the Palestine news dataset
"""

import io
import json
import re
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import os
import requests
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Optional, Tuple

from PIL import Image
from bs4 import BeautifulSoup

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

IMAGES_CACHE_DIR = Path("images_cache")
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

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

    def get_articles_with_images(self, date=None):
        """Return articles that include images, optionally filtered by date"""
        articles_with_images = [
            article for article in self.articles
            if article.get('image_url')
        ]

        if date:
            articles_with_images = [
                article for article in articles_with_images
                if article.get('date') == date
            ]

        # Sort by date (newest first), then by id descending as tie-breaker
        articles_with_images.sort(
            key=lambda article: (
                article.get('date') or '0000-00-00',
                article.get('id') or 0
            ),
            reverse=True
        )

        return articles_with_images
    
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


@app.route('/images')
def images():
    """Images gallery page"""
    return render_template('images.html')


@app.route('/tools')
def tools():
    """Tools page"""
    return render_template('tools.html')

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


@app.route('/api/images')
def api_images():
    """API endpoint for articles that include images"""
    date = request.args.get('date', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 24))

    # Limit per_page to avoid overly large responses
    per_page = min(max(per_page, 1), 60)

    articles_with_images = analyzer.get_articles_with_images(date or None)

    total = len(articles_with_images)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles_with_images[start:end]

    response_articles = [
        {
            'id': article.get('id'),
            'title': article.get('title'),
            'date': article.get('date'),
            'type': article.get('type'),
            'image_url': article.get('image_url'),
            'link': article.get('link'),
            'excerpt': article.get('excerpt'),
        }
        for article in paginated_articles
    ]

    return jsonify({
        'articles': response_articles,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/api/tools/download-images', methods=['POST'])
def api_download_images():
    data = request.get_json() or {}
    date = data.get('date')
    limit = data.get('limit')
    force = data.get('force', False)

    try:
        limit = int(limit) if limit is not None else None
    except (ValueError, TypeError):
        limit = None

    result = download_images(date=date or None, limit=limit, force=bool(force))

    return jsonify({
        'success': True,
        'requested': result['requested'],
        'downloaded': result['downloaded'],
        'skipped': result['skipped'],
        'errors': result['errors'],
        'output_dir': str(IMAGES_CACHE_DIR.resolve())
    })


def build_image_path(article, output_dir: Path) -> Path:
    image_url = article.get('image_url', '')
    parsed = urlparse(image_url)
    basename = Path(unquote(parsed.path)).name or f"article_{article.get('id', 'unknown')}"
    stem, ext = os.path.splitext(basename)
    if not ext:
        ext = '.jpg'

    article_date = (article.get('date') or 'unknown_date').replace('/', '-').strip()
    target_dir = output_dir / article_date
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{article.get('id', 'article')}_{stem}{ext}"
    return target_dir / filename


def ensure_image_file(article) -> Optional[Path]:
    """Ensure the article image exists locally and return its path."""
    image_url = article.get('image_url')
    if not image_url:
        return None

    destination = build_image_path(article, IMAGES_CACHE_DIR)

    if destination.exists():
        return destination

    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
        return destination
    except requests.RequestException as exc:
        print(f"Failed to download image {image_url}: {exc}")
        return None


def prepare_image_stream(image_path: Path, max_width: int = 1200, max_height: int = 1200,
                         quality: int = 80) -> Optional[io.BytesIO]:
    """Resize/compress image and return BytesIO stream ready for docx embedding."""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img.thumbnail((max_width, max_height), Image.LANCZOS)
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            return output
    except Exception as exc:
        print(f"Failed to process image {image_path}: {exc}")
        return None


def fetch_article_content_formatted(article) -> str:
    """Fetch and format full article content; fallback to excerpt if download fails."""
    link = article.get('link')
    if not link:
        return ''

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(link, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        selectors = [
            '.wysiwyg--all-content',
            '.article-body',
            '.post-content',
            'article .content',
            '.entry-content',
        ]

        article_content = None
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                article_content = node
                break

        if not article_content:
            fallback = soup.find_all('div', string=lambda text: text and len(text.strip()) > 200)
            if fallback:
                article_content = fallback[0]

        if not article_content:
            return ''

        for unwanted in article_content.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            unwanted.decompose()

        for link_node in article_content.find_all('a'):
            link_node.replace_with(link_node.get_text())

        text = article_content.get_text(separator=' \n ', strip=True)
        text = re.sub(r'\s+', ' ', text)

        paragraph_candidates = re.split(r'([.!؟]\s+)', text)
        paragraphs, buffer = [], []
        for part in paragraph_candidates:
            if part.strip():
                buffer.append(part)
                if part.strip().endswith(tuple('.!؟')) and len(buffer) >= 2:
                    paragraphs.append(''.join(buffer).strip())
                    buffer = []
        if buffer:
            paragraphs.append(''.join(buffer).strip())

        if not paragraphs:
            paragraphs = [text]

        return '\n\n'.join(paragraphs)
    except requests.RequestException as exc:
        print(f"Network error while fetching article content {link}: {exc}")
        return ''
    except Exception as exc:
        print(f"Parsing error while fetching article content {link}: {exc}")
        return ''


def download_images(date=None, limit=None, force=False):
    articles = analyzer.get_articles_with_images(date)

    downloaded = 0
    skipped = 0
    errors = 0

    for article in articles:
        if limit and downloaded >= limit:
            break

        destination = build_image_path(article, IMAGES_CACHE_DIR)
        image_url = article.get('image_url')

        if destination.exists() and not force:
            skipped += 1
            continue

        try:
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()
            destination.write_bytes(response.content)
            downloaded += 1
        except requests.RequestException as exc:
            errors += 1
            print(f"Error downloading image {image_url}: {exc}")

    return {
        'requested': len(articles),
        'downloaded': downloaded,
        'skipped': skipped,
        'errors': errors
    }


def create_headline_only_document(date):
    articles = [
        article for article in analyzer.articles
        if article.get('date') == date
    ]

    if not articles:
        return None, None

    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Inches(0.12)

    title = doc.add_heading(f'أخبار فلسطين - {analyzer.format_date_arabic(date)}', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    for article in articles:
        heading = doc.add_heading(article.get('title', 'بدون عنوان'), level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        link_para = doc.add_paragraph()
        link_para.add_run('رابط المقال: ').bold = True
        link_para.add_run(article.get('link', 'غير متوفر'))
        link_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        content = analyzer.fetch_article_content(article.get('link')) if article.get('link') else ''
        if content and not content.startswith('عذراً'):
            for paragraph in content.split('\n'):
                paragraph = paragraph.strip()
                if paragraph:
                    para = doc.add_paragraph(paragraph)
                    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    para.paragraph_format.keep_together = True
        else:
            missing_para = doc.add_paragraph('تعذر تحميل المحتوى الكامل للمقال.')
            missing_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        doc.add_paragraph('-' * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()

    footer = doc.add_paragraph(f'تم إنشاء هذا التقرير في: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    filename = f"palestine_news_headline_only_{date.replace('-', '_')}_{int(time.time())}.docx"
    filepath = TEMP_DIR / filename
    doc.save(filepath)

    return filepath, filename


def create_document_with_images(date: str, include_content: bool = True) -> Tuple[Optional[Path], Optional[str]]:
    articles = [
        article for article in analyzer.articles
        if article.get('date') == date
    ]

    if not articles:
        return None, None

    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Inches(0.12)

    title = doc.add_heading(f'أخبار فلسطين - {analyzer.format_date_arabic(date)}', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Track image files to clean up after document creation
    used_image_paths = []

    for idx, article in enumerate(articles, start=1):
        heading = doc.add_heading(article.get('title', 'بدون عنوان'), level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        image_path = ensure_image_file(article)
        if image_path and image_path.exists():
            try:
                resized_stream = prepare_image_stream(image_path)
                if resized_stream:
                    doc.add_picture(resized_stream, width=Inches(5.5))
                else:
                    doc.add_picture(str(image_path), width=Inches(5.5))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                # Track this image for cleanup
                used_image_paths.append(image_path)
            except Exception as exc:
                print(f"Failed to insert image {image_path}: {exc}")

        if article.get('link'):
            cleaned_url = unquote(article['link'])
            link_para = doc.add_paragraph()
            link_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = link_para.add_run(cleaned_url)
            run.font.size = Inches(0.11)

        content_text = ''
        if include_content:
            content_text = fetch_article_content_formatted(article)
            if not content_text and article.get('excerpt'):
                content_text = article.get('excerpt')
        else:
            content_text = article.get('excerpt') or ''

        if not content_text:
            content_text = 'عذراً، تعذر تحميل المحتوى الكامل للمقال.'

        for paragraph in content_text.split('\n'):
            cleaned = paragraph.strip()
            if not cleaned:
                continue
            para = doc.add_paragraph(cleaned)
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            para.paragraph_format.keep_together = True

        if idx != len(articles):
            doc.add_paragraph('-' * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()
 
    footer = doc.add_paragraph(f'تم إنشاء هذا التقرير في: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
 
    # Use simpler filename format (matching other exports)
    filename = f"palestine_news_with_images_{date.replace('-', '_')}.docx"
    filepath = TEMP_DIR / filename
    doc.save(filepath)

    # Clean up cached images after embedding (Option 2)
    for image_path in used_image_paths:
        try:
            if image_path.exists():
                image_path.unlink()
                print(f"Cleaned up cached image: {image_path}")
        except Exception as exc:
            print(f"Failed to delete cached image {image_path}: {exc}")

    return filepath, filename


@app.route('/api/export/headline-only')
def api_export_headline_only():
    date = request.args.get('date', '').strip()

    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    filepath, filename = create_headline_only_document(date)

    if not filepath:
        return jsonify({'error': 'No articles found for the specified date'}), 404

    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route('/api/export/word-with-images')
def api_export_with_images():
    date = request.args.get('date', '').strip()
    include_content = request.args.get('include_content', 'true').lower() != 'false'

    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    filepath, filename = create_document_with_images(date, include_content)

    if not filepath:
        return jsonify({'error': 'No articles found for the specified date'}), 404

    return send_file(filepath, as_attachment=True, download_name=filename)

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
