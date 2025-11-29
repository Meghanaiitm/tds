import html
from playwright.sync_api import sync_playwright
from markdownify import markdownify as md

def fetch_page_content(url):
    """
    Launches a headless browser, renders the JS, and returns 
    markdown text of the page.
    """
    try:
        with sync_playwright() as p:
            # CRITICAL FIX FOR RENDER: Add these args
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = browser.new_page()
            
            # Navigate
            print(f"👀 Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Get content
            content_html = page.content()
            
            # Convert to Markdown for better LLM readability
            markdown = md(content_html)
            
            browser.close()
            return markdown
            
    except Exception as e:
        print(f"Browser Error: {e}")
        return f"Error fetching page: {str(e)}"