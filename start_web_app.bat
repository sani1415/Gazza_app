@echo off
echo Starting Palestine News Web Application...
echo ================================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting web server...
echo The application will open in your browser automatically
echo Or visit: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.
python run_app.py
pause
