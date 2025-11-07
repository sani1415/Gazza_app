# 🌐 Palestine News Web Application

A beautiful, Arabic-supported web interface for researching the Palestine news dataset.

## ✨ Features

- **🔍 Advanced Search**: Search by keywords, content type, date range
- **📊 Visual Analytics**: Timeline charts and statistics
- **🎨 Beautiful UI**: Modern, responsive design with Arabic support
- **📱 Mobile Friendly**: Works perfectly on all devices
- **⚡ Fast Performance**: Optimized for 26,648+ articles
- **🌍 Arabic Support**: Full RTL support with proper Arabic fonts

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python run_app.py
```

### 3. Open Your Browser
The application will automatically open at: http://localhost:5000

## 📋 Manual Setup

If you prefer to run manually:

```bash
# Install Flask
pip install Flask

# Run the application
python app.py
```

Then visit: http://localhost:5000

## 🎯 How to Use

### **Home Page**
- View dataset statistics
- See timeline distribution
- Quick search with popular keywords
- Browse by content type

### **Search Page**
- **Text Search**: Enter keywords in Arabic or English
- **Content Type Filter**: Articles, Videos, Live Blogs, Episodes
- **Date Range**: Filter by specific time periods
- **Search Type**: Title only, content only, or both

### **Article Detail Page**
- Full article information
- Related articles
- Share and print options
- Direct link to original article

## 🔧 Technical Details

### **Backend**
- **Flask**: Web framework
- **JSON**: Data storage
- **Python**: Server-side logic

### **Frontend**
- **Bootstrap 5 RTL**: Responsive framework
- **Chart.js**: Data visualization
- **Arabic Fonts**: Noto Sans Arabic, Amiri
- **Custom CSS**: Beautiful animations and effects

### **Data Structure**
Each article contains:
- `id`: Unique identifier
- `title`: Article title in Arabic
- `excerpt`: Article summary
- `link`: Original URL
- `date`: Publication date
- `type`: Content type (post, video, liveblog, episode)
- `image_url`: Article image
- `source`: News source

## 📊 Search Capabilities

### **Keyword Search**
- Search in titles and content
- Arabic and English support
- Case-insensitive matching

### **Content Types**
- **مقالات (Posts)**: Regular news articles
- **فيديوهات (Videos)**: Video content
- **بث مباشر (Live Blogs)**: Live coverage
- **حلقات (Episodes)**: Program episodes

### **Date Filtering**
- Specific date ranges
- Monthly and yearly filtering
- Timeline visualization

## 🎨 UI Features

### **Responsive Design**
- Mobile-first approach
- Tablet and desktop optimized
- Touch-friendly interface

### **Arabic Support**
- RTL (Right-to-Left) layout
- Proper Arabic fonts
- Cultural design elements

### **Visual Elements**
- Gradient backgrounds
- Smooth animations
- Card-based layout
- Interactive charts

## 🔍 Research Applications

### **Academic Research**
- Media coverage analysis
- Timeline studies
- Content analysis
- Comparative research

### **Journalism**
- Fact-checking
- Source verification
- Historical context
- Story development

### **Policy Analysis**
- Event tracking
- Coverage trends
- Public discourse analysis
- Impact assessment

## 🛠️ Customization

### **Adding New Features**
1. Modify `app.py` for backend logic
2. Update templates for UI changes
3. Add CSS in `static/style.css`
4. Extend JavaScript in templates

### **Data Updates**
1. Replace `articles_combined.json`
2. Restart the application
3. New data will be automatically loaded

## 📱 Mobile Usage

The application is fully responsive and works great on:
- 📱 Smartphones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktop computers

## 🌟 Pro Tips

1. **Use Arabic keywords** for better search results
2. **Filter by content type** to focus your research
3. **Use date ranges** to study specific periods
4. **Check related articles** for deeper insights
5. **Export data** for external analysis

## 🚨 Troubleshooting

### **Common Issues**

**App won't start:**
- Check if `articles_combined.json` exists
- Install Flask: `pip install Flask`
- Check Python version (3.7+)

**Search not working:**
- Check internet connection
- Clear browser cache
- Try different keywords

**Arabic text not displaying:**
- Check browser font support
- Clear browser cache
- Try different browser

## 📞 Support

If you encounter any issues:
1. Check the console for error messages
2. Verify all files are in the correct location
3. Ensure Python and Flask are properly installed
4. Check browser compatibility

## 🎉 Enjoy Your Research!

This web application provides a powerful interface for exploring your comprehensive Palestine news dataset. Use it to uncover insights, track trends, and conduct thorough research on this important historical archive.

**Happy researching! 🔍📰**
