import re
from typing import Optional


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_email(text: str) -> Optional[str]:
    """Extract email from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def clean_price(price_str: str) -> Optional[float]:
    """Clean and convert price string to float"""
    if not price_str:
        return None
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[$,]', '', str(price_str))
    
    try:
        return float(cleaned)
    except:
        return None
