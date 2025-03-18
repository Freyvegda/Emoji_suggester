import emoji
import random

class EmojiSuggester:
    def __init__(self):
        # Define emoji categories based on sentiment
        self.positive_emojis = [
            "😊", "😄", "😁", "😃", "😀", "🙂", "😍", "🥰", "😘", "👍", 
            "🎉", "✨", "🌟", "💯", "🔥", "👏", "🤩", "😎", "🌈", "💪"
        ]
        
        self.neutral_emojis = [
            "😐", "🤔", "🙄", "😶", "😑", "🤷", "👀", "💭", "🧐", "🤨",
            "📝", "🗒️", "📊", "🔍", "⏱️", "📌", "🔄", "🔔", "📱", "💻"
        ]
        
        self.negative_emojis = [
            "😕", "😟", "😔", "😞", "😢", "😭", "😠", "😡", "😤", "👎",
            "💔", "😓", "😥", "😰", "😨", "😱", "😖", "😣", "😩", "😫"
        ]
        
        # Special categories for mixed sentiments
        self.mixed_emojis = [
            "😅", "😬", "😏", "🙃", "😌", "🤐", "😒", "🤥", "😪", "😴",
            "🤞", "🤝", "🙏", "💆", "🧘", "💅", "🤦", "🤷", "🙇", "🤯"
        ]
    
    def suggest(self, short_term_sentiment, long_term_sentiment, num_suggestions=3):
        """
        Suggest emojis based on short-term and long-term sentiment values
        Returns a string of suggested emojis
        """
        # Determine primary emoji category based on short-term sentiment
        if short_term_sentiment > 0.3:
            primary_category = self.positive_emojis
        elif short_term_sentiment < -0.3:
            primary_category = self.negative_emojis
        else:
            primary_category = self.neutral_emojis
        
        # Determine secondary category based on long-term sentiment
        if long_term_sentiment > 0.3:
            secondary_category = self.positive_emojis
        elif long_term_sentiment < -0.3:
            secondary_category = self.negative_emojis
        else:
            secondary_category = self.neutral_emojis
        
        # If short and long term sentiments differ significantly, add mixed emojis
        if abs(short_term_sentiment - long_term_sentiment) > 0.5:
            tertiary_category = self.mixed_emojis
        else:
            tertiary_category = primary_category
        
        # Select emojis with weighted probability
        suggestions = []
        
        # 60% chance from primary category (short-term)
        if random.random() < 0.6 and primary_category:
            suggestions.append(random.choice(primary_category))
        
        # 30% chance from secondary category (long-term)
        if random.random() < 0.3 and secondary_category:
            suggestions.append(random.choice(secondary_category))
        
        # 10% chance from tertiary category (mixed or primary)
        if random.random() < 0.1 and tertiary_category:
            suggestions.append(random.choice(tertiary_category))
        
        # Fill remaining slots if needed
        while len(suggestions) < num_suggestions:
            category = random.choices(
                [primary_category, secondary_category, tertiary_category],
                weights=[0.6, 0.3, 0.1]
            )[0]
            emoji_choice = random.choice(category)
            if emoji_choice not in suggestions:
                suggestions.append(emoji_choice)
        
        return " ".join(suggestions)