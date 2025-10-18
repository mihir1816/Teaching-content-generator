"""
Web article scraping and processing service using LangChain WebBaseLoader.
"""
from langchain_community.document_loaders import WebBaseLoader
from app.config import cfg
import logging

logger = logging.getLogger(__name__)

def get_article_text(url: str) -> dict:
    """
    Fetch and extract main content from a web article URL.
    
    Args:
        url: Article URL to scrape
        
    Returns:
        dict with keys:
            - title: str (from metadata or first heading)
            - text: str (main content)
            - url: str (source URL)
            - lang: str (default 'en')
    """
    try:
        # Initialize WebBaseLoader
        loader = WebBaseLoader(
            web_paths=[url],
            header_template={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        # Load documents - FIX: Call the method with ()
        docs = loader.load()
        
        if not docs or not docs[0].page_content.strip():
            raise ValueError("No content extracted from URL")
        
        doc = docs[0]
        
        # Extract metadata
        title = doc.metadata.get("title", "")
        if not title and doc.page_content:
            # Fallback: use first line as title
            lines = doc.page_content.split('\n')
            first_line = lines[0].strip() if lines else ""
            title = first_line[:100] if len(first_line) > 100 else first_line
        
        # Clean the text content
        text_content = doc.page_content.strip()
        
        return {
            "title": title or "Untitled Article",
            "text": text_content,
            "url": url,
            "lang": "en"  # Default; can add langdetect later if needed
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch article from {url}: {str(e)}")
        raise ValueError(f"Could not fetch article: {str(e)}")