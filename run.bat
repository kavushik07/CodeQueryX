@echo off
echo ========================================
echo GitHub Codebase RAG System
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo .env file not found. Running setup...
    echo.
    python setup_env.py
    echo.
)

REM Test setup
echo Testing setup...
python test_app.py
if errorlevel 1 (
    echo.
    echo Setup test failed. Please fix the errors above.
    pause
    exit /b 1
)

echo.
echo Starting Streamlit app...
echo.
streamlit run app.py
