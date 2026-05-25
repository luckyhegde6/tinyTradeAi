import requests
import xml.etree.ElementTree as ET
from config import NEWS_FEEDS
from utils.helpers import setup_logger

logger = setup_logger("NewsFetcher")

def fetch_rss_headlines():
    """Fetches and parses RSS feeds to extract recent headlines.
    Uses xml.etree to avoid heavy feedparser dependencies.
    """
    headlines = []
    
    for feed_url in NEWS_FEEDS:
        try:
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Simple RSS 2.0 parsing (finds all 'item' elements, gets 'title')
            # Only taking top 5 per feed to save memory
            count = 0
            for item in root.findall('.//item'):
                if count >= 5: break
                title_elem = item.find('title')
                if title_elem is not None and title_elem.text:
                    headlines.append({
                        "source": feed_url,
                        "headline": title_elem.text.strip()
                    })
                    count += 1
                    
        except Exception as e:
            logger.error("Error fetching RSS %s: %s" % (feed_url, e))
            
    return headlines
