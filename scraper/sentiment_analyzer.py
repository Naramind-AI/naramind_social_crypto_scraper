"""
Sentiment analysis module for Naramind
"""
import re
import logging
from typing import Dict, List
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.model_version = "textblob_v1.0"
        
        # Crypto-specific sentiment words
        self.crypto_positive_words = {
            'moon', 'bullish', 'pump', 'rally', 'surge', 'breakout', 'hodl',
            'diamond', 'hands', 'rocket', 'lambo', 'ath', 'gains', 'profit',
            'buy', 'accumulate', 'strong', 'support', 'resistance', 'upgrade',
            'adoption', 'institutional', 'partnership', 'integration', 'launch'
        }
        
        self.crypto_negative_words = {
            'dump', 'crash', 'bear', 'bearish', 'sell', 'panic', 'fud',
            'scam', 'rug', 'pull', 'hack', 'exploit', 'ban', 'regulation',
            'decline', 'drop', 'fall', 'weak', 'concern', 'risk', 'warning',
            'bubble', 'overvalued', 'correction', 'liquidation', 'loss'
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags symbols but keep the words
        text = re.sub(r'[@#]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Convert to lowercase
        text = text.lower().strip()
        
        return text
    
    def extract_features(self, text: str) -> Dict:
        """Extract features from text"""
        processed_text = self.preprocess_text(text)
        
        # Tokenize
        tokens = word_tokenize(processed_text)
        
        # Remove stop words and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and token.isalpha()]
        
        # Count crypto-specific sentiment words
        positive_crypto_count = sum(1 for token in tokens if token in self.crypto_positive_words)
        negative_crypto_count = sum(1 for token in tokens if token in self.crypto_negative_words)
        
        # Calculate ratios
        total_words = len(tokens)
        positive_ratio = positive_crypto_count / total_words if total_words > 0 else 0
        negative_ratio = negative_crypto_count / total_words if total_words > 0 else 0
        
        return {
            'total_words': total_words,
            'positive_crypto_count': positive_crypto_count,
            'negative_crypto_count': negative_crypto_count,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'tokens': tokens
        }
    
    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        try:
            if not text or len(text.strip()) == 0:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'score': 0.0,
                    'model_version': self.model_version
                }
            
            # Get features
            features = self.extract_features(text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Adjust sentiment based on crypto-specific words
            crypto_sentiment_adjustment = features['positive_ratio'] - features['negative_ratio']
            adjusted_polarity = polarity + (crypto_sentiment_adjustment * 0.5)
            
            # Clamp to [-1, 1] range
            adjusted_polarity = max(-1, min(1, adjusted_polarity))
            
            # Determine sentiment category
            if adjusted_polarity > 0.1:
                sentiment = 'positive'
            elif adjusted_polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate confidence based on absolute polarity and subjectivity
            confidence = abs(adjusted_polarity) * (1 - subjectivity)
            confidence = max(0.0, min(1.0, confidence))
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'score': adjusted_polarity,
                'model_version': self.model_version,
                'features': features,
                'original_polarity': polarity,
                'subjectivity': subjectivity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'score': 0.0,
                'model_version': self.model_version,
                'error': str(e)
            }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        return results
    
    def get_sentiment_summary(self, texts: List[str]) -> Dict:
        """Get sentiment summary for a list of texts"""
        results = self.batch_analyze(texts)
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_score = 0
        total_confidence = 0
        
        for result in results:
            sentiment_counts[result['sentiment']] += 1
            total_score += result['score']
            total_confidence += result['confidence']
        
        total_texts = len(results)
        
        return {
            'total_texts': total_texts,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': {
                'positive': (sentiment_counts['positive'] / total_texts) * 100 if total_texts > 0 else 0,
                'negative': (sentiment_counts['negative'] / total_texts) * 100 if total_texts > 0 else 0,
                'neutral': (sentiment_counts['neutral'] / total_texts) * 100 if total_texts > 0 else 0
            },
            'average_score': total_score / total_texts if total_texts > 0 else 0,
            'average_confidence': total_confidence / total_texts if total_texts > 0 else 0,
            'overall_sentiment': max(sentiment_counts, key=sentiment_counts.get)
        }

# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test texts
    test_texts = [
        "Bitcoin is going to the moon! 🚀 HODL diamond hands!",
        "This market crash is terrible, everything is dumping",
        "Ethereum upgrade looks promising for the future",
        "Not sure about this crypto regulation news",
        "DeFi protocols are revolutionizing finance"
    ]
    
    print("Individual Analysis:")
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Score: {result['score']:.3f}")
        print(f"Confidence: {result['confidence']:.3f}")
        print("-" * 50)
    
    print("\nBatch Summary:")
    summary = analyzer.get_sentiment_summary(test_texts)
    print(f"Overall Sentiment: {summary['overall_sentiment']}")
    print(f"Positive: {summary['sentiment_percentages']['positive']:.1f}%")
    print(f"Negative: {summary['sentiment_percentages']['negative']:.1f}%")
    print(f"Neutral: {summary['sentiment_percentages']['neutral']:.1f}%")
    print(f"Average Score: {summary['average_score']:.3f}")
    print(f"Average Confidence: {summary['average_confidence']:.3f}")