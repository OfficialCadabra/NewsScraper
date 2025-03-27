@echo off
REM Activate the virtual environment
call %~dp0venv\Scripts\activate.bat

REM Get the command-line arguments
set params=%*

if "%1"=="scrape" (
    python %~dp0news_manager.py %params%
) else if "%1"=="browse" (
    python %~dp0browse_articles.py %params:~7%
) else if "%1"=="process" (
    python %~dp0process_articles.py %params:~8%
) else (
    echo Financial News Manager
    echo ====================
    echo.
    echo Available commands:
    echo.
    echo scrape [ticker] --days [days]    - Scrape and store news for a ticker
    echo browse list [ticker]             - List articles for a ticker
    echo browse search [query]            - Search for articles
    echo browse view --id [id]            - View a specific article
    echo browse stats [ticker]            - Show statistics for a ticker
    echo process [csv_file] [ticker]      - Process articles from a CSV file
)

REM Keep the window open
pause
