
import re

BAD_WORDS = {
    'damn', 'hell', 'stupid', 'idiot', 'trash', 'scam', 'fuck', 'shit', 'bitch', 'asshole'
}

def contains_profanity(text):
    if not text:
        return False
    
    # Convert to lowercase
    text_lower = text.lower()
    
    # Check for words, handling punctuation
    # \b matches word boundaries
    for word in BAD_WORDS:
        # Use regex to find the word as a whole word, ignoring punctuation around it
        # This will match "fuck!", "fuck.", "fuck?" etc.
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            return True
            
    return False
