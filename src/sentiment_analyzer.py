from textblob import TextBlob
import nltk
import os

class SentimentAnalyzer:
    def __init__(self):
        # Download necessary NLTK data if not already downloaded
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        self.sia = SentimentIntensityAnalyzer()
        
    def analyze_short_term(self, text):
        """
        Analyze the sentiment of a single message (short-term sentiment)
        Returns a value between -1 (very negative) and 1 (very positive)
        """
        # Using VADER for short-term sentiment analysis
        sentiment_scores = self.sia.polarity_scores(text)
        return sentiment_scores['compound']
    
    def analyze_long_term(self, messages, window_size=10):
        """
        Analyze the sentiment over multiple messages (long-term sentiment)
        Takes a list of messages and returns a value between -1 and 1
        """
        if not messages:
            return 0.0
        
        # Take the most recent messages up to window_size
        recent_messages = messages[-window_size:] if len(messages) > window_size else messages
        
        # Calculate weighted average of sentiment scores (more recent = higher weight)
        total_weight = 0
        weighted_sum = 0
        
        for i, message in enumerate(recent_messages):
            weight = i + 1  # More recent messages get higher weights
            score = self.analyze_short_term(message)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0