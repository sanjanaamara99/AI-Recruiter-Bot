@echo off
echo ================================================
echo   Starting Autonomous AI Interviewer Frontend
echo ================================================
echo.
echo Make sure the Flask backend is running first!
echo If not, start it in another terminal:
echo     python app.py
echo.
echo Starting Streamlit frontend...
echo.

streamlit run streamlit_app.py

pause
