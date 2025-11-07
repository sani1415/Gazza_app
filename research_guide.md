# 🔬 Palestine News Dataset Research Guide

## 📊 Your Dataset Overview
- **Total Articles**: 26,648 unique articles
- **Time Period**: October 2023 - September 2025
- **File Size**: 25.9 MB (articles_combined.json)
- **Perfect Data**: 100% complete dates, excerpts, and images

## 🎯 Research Ideas & Methods

### 1. **Timeline Analysis**
```python
# Find peak activity periods
# Analyze coverage during specific events
# Track story evolution over time
```

**Research Questions:**
- Which months had the most coverage?
- How did coverage change during major events?
- What were the quietest periods?

### 2. **Content Theme Analysis**
```python
# Search for specific keywords
# Analyze recurring topics
# Track theme frequency over time
```

**Key Arabic Keywords to Search:**
- غزة (Gaza)
- الضفة (West Bank) 
- القدس (Jerusalem)
- حماس (Hamas)
- إسرائيل (Israel)
- الاحتلال (Occupation)
- شهداء (Martyrs)
- قصف (Bombing)
- مفاوضات (Negotiations)
- أسرى (Prisoners)

### 3. **Content Type Analysis**
- **Videos**: 2,530 articles (9.5%)
- **Live Blogs**: 676 articles (2.5%)
- **Episodes**: 426 articles (1.6%)
- **Regular Posts**: 23,016 articles (86.4%)

### 4. **Specific Event Analysis**
**Major Events to Research:**
- October 7, 2023 (Al-Aqsa Flood)
- Ramadan 2024
- Summer 2024 escalation
- Recent developments (2025)

## 🛠️ Practical Research Tools

### **Method 1: Simple Text Search**
```bash
# Search for specific terms in the JSON file
grep -i "غزة" articles_combined.json | wc -l
grep -i "مفاوضات" articles_combined.json | wc -l
```

### **Method 2: Python Analysis**
```python
import json

# Load the data
with open('articles_combined.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

# Search for specific topics
gaza_articles = [a for a in articles if 'غزة' in a.get('title', '')]
print(f"Articles about Gaza: {len(gaza_articles)}")

# Get articles from specific period
oct_2023 = [a for a in articles if a.get('date', '').startswith('2023-10')]
print(f"October 2023 articles: {len(oct_2023)}")
```

### **Method 3: Excel/CSV Analysis**
1. Convert JSON to CSV
2. Use Excel filters and pivot tables
3. Create charts and visualizations

## 📈 Research Applications

### **Academic Research**
- Media coverage analysis
- Timeline of events
- Content sentiment analysis
- Comparative studies

### **Journalism**
- Fact-checking and verification
- Story development
- Historical context
- Source material

### **Policy Analysis**
- Event impact assessment
- Coverage trends
- Public discourse analysis
- Timeline reconstruction

## 🔍 Specific Research Examples

### **Example 1: Coverage During Major Events**
```python
# Find all articles from October 7-14, 2023
oct_7_articles = [a for a in articles 
                 if '2023-10-0' in a.get('date', '')]
```

### **Example 2: Video Content Analysis**
```python
# Get all video articles
videos = [a for a in articles if a.get('type') == 'video']
# Analyze video topics
video_titles = [v.get('title') for v in videos]
```

### **Example 3: Live Blog Coverage**
```python
# Get live blog entries
liveblogs = [a for a in articles if a.get('type') == 'liveblog']
# Find most active live blog days
```

## 📊 Data Export Options

### **Export Specific Subsets:**
- All video articles
- Articles from specific time periods
- Articles containing specific keywords
- Live blog entries only

### **Export Formats:**
- JSON (original format)
- CSV (for Excel analysis)
- TXT (for text analysis tools)

## 🎯 Recommended Research Workflow

1. **Start with broad analysis** (timeline, content types)
2. **Focus on specific topics** (keywords, themes)
3. **Deep dive into events** (date ranges, live coverage)
4. **Export subsets** for detailed analysis
5. **Use external tools** (Excel, Python, R) for advanced analysis

## 💡 Pro Tips

- **Use Arabic text search** for better results
- **Combine multiple keywords** for complex queries
- **Export data regularly** to avoid re-processing
- **Focus on specific time periods** for detailed analysis
- **Use the date field** for chronological analysis

## 🚀 Next Steps

1. Choose your research focus
2. Use the provided tools
3. Export relevant data subsets
4. Apply your preferred analysis methods
5. Share your findings!

Your dataset is a goldmine of information - use it wisely! 🎯
