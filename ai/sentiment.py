from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from database.db import insert_sentiment
from fetchers.news import fetch_rss_headlines
from utils.helpers import setup_logger

logger = setup_logger("SentimentAI")

# Initialize VADER analyzer once (lightweight)
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyzes sentiment using a combination of VADER and TextBlob.
    Returns a score between -1.0 (extremely bearish) and 1.0 (extremely bullish).
    """
    # VADER is great for financial/social media text (compound score is -1 to 1)
    vader_score = analyzer.polarity_scores(text)['compound']
    
    # TextBlob provides polarity (-1 to 1)
    blob_score = TextBlob(text).sentiment.polarity
    
    # Simple average
    final_score = (vader_score + blob_score) / 2.0
    
    if final_score > 0.15:
        label = "BULLISH"
    elif final_score < -0.15:
        label = "BEARISH"
    else:
        label = "NEUTRAL"
        
    return final_score, label

def process_news_sentiment():
    """Fetches latest news, analyzes sentiment, and stores it in DB."""
    logger.info("Processing news sentiment...")
    headlines = fetch_rss_headlines()
    
    for item in headlines:
        headline = item["headline"]
        source = item["source"]
        
        # In a real app, check if we already processed this exact headline
        score, label = analyze_sentiment(headline)
        
        insert_sentiment(source, headline, score, label)
        logger.info("Sentiment: %s (%.2f) - %s..." % (label, score, headline[:50]))
