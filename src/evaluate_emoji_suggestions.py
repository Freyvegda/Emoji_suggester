import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from collections import Counter
import emoji

class EmojiSuggestionEvaluator:
    def __init__(self):
        # Create evaluation directory if it doesn't exist
        self.eval_dir = os.path.join('d:', 'CODES', 'Projects', 'Emoji', 'data', 'evaluation')
        os.makedirs(self.eval_dir, exist_ok=True)
        
        # Load test results
        test_results_path = os.path.join('d:', 'CODES', 'Projects', 'Emoji', 'data', 'test_data', 'test_results.json')
        with open(test_results_path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        # Convert to DataFrame for easier analysis
        self.df = pd.DataFrame(self.results)
        
        # Load emoji categories for reference
        emoji_categories_path = os.path.join('d:', 'CODES', 'Projects', 'Emoji', 'data', 'emoji_categories.json')
        try:
            with open(emoji_categories_path, 'r', encoding='utf-8') as f:
                self.emoji_categories = json.load(f)
        except FileNotFoundError:
            # Create a simplified version if file doesn't exist
            self.emoji_categories = {
                "positive": ["😊", "😄", "😁", "😃", "😀", "🙂", "😍", "🥰", "😘", "👍", 
                            "🎉", "✨", "🌟", "💯", "🔥", "👏", "🤩", "😎", "🌈", "💪"],
                "neutral": ["😐", "🤔", "🙄", "😶", "😑", "🤷", "👀", "💭", "🧐", "🤨",
                           "📝", "🗒️", "📊", "🔍", "⏱️", "📌", "🔄", "🔔", "📱", "💻"],
                "negative": ["😕", "😟", "😔", "😞", "😢", "😭", "😠", "😡", "😤", "👎",
                            "💔", "😓", "😥", "😰", "😨", "😱", "😖", "😣", "😩", "😫"],
                "mixed": ["😅", "😬", "😏", "🙃", "😌", "🤐", "😒", "🤥", "😪", "😴",
                         "🤞", "🤝", "🙏", "💆", "🧘", "💅", "🤦", "🤷", "🙇", "🤯"]
            }
    
    def categorize_emoji(self, emoji_char):
        """Determine which category an emoji belongs to"""
        for category, emoji_list in self.emoji_categories.items():
            # Flatten nested categories if they exist
            if isinstance(emoji_list, dict):
                all_emojis = []
                for subcategory, emojis in emoji_list.items():
                    all_emojis.extend(emojis)
                if emoji_char in all_emojis:
                    return category
            elif emoji_char in emoji_list:
                return category
        return "unknown"
    
    def evaluate_sentiment_emoji_match(self):
        """Evaluate how well emoji suggestions match the sentiment"""
        print("Evaluating sentiment-emoji match...")
        
        # Add emoji category columns to dataframe
        self.df['emoji_list'] = self.df['suggested_emojis'].apply(lambda x: x.split())
        self.df['emoji_categories'] = self.df['emoji_list'].apply(
            lambda emojis: [self.categorize_emoji(e) for e in emojis]
        )
        
        # Map sentiment categories to expected emoji categories
        sentiment_to_emoji_map = {
            "very_positive": "positive",
            "positive": "positive",
            "slightly_positive": "positive",
            "neutral": "neutral",
            "slightly_negative": "negative",
            "negative": "negative",
            "very_negative": "negative"
        }
        
        self.df['expected_emoji_category'] = self.df['sentiment_category'].map(sentiment_to_emoji_map)
        
        # Calculate match percentage for each suggestion
        def calculate_match(row):
            expected = row['expected_emoji_category']
            categories = row['emoji_categories']
            if not categories:
                return 0
            matches = sum(1 for cat in categories if cat == expected)
            return matches / len(categories)
        
        self.df['match_percentage'] = self.df.apply(calculate_match, axis=1)
        
        # Overall accuracy
        overall_accuracy = self.df['match_percentage'].mean()
        
        # Accuracy by sentiment category
        accuracy_by_sentiment = self.df.groupby('sentiment_category')['match_percentage'].mean()
        
        # Create confusion matrix
        # For each suggested emoji, check if it matches the expected category
        all_categories = ['positive', 'neutral', 'negative', 'mixed']
        
        # Flatten the emoji categories for confusion matrix
        true_categories = []
        pred_categories = []
        
        for _, row in self.df.iterrows():
            expected = row['expected_emoji_category']
            for category in row['emoji_categories']:
                true_categories.append(expected)
                pred_categories.append(category)
        
                cm = confusion_matrix(
            true_categories, 
            pred_categories, 
            labels=all_categories
        )
        
        # Save results to files
        results_summary = {
            "overall_accuracy": overall_accuracy,
            "accuracy_by_sentiment": accuracy_by_sentiment.to_dict(),
            "confusion_matrix": cm.tolist(),
            "confusion_matrix_labels": all_categories
        }
        
        with open(os.path.join(self.eval_dir, 'evaluation_summary.json'), 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2)
        
        return results_summary
    
    def generate_visualizations(self):
        """Generate visualizations of the evaluation results"""
        print("Generating visualizations...")
        
        # Evaluate if not already done
        if 'match_percentage' not in self.df.columns:
            self.evaluate_sentiment_emoji_match()
        
        # 1. Sentiment distribution
        plt.figure(figsize=(10, 6))
        sns.countplot(x='sentiment_category', data=self.df, order=[
            'very_positive', 'positive', 'slightly_positive', 'neutral',
            'slightly_negative', 'negative', 'very_negative'
        ])
        plt.title('Distribution of Sentiment Categories')
        plt.xlabel('Sentiment Category')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.eval_dir, 'sentiment_distribution.png'))
        
        # 2. Accuracy by sentiment category
        accuracy_by_sentiment = self.df.groupby('sentiment_category')['match_percentage'].mean().reset_index()
        plt.figure(figsize=(10, 6))
        sns.barplot(x='sentiment_category', y='match_percentage', data=accuracy_by_sentiment, order=[
            'very_positive', 'positive', 'slightly_positive', 'neutral',
            'slightly_negative', 'negative', 'very_negative'
        ])
        plt.title('Emoji Suggestion Accuracy by Sentiment Category')
        plt.xlabel('Sentiment Category')
        plt.ylabel('Accuracy')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.eval_dir, 'accuracy_by_sentiment.png'))
        
        # 3. Confusion Matrix Heatmap
        # Flatten the emoji categories for confusion matrix
        true_categories = []
        pred_categories = []
        
        for _, row in self.df.iterrows():
            expected = row['expected_emoji_category']
            for category in row['emoji_categories']:
                true_categories.append(expected)
                pred_categories.append(category)
        
        all_categories = ['positive', 'neutral', 'negative', 'mixed']
        cm = confusion_matrix(
            true_categories, 
            pred_categories, 
            labels=all_categories
        )
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=all_categories,
                   yticklabels=all_categories)
        plt.title('Confusion Matrix: Expected vs. Suggested Emoji Categories')
        plt.xlabel('Suggested Emoji Category')
        plt.ylabel('Expected Emoji Category')
        plt.tight_layout()
        plt.savefig(os.path.join(self.eval_dir, 'confusion_matrix.png'))
        
        # 4. Sentiment vs. Emoji Category Distribution
        emoji_category_counts = []
        for _, row in self.df.iterrows():
            sentiment = row['sentiment_category']
            for category in row['emoji_categories']:
                emoji_category_counts.append({
                    'sentiment_category': sentiment,
                    'emoji_category': category
                })
        
        emoji_df = pd.DataFrame(emoji_category_counts)
        plt.figure(figsize=(12, 8))
        ct = pd.crosstab(emoji_df['sentiment_category'], emoji_df['emoji_category'])
        sns.heatmap(ct, annot=True, fmt='d', cmap='YlGnBu')
        plt.title('Distribution of Emoji Categories by Sentiment')
        plt.xlabel('Emoji Category')
        plt.ylabel('Sentiment Category')
        plt.tight_layout()
        plt.savefig(os.path.join(self.eval_dir, 'emoji_sentiment_distribution.png'))
        
        # 5. Short-term vs. Long-term Sentiment Scatter Plot
        plt.figure(figsize=(10, 8))
        sns.scatterplot(
            x='short_term_sentiment', 
            y='long_term_sentiment', 
            hue='sentiment_category',
            data=self.df,
            palette='viridis'
        )
        plt.title('Short-term vs. Long-term Sentiment')
        plt.xlabel('Short-term Sentiment')
        plt.ylabel('Long-term Sentiment')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.eval_dir, 'sentiment_comparison.png'))
        
        # 6. Match Percentage Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(self.df['match_percentage'], bins=10, kde=True)
        plt.title('Distribution of Emoji-Sentiment Match Percentages')
        plt.xlabel('Match Percentage')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(self.eval_dir, 'match_percentage_distribution.png'))
        
        print(f"Visualizations saved to {self.eval_dir}")
    
    def generate_report(self):
        """Generate a comprehensive evaluation report"""
        print("Generating evaluation report...")
        
        # Evaluate if not already done
        if 'match_percentage' not in self.df.columns:
            results = self.evaluate_sentiment_emoji_match()
        else:
            # Recalculate summary metrics
            overall_accuracy = self.df['match_percentage'].mean()
            accuracy_by_sentiment = self.df.groupby('sentiment_category')['match_percentage'].mean()
            
            # Create confusion matrix
            true_categories = []
            pred_categories = []
            for _, row in self.df.iterrows():
                expected = row['expected_emoji_category']
                for category in row['emoji_categories']:
                    true_categories.append(expected)
                    pred_categories.append(category)
            
            all_categories = ['positive', 'neutral', 'negative', 'mixed']
            cm = confusion_matrix(
                true_categories, 
                pred_categories, 
                labels=all_categories
            )
            
            results = {
                "overall_accuracy": overall_accuracy,
                "accuracy_by_sentiment": accuracy_by_sentiment.to_dict(),
                "confusion_matrix": cm.tolist(),
                "confusion_matrix_labels": all_categories
            }
        
        # Generate visualizations
        self.generate_visualizations()
        
        # Create HTML report
        html_report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Emoji Suggestion Evaluation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .metric {{ margin-bottom: 10px; }}
                .metric-value {{ font-weight: bold; }}
                .container {{ display: flex; flex-wrap: wrap; }}
                .chart {{ margin: 10px; max-width: 600px; }}
                img {{ max-width: 100%; border: 1px solid #ddd; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Emoji Suggestion Evaluation Report</h1>
            
            <h2>Summary Metrics</h2>
            <div class="metric">
                <span>Overall Accuracy: </span>
                <span class="metric-value">{results["overall_accuracy"]:.2f}</span>
            </div>
            
            <h3>Accuracy by Sentiment Category</h3>
            <table>
                <tr>
                    <th>Sentiment Category</th>
                    <th>Accuracy</th>
                </tr>
        """
        
        # Add rows for each sentiment category
        for category, accuracy in results["accuracy_by_sentiment"].items():
            html_report += f"""
                <tr>
                    <td>{category}</td>
                    <td>{accuracy:.2f}</td>
                </tr>
            """
        
        html_report += """
            </table>
            
            <h2>Visualizations</h2>
            <div class="container">
                <div class="chart">
                    <h3>Sentiment Distribution</h3>
                    <img src="sentiment_distribution.png" alt="Sentiment Distribution">
                </div>
                
                <div class="chart">
                    <h3>Accuracy by Sentiment</h3>
                    <img src="accuracy_by_sentiment.png" alt="Accuracy by Sentiment">
                </div>
                
                <div class="chart">
                    <h3>Confusion Matrix</h3>
                    <img src="confusion_matrix.png" alt="Confusion Matrix">
                </div>
                
                <div class="chart">
                    <h3>Emoji-Sentiment Distribution</h3>
                    <img src="emoji_sentiment_distribution.png" alt="Emoji-Sentiment Distribution">
                </div>
                
                <div class="chart">
                    <h3>Short-term vs. Long-term Sentiment</h3>
                    <img src="sentiment_comparison.png" alt="Sentiment Comparison">
                </div>
                
                <div class="chart">
                    <h3>Match Percentage Distribution</h3>
                    <img src="match_percentage_distribution.png" alt="Match Percentage Distribution">
                </div>
            </div>
            
            <h2>Conclusion</h2>
            <p>
                This report evaluates the performance of the emoji suggestion algorithm based on sentiment analysis.
                The overall accuracy of {results["overall_accuracy"]:.2f} indicates how well the suggested emojis match
                the expected sentiment categories.
            </p>
            
            <p>
                Areas for improvement:
                <ul>
                    <li>Fine-tune sentiment thresholds for better categorization</li>
                    <li>Expand emoji categories for more nuanced suggestions</li>
                    <li>Adjust the weighting between short-term and long-term sentiment</li>
                </ul>
            </p>
        </body>
        </html>
        """
        
        # Save HTML report
        with open(os.path.join(self.eval_dir, 'evaluation_report.html'), 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"Evaluation report saved to {os.path.join(self.eval_dir, 'evaluation_report.html')}")

if __name__ == "__main__":
    evaluator = EmojiSuggestionEvaluator()
    evaluator.evaluate_sentiment_emoji_match()
    evaluator.generate_visualizations()
    evaluator.generate_report()
    print("Evaluation complete!")