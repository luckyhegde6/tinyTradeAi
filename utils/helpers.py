import logging

def setup_logger(name):
    """Sets up a standardized logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

def format_price(price):
    """Formats a price string appropriately."""
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:.2f}"
    else:
        return f"{price:.4f}"
