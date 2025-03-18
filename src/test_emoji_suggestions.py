import os
import json
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time

from sentiment_analyzer import SentimentAnalyzer
from emoji_suggester import EmojiSuggester
from chat_processor import ChatProcessor

class EmojiSuggestionTester:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emoji_suggester = EmojiSuggester()
        self.chat_processor = ChatProcessor()
        
        # Create data directory if it doesn't exist
        self.test_data_dir = os.path.join('d:', 'CODES', 'Projects', 'Emoji', 'data', 'test_data')
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Create default sentiment config if it doesn't exist
        config_path = os.path.join('d:', 'CODES', 'Projects', 'Emoji', 'data', 'sentiment_config.json')
        if not os.path.exists(config_path):
            # Create default sentiment config
            default_config = {
                "thresholds": {
                    "very_positive": 0.6,
                    "positive": 0.3,
                    "slightly_positive": 0.1,
                    "neutral_upper": 0.1,
                    "neutral_lower": -0.1,
                    "slightly_negative": -0.1,
                    "negative": -0.3,
                    "very_negative": -0.6
                },
                "weights": {
                    "short_term": 0.6,
                    "long_term": 0.3,
                    "context": 0.1
                },
                "analysis": {
                    "short_term_window": 1,
                    "long_term_window": 10,
                    "context_window": 20
                }
            }
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Save the default config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default sentiment config at {config_path}")
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Initialize results storage
        self.results = []
    
    def scrape_conversations(self, num_conversations=20):
        """Scrape sample conversations from various sources"""
        conversations = []
        
        # Sources to scrape conversation examples
        sources = [
            {
                'url': 'https://www.fluentu.com/blog/english/english-conversation-topics/',
                'selector': 'div.post-content p'
            },
            {
                'url': 'https://www.eslfast.com/robot/topics/daily/daily.htm',
                'selector': 'p'
            },
            {
                'url': 'https://www.englishclub.com/speaking/small-talk-topics.htm',
                'selector': 'div.ec-content p'
            }
        ]
        
        print("Scraping conversation data...")
        
        for source in sources:
            try:
                response = requests.get(source['url'], timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = soup.select(source['selector'])
                    
                    # Extract text from paragraphs
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if len(text) > 50 and '?' in text and '.' in text:  # Basic filtering for conversation-like text
                            # Split into sentences
                            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 0]
                            
                            if len(sentences) >= 2:
                                # Create a conversation with alternating speakers
                                conversation = []
                                for i, sentence in enumerate(sentences[:10]):  # Limit to 10 sentences per conversation
                                    speaker = "User 1" if i % 2 == 0 else "User 2"
                                    conversation.append({"speaker": speaker, "message": sentence})
                                
                                if len(conversation) >= 2:
                                    conversations.append(conversation)
            except Exception as e:
                print(f"Error scraping {source['url']}: {e}")
        
        # If we couldn't scrape enough conversations, generate some synthetic ones
        if len(conversations) < num_conversations:
            synthetic_count = num_conversations - len(conversations)
            print(f"Generating {synthetic_count} synthetic conversations...")
            
            # Sample messages for synthetic conversations
            positive_messages = [
                "That's wonderful news!", "I'm so happy for you!", "Great job on the project!",
                "I love this idea!", "This makes me so excited!", "You're doing amazing work!",
                "I'm really impressed with your progress!", "This is exactly what we needed!",
                "I'm looking forward to our next meeting!", "Your help has been invaluable!"
            ]
            
            neutral_messages = [
                "I see what you mean.", "Let me think about that.", "That's interesting.",
                "I'm not sure yet.", "We should consider all options.", "What do you think?",
                "Let's discuss this further.", "I need more information.", "That's a possibility.",
                "I'll get back to you on that."
            ]
            
            negative_messages = [
                "I'm disappointed with the results.", "This isn't what I expected.",
                "We need to fix these issues.", "I'm concerned about the timeline.",
                "This approach has serious problems.", "I disagree with your assessment.",
                "The quality is below our standards.", "I'm frustrated with the lack of progress.",
                "This creates more problems than it solves.", "We're facing significant challenges."
            ]
            
            for _ in range(synthetic_count):
                sentiment_type = random.choice(["positive", "neutral", "negative", "mixed"])
                conversation = []
                
                for i in range(random.randint(4, 8)):
                    speaker = "User 1" if i % 2 == 0 else "User 2"
                    
                    if sentiment_type == "positive":
                        message = random.choice(positive_messages)
                    elif sentiment_type == "negative":
                        message = random.choice(negative_messages)
                    elif sentiment_type == "neutral":
                        message = random.choice(neutral_messages)
                    else:  # mixed
                        if speaker == "User 1":
                            message = random.choice(positive_messages)
                        else:
                            message = random.choice(negative_messages)
                    
                    conversation.append({"speaker": speaker, "message": message})
                
                conversations.append(conversation)
        
        # Save conversations to file
        conversations_file = os.path.join(self.test_data_dir, 'test_conversations.json')
        with open(conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations[:num_conversations], f, indent=2)
        
        print(f"Saved {len(conversations[:num_conversations])} conversations to {conversations_file}")
        return conversations[:num_conversations]
    
    def load_conversations(self):
        """Load previously scraped conversations if available"""
        conversations_file = os.path.join(self.test_data_dir, 'test_conversations.json')
        if os.path.exists(conversations_file):
            with open(conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            print(f"Loaded {len(conversations)} conversations from {conversations_file}")
            return conversations
        else:
            return self.scrape_conversations()
    
    def test_emoji_suggestions(self):
        """Test emoji suggestions on the conversations"""
        conversations = self.load_conversations()
        
        print("Testing emoji suggestions...")
        
        for conversation_idx, conversation in enumerate(tqdm(conversations)):
            # Reset chat processor for each conversation
            self.chat_processor = ChatProcessor()
            
            # Process each message in the conversation
            for msg_idx, msg_data in enumerate(conversation):
                speaker = msg_data["speaker"]
                message = msg_data["message"]
                
                # Add message to chat processor
                self.chat_processor.add_message(speaker, message)
                
                # Only analyze messages from User 2 (as per your app logic)
                if speaker == "User 2":
                    # Get messages from User 2
                    user2_messages = self.chat_processor.get_recent_messages("User 2")
                    
                    # Calculate sentiments
                    short_term_sentiment = self.sentiment_analyzer.analyze_short_term(message)
                    long_term_sentiment = self.sentiment_analyzer.analyze_long_term(user2_messages)
                    
                    # Get emoji suggestions
                    suggested_emojis = self.emoji_suggester.suggest(short_term_sentiment, long_term_sentiment)
                    
                    # Store results
                    self.results.append({
                        "conversation_id": conversation_idx,
                        "message_id": msg_idx,
                        "message": message,
                        "short_term_sentiment": short_term_sentiment,
                        "long_term_sentiment": long_term_sentiment,
                        "suggested_emojis": suggested_emojis,
                        # Categorize sentiment for evaluation
                        "sentiment_category": self._categorize_sentiment(short_term_sentiment)
                    })
        
        # Save results
        results_file = os.path.join(self.test_data_dir, 'test_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Saved {len(self.results)} test results to {results_file}")
        return self.results
    
    def _categorize_sentiment(self, sentiment_score):
        """Categorize sentiment score into discrete categories"""
        thresholds = self.config["thresholds"]
        
        if sentiment_score >= thresholds["very_positive"]:
            return "very_positive"
        elif sentiment_score >= thresholds["positive"]:
            return "positive"
        elif sentiment_score >= thresholds["slightly_positive"]:
            return "slightly_positive"
        elif sentiment_score > thresholds["neutral_lower"]:
            return "neutral"
        elif sentiment_score > thresholds["negative"]:
            return "slightly_negative"
        elif sentiment_score > thresholds["very_negative"]:
            return "negative"
        else:
            return "very_negative"

if __name__ == "__main__":
    tester = EmojiSuggestionTester()
    results = tester.test_emoji_suggestions()
    print(f"Testing complete. Processed {len(results)} messages.")