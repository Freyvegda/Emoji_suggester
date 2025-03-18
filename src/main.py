import tkinter as tk
from tkinter import scrolledtext
import emoji
from sentiment_analyzer import SentimentAnalyzer
from emoji_suggester import EmojiSuggester
from chat_processor import ChatProcessor

class EmojiSuggestionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emoji Suggestion App")
        self.root.geometry("600x500")
        
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emoji_suggester = EmojiSuggester()
        self.chat_processor = ChatProcessor()
        
        # Current users
        self.current_user = "User 1"
        self.second_user = "User 2"
        
        # Create UI elements
        self.create_widgets()
        
        # Initialize chat display with default messages
        self.initialize_chat_display()
        
        # Show initial emoji suggestions
        self.update_emoji_suggestions()
        
    def create_widgets(self):
        # Chat display area
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, height=15)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.message_input = tk.Entry(self.input_frame, width=50)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_input.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # User switch and emoji suggestion area
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.switch_user_button = tk.Button(self.control_frame, text="Switch User", command=self.switch_user)
        self.switch_user_button.pack(side=tk.LEFT, padx=5)
        
        self.current_user_label = tk.Label(self.control_frame, text=f"Current: {self.current_user}")
        self.current_user_label.pack(side=tk.LEFT, padx=5)
        
        self.emoji_label = tk.Label(self.control_frame, text="Suggested Emojis:")
        self.emoji_label.pack(side=tk.LEFT, padx=20)
        
        # Replace the emoji suggestions label with a frame containing emoji buttons
        self.emoji_suggestions_frame = tk.Frame(self.control_frame)
        self.emoji_suggestions_frame.pack(side=tk.LEFT, padx=5)
        
        # Initial emoji buttons (will be updated later)
        self.emoji_buttons = []
    
    def initialize_chat_display(self):
        """Initialize chat display with default messages from chat processor"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        
        # Display default messages from chat processor
        for user, messages in self.chat_processor.messages.items():
            for message in messages:
                self.chat_display.insert(tk.END, f"{user}: {message}\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def update_emoji_suggestions(self):
        """Update emoji suggestions based on the other user's messages"""
        # Get messages from the other user (not current user)
        other_user_messages = self.chat_processor.get_recent_messages(self.second_user)
        
        # Clear existing emoji buttons
        for button in self.emoji_buttons:
            button.destroy()
        self.emoji_buttons = []
        
        if other_user_messages:
            # Get the most recent message for short-term sentiment
            short_term_sentiment = self.sentiment_analyzer.analyze_short_term(other_user_messages[-1])
            # Get long-term sentiment from all recent messages
            long_term_sentiment = self.sentiment_analyzer.analyze_long_term(other_user_messages)
            
            # Get emoji suggestions
            suggested_emojis = self.emoji_suggester.suggest(short_term_sentiment, long_term_sentiment)
            emojis_list = suggested_emojis.split()
        else:
            # If no messages yet, show neutral emojis
            emojis_list = ["🙂", "👋", "👀"]
        
        # Create clickable buttons for each emoji
        for emoji_char in emojis_list:
            button = tk.Button(
                self.emoji_suggestions_frame, 
                text=emoji_char, 
                font=("Arial", 14),
                command=lambda e=emoji_char: self.insert_emoji(e),
                width=2, height=1
            )
            button.pack(side=tk.LEFT, padx=2)
            self.emoji_buttons.append(button)
    
    def insert_emoji(self, emoji_char):
        """Insert the selected emoji into the message input field"""
        current_text = self.message_input.get()
        cursor_position = self.message_input.index(tk.INSERT)
        
        # Insert emoji at cursor position
        new_text = current_text[:cursor_position] + emoji_char + current_text[cursor_position:]
        
        # Update input field
        self.message_input.delete(0, tk.END)
        self.message_input.insert(0, new_text)
        
        # Move cursor after the inserted emoji
        self.message_input.icursor(cursor_position + len(emoji_char))
        self.message_input.focus()
        
    def send_message(self, event=None):
        message = self.message_input.get().strip()
        if not message:
            return
        
        # Add message to chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{self.current_user}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Process the message
        self.chat_processor.add_message(self.current_user, message)
        
        # Always update emoji suggestions after any message
        self.update_emoji_suggestions()
        
        self.message_input.delete(0, tk.END)
        
    def switch_user(self):
        if self.current_user == "User 1":
            self.current_user = "User 2"
            self.second_user = "User 1"
        else:
            self.current_user = "User 1"
            self.second_user = "User 2"
        
        self.current_user_label.config(text=f"Current: {self.current_user}")
        
        # Always update emoji suggestions when switching users
        self.update_emoji_suggestions()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmojiSuggestionApp(root)
    root.mainloop()