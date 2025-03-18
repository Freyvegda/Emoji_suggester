class ChatProcessor:
    def __init__(self):
        # Store messages by user
        self.messages = {
            "User 1": [],
            "User 2": []
        }
        # Add default messages to ensure emoji suggestions from the start
        self.default_messages = {
            "User 1": ["Hello", "How are you?"],
            "User 2": ["Hi there", "I'm doing well"]
        }
        
        # Initialize with default messages
        for user, msgs in self.default_messages.items():
            self.messages[user] = msgs.copy()
    
    def add_message(self, user, message):
        """Add a message to the user's message history"""
        if user in self.messages:
            self.messages[user].append(message)
        else:
            self.messages[user] = [message]
    
    def get_recent_messages(self, user, count=10):
        """Get the most recent messages from a specific user"""
        if user not in self.messages:
            return []
        
        return self.messages[user][-count:]
    
    def get_conversation(self, count=20):
        """Get the most recent messages from the conversation (all users)"""
        all_messages = []
        for user, msgs in self.messages.items():
            for msg in msgs:
                all_messages.append((user, msg))
        
        # Sort by assumed timestamp (just by order added in this simple implementation)
        return all_messages[-count:]
        
    def reset_conversation(self):
        """Reset the conversation to initial state with default messages"""
        for user, msgs in self.default_messages.items():
            self.messages[user] = msgs.copy()
            
    def has_messages(self, user):
        """Check if a user has any messages"""
        return user in self.messages and len(self.messages[user]) > 0