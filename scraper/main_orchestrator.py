"""
Main orchestrator for the Naramind social media scraper
"""
import asyncio
import threading
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

from twitter_scraper import TwitterScraper, TwitterConfig
from telegram_scraper import TelegramScraper, TelegramConfig
from reddit_scraper import RedditScraper, RedditConfig
from database_models import init_database, Session, ScrapingJob, ErrorLog, Platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('naramind_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    # Database
    database_url: str = "sqlite:///naramind_scraper.db"
    
    # Twitter
    twitter_bearer_token: str = ""
    twitter_consumer_key: str = ""
    twitter_consumer_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    # Telegram
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone_number: str = ""
    telegram_channels: List[str] = None
    
    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_username: str = ""
    reddit_password: str = ""
    reddit_subreddits: List[str] = None
    
    # Common
    keywords: List[str] = None
    scraping_interval: int = 30  # minutes
    max_posts_per_cycle: int = 100
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = [
                "Bitcoin", "BTC", "Ethereum", "ETH", "DeFi", "NFT",
                "crypto", "blockchain", "altcoins", "Solana", "Cardano",
                "Polygon", "Chainlink", "Uniswap", "Aave", "Compound"
            ]
        
        if self.telegram_channels is None:
            self.telegram_channels = [
                "@bitcoinmagazine", "@ethereum", "@defi_news",
                "@crypto", "@blockchain"
            ]
        
        if self.reddit_subreddits is None:
            self.reddit_subreddits = [
                "CryptoCurrency", "Bitcoin", "ethereum", "DeFi",
                "NFT", "altcoins", "CryptoNews", "CryptoMarkets"
            ]

class NaramindOrchestrator:
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.running = False
        self.scrapers = {}
        
        # Initialize database
        self.Session = init_database(config.database_url)
        
        # Initialize scrapers
        self._initialize_scrapers()
        
        # Thread pool for parallel scraping
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _initialize_scrapers(self):
        """Initialize all scrapers"""
        try:
            # Twitter scraper
            if all([self.config.twitter_bearer_token, self.config.twitter_consumer_key]):
                twitter_config = TwitterConfig(
                    bearer_token=self.config.twitter_bearer_token,
                    consumer_key=self.config.twitter_consumer_key,
                    consumer_secret=self.config.twitter_consumer_secret,
                    access_token=self.config.twitter_access_token,
                    access_token_secret=self.config.twitter_access_token_secret,
                    keywords=self.config.keywords,
                    max_results=self.config.max_posts_per_cycle
                )
                session = self.Session()
                self.scrapers['twitter'] = TwitterScraper(twitter_config, session)
                logger.info("Twitter scraper initialized")
            
            # Telegram scraper
            if all([self.config.telegram_api_id, self.config.telegram_api_hash]):
                telegram_config = TelegramConfig(
                    api_id=self.config.telegram_api_id,
                    api_hash=self.config.telegram_api_hash,
                    phone_number=self.config.telegram_phone_number,
                    channels=self.config.telegram_channels,
                    keywords=self.config.keywords,
                    max_messages=self.config.max_posts_per_cycle
                )
                session = self.Session()
                self.scrapers['telegram'] = TelegramScraper(telegram_config, session)
                logger.info("Telegram scraper initialized")
            
            # Reddit scraper
            if all([self.config.reddit_client_id, self.config.reddit_client_secret]):
                reddit_config = RedditConfig(
                    client_id=self.config.reddit_client_id,
                    client_secret=self.config.reddit_client_secret,
                    user_agent="Naramind Scraper v1.0",
                    username=self.config.reddit_username,
                    password=self.config.reddit_password,
                    subreddits=self.config.reddit_subreddits,
                    keywords=self.config.keywords,
                    max_posts=self.config.max_posts_per_cycle
                )
                session = self.Session()
                self.scrapers['reddit'] = RedditScraper(reddit_config, session)
                logger.info("Reddit scraper initialized")
            
            logger.info(f"Initialized {len(self.scrapers)} scrapers")
            
        except Exception as e:
            logger.error(f"Error initializing scrapers: {e}")
            self.log_error("initialization", str(e))
    
    def log_error(self, error_type: str, error_message: str, platform_name: str = None):
        """Log error to database"""
        try:
            session = self.Session()
            
            platform_id = None
            if platform_name:
                platform = session.query(Platform).filter_by(name=platform_name).first()
                if platform:
                    platform_id = platform.id
            
            error_log = ErrorLog(
                platform_id=platform_id,
                error_type=error_type,
                error_message=error_message,
                occurred_at=datetime.utcnow()
            )
            
            session.add(error_log)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error logging to database: {e}")
    
    def create_scraping_job(self, platform_name: str, job_type: str, configuration: Dict = None) -> str:
        """Create a new scraping job"""
        try:
            session = self.Session()
            platform = session.query(Platform).filter_by(name=platform_name).first()
            
            if not platform:
                platform = Platform(name=platform_name)
                session.add(platform)
                session.commit()
            
            job = ScrapingJob(
                platform_id=platform.id,
                job_type=job_type,
                status='pending',
                configuration=str(configuration) if configuration else None
            )
            
            session.add(job)
            session.commit()
            
            job_id = job.id
            session.close()
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error creating scraping job: {e}")
            return None
    
    def update_scraping_job(self, job_id: str, status: str, posts_scraped: int = 0, errors: str = None):
        """Update scraping job status"""
        try:
            session = self.Session()
            job = session.query(ScrapingJob).filter_by(id=job_id).first()
            
            if job:
                job.status = status
                if posts_scraped > 0:
                    job.posts_scraped = posts_scraped
                if errors:
                    job.errors = errors
                
                if status == 'running' and not job.started_at:
                    job.started_at = datetime.utcnow()
                elif status in ['completed', 'failed']:
                    job.completed_at = datetime.utcnow()
                
                session.commit()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error updating scraping job: {e}")
    
    def run_twitter_scraping(self) -> Dict:
        """Run Twitter scraping"""
        if 'twitter' not in self.scrapers:
            return {'success': False, 'message': 'Twitter scraper not initialized'}
        
        job_id = self.create_scraping_job('Twitter', 'keyword_search')
        
        try:
            self.update_scraping_job(job_id, 'running')
            scraper = self.scrapers['twitter']
            scraped_count = scraper.scrape_keywords()
            
            self.update_scraping_job(job_id, 'completed', scraped_count)
            
            return {
                'success': True,
                'platform': 'Twitter',
                'scraped_count': scraped_count,
                'job_id': job_id
            }
            
        except Exception as e:
            error_msg = f"Twitter scraping error: {e}"
            logger.error(error_msg)
            self.update_scraping_job(job_id, 'failed', errors=error_msg)
            self.log_error('scraping', error_msg, 'Twitter')
            
            return {
                'success': False,
                'platform': 'Twitter',
                'error': error_msg,
                'job_id': job_id
            }
    
    async def run_telegram_scraping(self) -> Dict:
        """Run Telegram scraping"""
        if 'telegram' not in self.scrapers:
            return {'success': False, 'message': 'Telegram scraper not initialized'}
        
        job_id = self.create_scraping_job('Telegram', 'channel_scraping')
        
        try:
            self.update_scraping_job(job_id, 'running')
            scraper = self.scrapers['telegram']
            
            # Authenticate if needed
            if not scraper.client.is_connected():
                await scraper.authenticate()
            
            scraped_count = await scraper.scrape_channels()
            
            self.update_scraping_job(job_id, 'completed', scraped_count)
            
            return {
                'success': True,
                'platform': 'Telegram',
                'scraped_count': scraped_count,
                'job_id': job_id
            }
            
        except Exception as e:
            error_msg = f"Telegram scraping error: {e}"
            logger.error(error_msg)
            self.update_scraping_job(job_id, 'failed', errors=error_msg)
            self.log_error('scraping', error_msg, 'Telegram')
            
            return {
                'success': False,
                'platform': 'Telegram',
                'error': error_msg,
                'job_id': job_id
            }
    
    def run_reddit_scraping(self) -> Dict:
        """Run Reddit scraping"""
        if 'reddit' not in self.scrapers:
            return {'success': False, 'message': 'Reddit scraper not initialized'}
        
        job_id = self.create_scraping_job('Reddit', 'subreddit_scraping')
        
        try:
            self.update_scraping_job(job_id, 'running')
            scraper = self.scrapers['reddit']
            scraped_count = scraper.scrape_subreddits()
            
            self.update_scraping_job(job_id, 'completed', scraped_count)
            
            return {
                'success': True,
                'platform': 'Reddit',
                'scraped_count': scraped_count,
                'job_id': job_id
            }
            
        except Exception as e:
            error_msg = f"Reddit scraping error: {e}"
            logger.error(error_msg)
            self.update_scraping_job(job_id, 'failed', errors=error_msg)
            self.log_error('scraping', error_msg, 'Reddit')
            
            return {
                'success': False,
                'platform': 'Reddit',
                'error': error_msg,
                'job_id': job_id
            }
    
    async def run_single_cycle(self) -> Dict:
        """Run a single scraping cycle for all platforms"""
        logger.info("Starting scraping cycle")
        
        results = {}
        
        # Run scrapers in parallel
        tasks = []
        
        if 'twitter' in self.scrapers:
            tasks.append(self.executor.submit(self.run_twitter_scraping))
        
        if 'telegram' in self.scrapers:
            tasks.append(self.run_telegram_scraping())
        
        if 'reddit' in self.scrapers:
            tasks.append(self.executor.submit(self.run_reddit_scraping))
        
        # Wait for all tasks to complete
        for task in tasks:
            if asyncio.iscoroutine(task):
                result = await task
            else:
                result = task.result()
            
            if result:
                results[result.get('platform', 'unknown')] = result
        
        total_scraped = sum(r.get('scraped_count', 0) for r in results.values() if r.get('success'))
        
        logger.info(f"Scraping cycle completed. Total posts scraped: {total_scraped}")
        
        return {
            'cycle_completed': True,
            'total_scraped': total_scraped,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def start_continuous_scraping(self):
        """Start continuous scraping"""
        logger.info("Starting continuous scraping")
        self.running = True
        
        while self.running:
            try:
                # Run scraping cycle
                cycle_result = await self.run_single_cycle()
                
                # Wait for next cycle
                logger.info(f"Waiting {self.config.scraping_interval} minutes for next cycle")
                await asyncio.sleep(self.config.scraping_interval * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous scraping")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in continuous scraping: {e}")
                self.log_error('continuous_scraping', str(e))
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping orchestrator")
        self.running = False
        
        # Close database sessions
        for scraper in self.scrapers.values():
            if hasattr(scraper, 'db_session'):
                scraper.db_session.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        try:
            session = self.Session()
            
            # Get platform stats
            platforms = session.query(Platform).all()
            platform_stats = {}
            
            for platform in platforms:
                posts_count = len(platform.posts)
                recent_posts = session.query(Post).filter_by(platform_id=platform.id).filter(
                    Post.created_at >= datetime.utcnow() - timedelta(days=1)
                ).count()
                
                platform_stats[platform.name] = {
                    'total_posts': posts_count,
                    'recent_posts_24h': recent_posts,
                    'is_active': platform.is_active
                }
            
            # Get recent jobs
            recent_jobs = session.query(ScrapingJob).order_by(
                ScrapingJob.created_at.desc()
            ).limit(10).all()
            
            jobs_info = []
            for job in recent_jobs:
                jobs_info.append({
                    'id': job.id,
                    'platform': job.platform.name,
                    'job_type': job.job_type,
                    'status': job.status,
                    'posts_scraped': job.posts_scraped,
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None
                })
            
            session.close()
            
            return {
                'platform_stats': platform_stats,
                'recent_jobs': jobs_info,
                'active_scrapers': list(self.scrapers.keys()),
                'running': self.running
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

# Example usage and main entry point
async def main():
    # Load configuration (in production, load from environment variables or config file)
    config = ScrapingConfig(
        # Twitter credentials
        twitter_bearer_token="YOUR_BEARER_TOKEN",
        twitter_consumer_key="YOUR_CONSUMER_KEY",
        twitter_consumer_secret="YOUR_CONSUMER_SECRET",
        twitter_access_token="YOUR_ACCESS_TOKEN",
        twitter_access_token_secret="YOUR_ACCESS_TOKEN_SECRET",
        
        # Telegram credentials
        telegram_api_id=12345,
        telegram_api_hash="your_api_hash",
        telegram_phone_number="+1234567890",
        
        # Reddit credentials
        reddit_client_id="YOUR_CLIENT_ID",
        reddit_client_secret="YOUR_CLIENT_SECRET",
        reddit_username="your_username",
        reddit_password="your_password",
        
        # Scraping configuration
        scraping_interval=15,  # 15 minutes
        max_posts_per_cycle=50
    )
    
    # Initialize orchestrator
    orchestrator = NaramindOrchestrator(config)
    
    try:
        # Start continuous scraping
        await orchestrator.start_continuous_scraping()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())