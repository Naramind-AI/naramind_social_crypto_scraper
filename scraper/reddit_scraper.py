"""
Reddit scraper for Naramind using PRAW (Python Reddit API Wrapper)
"""
import praw
import time
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
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str
    subreddits: List[str]
    keywords: List[str]
    max_posts: int = 100

class RedditScraper:
    def __init__(self, config: RedditConfig, db_session):
        self.config = config
        self.db_session = db_session
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
            username=config.username,
            password=config.password
        )
        
        # Get platform from database
        self.platform = self.db_session.query(Platform).filter_by(name='Reddit').first()
        if not self.platform:
            self.platform = Platform(name='Reddit')
            self.db_session.add(self.platform)
            self.db_session.commit()
    
    def check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        try:
            # Reddit API has built-in rate limiting, but we can track our usage
            rate_limit = self.db_session.query(RateLimit).filter_by(
                platform_id=self.platform.id,
                endpoint='reddit_api'
            ).first()
            
            if rate_limit:
                if datetime.utcnow() < rate_limit.reset_time:
                    if rate_limit.requests_made >= rate_limit.requests_limit:
                        logger.warning(f"Rate limit exceeded. Waiting until {rate_limit.reset_time}")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return True
    
    def get_subreddit_posts(self, subreddit_name: str, sort_type: str = 'new', limit: int = None) -> List[Dict]:
        """Get posts from a subreddit"""
        try:
            limit = limit or self.config.max_posts
            subreddit = self.reddit.subreddit(subreddit_name)
            
            logger.info(f"Fetching {limit} posts from r/{subreddit_name} (sort: {sort_type})")
            
            if sort_type == 'hot':
                posts = subreddit.hot(limit=limit)
            elif sort_type == 'new':
                posts = subreddit.new(limit=limit)
            elif sort_type == 'top':
                posts = subreddit.top(limit=limit, time_filter='day')
            elif sort_type == 'rising':
                posts = subreddit.rising(limit=limit)
            else:
                posts = subreddit.new(limit=limit)
            
            results = []
            for post in posts:
                # Skip stickied posts
                if post.stickied:
                    continue
                
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'selftext': post.selftext,
                    'url': post.url,
                    'author': str(post.author) if post.author else '[deleted]',
                    'author_id': str(post.author) if post.author else None,
                    'subreddit': subreddit_name,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'permalink': post.permalink,
                    'is_self': post.is_self,
                    'over_18': post.over_18,
                    'spoiler': post.spoiler,
                    'locked': post.locked,
                    'flair_text': post.link_flair_text
                }
                results.append(post_data)
            
            logger.info(f"Retrieved {len(results)} posts from r/{subreddit_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def search_posts(self, query: str, subreddit_name: str = None, sort_type: str = 'new', limit: int = 100) -> List[Dict]:
        """Search for posts with specific keywords"""
        try:
            if subreddit_name:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.search(query, sort=sort_type, limit=limit)
                logger.info(f"Searching for '{query}' in r/{subreddit_name}")
            else:
                posts = self.reddit.subreddit('all').search(query, sort=sort_type, limit=limit)
                logger.info(f"Searching for '{query}' in all subreddits")
            
            results = []
            for post in posts:
                if post.stickied:
                    continue
                
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'selftext': post.selftext,
                    'url': post.url,
                    'author': str(post.author) if post.author else '[deleted]',
                    'author_id': str(post.author) if post.author else None,
                    'subreddit': post.subreddit.display_name,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'permalink': post.permalink,
                    'is_self': post.is_self,
                    'over_18': post.over_18,
                    'spoiler': post.spoiler,
                    'locked': post.locked,
                    'flair_text': post.link_flair_text
                }
                results.append(post_data)
            
            logger.info(f"Found {len(results)} posts for query '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return []
    
    def get_post_comments(self, post_id: str, limit: int = 50) -> List[Dict]:
        """Get comments for a specific post"""
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments" objects
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    comment_data = {
                        'id': comment.id,
                        'body': comment.body,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'score': comment.score,
                        'parent_id': comment.parent_id,
                        'permalink': comment.permalink,
                        'is_submitter': comment.is_submitter
                    }
                    comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
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
    
    def save_post(self, post_data: Dict) -> Optional[Post]:
        """Save Reddit post to database"""
        try:
            # Create unique ID
            unique_id = f"reddit_{post_data['id']}"
            
            # Check if post already exists
            existing_post = self.db_session.query(Post).filter_by(id=unique_id).first()
            if existing_post:
                logger.info(f"Post {unique_id} already exists")
                return existing_post
            
            # Combine title and selftext for content
            content = post_data['title']
            if post_data['selftext']:
                content += f"\n\n{post_data['selftext']}"
            
            # Create new post
            post = Post(
                id=unique_id,
                platform_id=self.platform.id,
                content=content,
                author=post_data['author'],
                author_id=post_data['author_id'],
                post_url=f"https://reddit.com{post_data['permalink']}",
                created_at=post_data['created_utc'],
                likes=post_data['score'],
                comments=post_data['num_comments']
            )
            
            self.db_session.add(post)
            self.db_session.commit()
            
            # Analyze sentiment
            sentiment_result = self.sentiment_analyzer.analyze(content)
            sentiment = Sentiment(
                post_id=post.id,
                sentiment_type=sentiment_result['sentiment'],
                confidence_score=sentiment_result['confidence'],
                sentiment_score=sentiment_result['score'],
                model_version=sentiment_result['model_version']
            )
            self.db_session.add(sentiment)
            
            # Extract and save keywords
            keywords = self.extract_keywords(content)
            for keyword_text in keywords:
                keyword = self.db_session.query(Keyword).filter_by(keyword=keyword_text).first()
                if keyword:
                    keyword_match = KeywordMatch(
                        post_id=post.id,
                        keyword_id=keyword.id,
                        match_count=content.lower().count(keyword_text.lower())
                    )
                    self.db_session.add(keyword_match)
            
            self.db_session.commit()
            logger.info(f"Saved post {unique_id}")
            return post
            
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            self.db_session.rollback()
            return None
    
    def scrape_subreddits(self, subreddits: List[str] = None, sort_type: str = 'new') -> int:
        """Scrape posts from multiple subreddits"""
        subreddits = subreddits or self.config.subreddits
        total_scraped = 0
        
        for subreddit in subreddits:
            logger.info(f"Scraping r/{subreddit}")
            posts = self.get_subreddit_posts(subreddit, sort_type=sort_type)
            
            for post_data in posts:
                post = self.save_post(post_data)
                if post:
                    total_scraped += 1
            
            # Rate limiting delay
            time.sleep(2)
        
        logger.info(f"Total posts scraped: {total_scraped}")
        return total_scraped
    
    def scrape_keywords(self, keywords: List[str] = None, subreddits: List[str] = None) -> int:
        """Scrape posts for specific keywords"""
        keywords = keywords or self.config.keywords
        subreddits = subreddits or self.config.subreddits
        total_scraped = 0
        
        for keyword in keywords:
            for subreddit in subreddits:
                logger.info(f"Searching for '{keyword}' in r/{subreddit}")
                posts = self.search_posts(keyword, subreddit_name=subreddit)
                
                for post_data in posts:
                    post = self.save_post(post_data)
                    if post:
                        total_scraped += 1
                
                # Rate limiting delay
                time.sleep(2)
        
        logger.info(f"Total posts scraped for keywords: {total_scraped}")
        return total_scraped
    
    def continuous_scraping(self, interval_minutes: int = 30):
        """Run continuous scraping"""
        logger.info("Starting continuous Reddit scraping")
        
        while True:
            try:
                # Scrape subreddits
                scraped = self.scrape_subreddits()
                logger.info(f"Scraped {scraped} posts in this cycle")
                
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
    config = RedditConfig(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="Naramind Scraper v1.0",
        username="your_username",
        password="your_password",
        subreddits=["CryptoCurrency", "Bitcoin", "ethereum", "DeFi", "NFT"],
        keywords=["Bitcoin", "Ethereum", "DeFi", "NFT", "crypto", "blockchain"]
    )
    
    # Database session
    from database_models import init_database
    Session = init_database("sqlite:///naramind_scraper.db")
    db_session = Session()
    
    # Initialize scraper
    scraper = RedditScraper(config, db_session)
    
    # Start scraping
    scraper.continuous_scraping(interval_minutes=15)
    
    db_session.close()