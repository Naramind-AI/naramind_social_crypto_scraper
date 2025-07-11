"""
Twitter scraper for Naramind using Twitter API v2
"""
import tweepy
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from sentiment_analyzer import SentimentAnalyzer
from database_models import Session, Post, Platform, Sentiment, KeywordMatch, Keyword, RateLimit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TwitterConfig:
    bearer_token: str
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str
    keywords: List[str]
    max_results: int = 100
    tweet_fields: List[str] = None
    
    def __post_init__(self):
        if self.tweet_fields is None:
            self.tweet_fields = [
                'id', 'text', 'author_id', 'created_at', 'public_metrics',
                'context_annotations', 'entities', 'lang', 'possibly_sensitive'
            ]

class TwitterScraper:
    def __init__(self, config: TwitterConfig, db_session):
        self.config = config
        self.db_session = db_session
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize Twitter API client
        self.client = tweepy.Client(
            bearer_token=config.bearer_token,
            consumer_key=config.consumer_key,
            consumer_secret=config.consumer_secret,
            access_token=config.access_token,
            access_token_secret=config.access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Get platform from database
        self.platform = self.db_session.query(Platform).filter_by(name='Twitter').first()
        if not self.platform:
            self.platform = Platform(name='Twitter')
            self.db_session.add(self.platform)
            self.db_session.commit()
    
    def check_rate_limits(self, endpoint: str) -> bool:
        """Check if we're within rate limits for a specific endpoint"""
        try:
            rate_limit = self.db_session.query(RateLimit).filter_by(
                platform_id=self.platform.id,
                endpoint=endpoint
            ).first()
            
            if rate_limit:
                if datetime.utcnow() < rate_limit.reset_time:
                    if rate_limit.requests_made >= rate_limit.requests_limit:
                        logger.warning(f"Rate limit exceeded for {endpoint}. Waiting until {rate_limit.reset_time}")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return True
    
    def update_rate_limit(self, endpoint: str, requests_made: int, requests_limit: int, reset_time: datetime):
        """Update rate limit information"""
        try:
            rate_limit = self.db_session.query(RateLimit).filter_by(
                platform_id=self.platform.id,
                endpoint=endpoint
            ).first()
            
            if rate_limit:
                rate_limit.requests_made = requests_made
                rate_limit.requests_limit = requests_limit
                rate_limit.reset_time = reset_time
            else:
                rate_limit = RateLimit(
                    platform_id=self.platform.id,
                    endpoint=endpoint,
                    requests_made=requests_made,
                    requests_limit=requests_limit,
                    reset_time=reset_time
                )
                self.db_session.add(rate_limit)
            
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Error updating rate limit: {e}")
    
    def search_tweets(self, query: str, max_results: int = None) -> List[Dict]:
        """Search for tweets based on query"""
        if not self.check_rate_limits('search_tweets'):
            return []
        
        try:
            max_results = max_results or self.config.max_results
            
            # Build search query
            search_query = f"{query} -is:retweet lang:en"
            
            logger.info(f"Searching tweets for: {search_query}")
            
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=search_query,
                tweet_fields=self.config.tweet_fields,
                max_results=min(max_results, 100),  # Twitter API limit
                limit=max_results // 100 + 1
            ).flatten(limit=max_results)
            
            results = []
            for tweet in tweets:
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'created_at': tweet.created_at,
                    'public_metrics': tweet.public_metrics,
                    'lang': tweet.lang,
                    'entities': tweet.entities
                }
                results.append(tweet_data)
            
            logger.info(f"Found {len(results)} tweets")
            return results
            
        except tweepy.TooManyRequests:
            logger.warning("Rate limit exceeded. Waiting...")
            time.sleep(15 * 60)  # Wait 15 minutes
            return []
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []
    
    def get_user_timeline(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """Get user's timeline"""
        if not self.check_rate_limits('user_timeline'):
            return []
        
        try:
            tweets = self.client.get_users_tweets(
                id=user_id,
                tweet_fields=self.config.tweet_fields,
                max_results=min(max_results, 100)
            )
            
            results = []
            if tweets.data:
                for tweet in tweets.data:
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at,
                        'public_metrics': tweet.public_metrics,
                        'lang': tweet.lang,
                        'entities': tweet.entities
                    }
                    results.append(tweet_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting user timeline: {e}")
            return []
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        keywords = []
        active_keywords = self.db_session.query(Keyword).filter_by(is_active=True).all()
        
        text_lower = text.lower()
        for keyword_obj in active_keywords:
            if keyword_obj.keyword.lower() in text_lower:
                keywords.append(keyword_obj.keyword)
        
        return keywords
    
    def save_tweet(self, tweet_data: Dict) -> Optional[Post]:
        """Save tweet to database"""
        try:
            # Check if tweet already exists
            existing_post = self.db_session.query(Post).filter_by(id=str(tweet_data['id'])).first()
            if existing_post:
                logger.info(f"Tweet {tweet_data['id']} already exists")
                return existing_post
            
            # Create new post
            post = Post(
                id=str(tweet_data['id']),
                platform_id=self.platform.id,
                content=tweet_data['text'],
                author=f"@{tweet_data['author_id']}",
                author_id=str(tweet_data['author_id']),
                post_url=f"https://twitter.com/i/web/status/{tweet_data['id']}",
                created_at=tweet_data['created_at'],
                language=tweet_data.get('lang', 'en'),
                likes=tweet_data.get('public_metrics', {}).get('like_count', 0),
                shares=tweet_data.get('public_metrics', {}).get('retweet_count', 0),
                comments=tweet_data.get('public_metrics', {}).get('reply_count', 0)
            )
            
            self.db_session.add(post)
            self.db_session.commit()
            
            # Analyze sentiment
            sentiment_result = self.sentiment_analyzer.analyze(tweet_data['text'])
            sentiment = Sentiment(
                post_id=post.id,
                sentiment_type=sentiment_result['sentiment'],
                confidence_score=sentiment_result['confidence'],
                sentiment_score=sentiment_result['score'],
                model_version=sentiment_result['model_version']
            )
            self.db_session.add(sentiment)
            
            # Extract and save keywords
            keywords = self.extract_keywords(tweet_data['text'])
            for keyword_text in keywords:
                keyword = self.db_session.query(Keyword).filter_by(keyword=keyword_text).first()
                if keyword:
                    keyword_match = KeywordMatch(
                        post_id=post.id,
                        keyword_id=keyword.id,
                        match_count=tweet_data['text'].lower().count(keyword_text.lower())
                    )
                    self.db_session.add(keyword_match)
            
            self.db_session.commit()
            logger.info(f"Saved tweet {tweet_data['id']}")
            return post
            
        except Exception as e:
            logger.error(f"Error saving tweet: {e}")
            self.db_session.rollback()
            return None
    
    def scrape_keywords(self, keywords: List[str] = None) -> int:
        """Scrape tweets for specific keywords"""
        keywords = keywords or self.config.keywords
        total_scraped = 0
        
        for keyword in keywords:
            logger.info(f"Scraping tweets for keyword: {keyword}")
            tweets = self.search_tweets(keyword)
            
            for tweet_data in tweets:
                post = self.save_tweet(tweet_data)
                if post:
                    total_scraped += 1
            
            # Rate limiting delay
            time.sleep(2)
        
        logger.info(f"Total tweets scraped: {total_scraped}")
        return total_scraped
    
    def scrape_user_timelines(self, user_ids: List[str]) -> int:
        """Scrape timelines for specific users"""
        total_scraped = 0
        
        for user_id in user_ids:
            logger.info(f"Scraping timeline for user: {user_id}")
            tweets = self.get_user_timeline(user_id)
            
            for tweet_data in tweets:
                post = self.save_tweet(tweet_data)
                if post:
                    total_scraped += 1
            
            # Rate limiting delay
            time.sleep(2)
        
        logger.info(f"Total tweets scraped from timelines: {total_scraped}")
        return total_scraped
    
    def continuous_scraping(self, interval_minutes: int = 30):
        """Run continuous scraping"""
        logger.info("Starting continuous Twitter scraping")
        
        while True:
            try:
                # Scrape keywords
                scraped = self.scrape_keywords()
                logger.info(f"Scraped {scraped} tweets in this cycle")
                
                # Wait for next cycle
                logger.info(f"Waiting {interval_minutes} minutes for next cycle")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous scraping")
                break
            except Exception as e:
                logger.error(f"Error in continuous scraping: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

# Example usage
if __name__ == "__main__":
    # Configuration
    config = TwitterConfig(
        bearer_token="YOUR_BEARER_TOKEN",
        consumer_key="YOUR_CONSUMER_KEY",
        consumer_secret="YOUR_CONSUMER_SECRET",
        access_token="YOUR_ACCESS_TOKEN",
        access_token_secret="YOUR_ACCESS_TOKEN_SECRET",
        keywords=["Bitcoin", "Ethereum", "DeFi", "NFT", "crypto", "blockchain"]
    )
    
    # Database session
    from database_models import init_database
    Session = init_database("sqlite:///naramind_scraper.db")
    db_session = Session()
    
    # Initialize scraper
    scraper = TwitterScraper(config, db_session)
    
    # Start scraping
    scraper.continuous_scraping(interval_minutes=15)
    
    db_session.close()