"""
Telegram scraper for Naramind using Telethon
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from telethon import TelegramClient, events
from telethon.tl.types import Message, Channel, User
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from sentiment_analyzer import SentimentAnalyzer
from database_models import Session, Post, Platform, Sentiment, KeywordMatch, Keyword

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TelegramConfig:
    api_id: int
    api_hash: str
    phone_number: str
    channels: List[str]  # List of channel usernames or IDs
    keywords: List[str]
    max_messages: int = 100
    session_name: str = "naramind_session"

class TelegramScraper:
    def __init__(self, config: TelegramConfig, db_session):
        self.config = config
        self.db_session = db_session
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize Telegram client
        self.client = TelegramClient(
            config.session_name,
            config.api_id,
            config.api_hash
        )
        
        # Get platform from database
        self.platform = self.db_session.query(Platform).filter_by(name='Telegram').first()
        if not self.platform:
            self.platform = Platform(name='Telegram')
            self.db_session.add(self.platform)
            self.db_session.commit()
    
    async def authenticate(self):
        """Authenticate with Telegram"""
        try:
            await self.client.start(phone=self.config.phone_number)
            
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.config.phone_number)
                code = input("Enter the code you received: ")
                await self.client.sign_in(self.config.phone_number, code)
            
            logger.info("Successfully authenticated with Telegram")
            
        except SessionPasswordNeededError:
            password = input("Enter your 2FA password: ")
            await self.client.sign_in(password=password)
            logger.info("Successfully authenticated with 2FA")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def get_channel_entity(self, channel_username: str):
        """Get channel entity by username"""
        try:
            entity = await self.client.get_entity(channel_username)
            return entity
        except Exception as e:
            logger.error(f"Error getting channel entity for {channel_username}: {e}")
            return None
    
    async def scrape_channel_history(self, channel_username: str, limit: int = None) -> List[Dict]:
        """Scrape message history from a channel"""
        try:
            limit = limit or self.config.max_messages
            entity = await self.get_channel_entity(channel_username)
            
            if not entity:
                return []
            
            messages = []
            logger.info(f"Scraping {limit} messages from {channel_username}")
            
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.text:
                    message_data = {
                        'id': message.id,
                        'text': message.text,
                        'date': message.date,
                        'channel': channel_username,
                        'channel_id': entity.id,
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'replies': getattr(message, 'replies', {}).get('replies', 0) if hasattr(message, 'replies') and message.replies else 0,
                        'from_id': message.from_id.user_id if message.from_id else None,
                        'grouped_id': message.grouped_id
                    }
                    messages.append(message_data)
            
            logger.info(f"Scraped {len(messages)} messages from {channel_username}")
            return messages
            
        except FloodWaitError as e:
            logger.warning(f"Flood wait error: waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return []
        except Exception as e:
            logger.error(f"Error scraping channel {channel_username}: {e}")
            return []
    
    async def search_messages(self, channel_username: str, query: str, limit: int = 100) -> List[Dict]:
        """Search for messages in a channel"""
        try:
            entity = await self.get_channel_entity(channel_username)
            if not entity:
                return []
            
            messages = []
            logger.info(f"Searching for '{query}' in {channel_username}")
            
            async for message in self.client.iter_messages(entity, search=query, limit=limit):
                if message.text:
                    message_data = {
                        'id': message.id,
                        'text': message.text,
                        'date': message.date,
                        'channel': channel_username,
                        'channel_id': entity.id,
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'replies': getattr(message, 'replies', {}).get('replies', 0) if hasattr(message, 'replies') and message.replies else 0,
                        'from_id': message.from_id.user_id if message.from_id else None,
                        'grouped_id': message.grouped_id
                    }
                    messages.append(message_data)
            
            logger.info(f"Found {len(messages)} messages for query '{query}'")
            return messages
            
        except Exception as e:
            logger.error(f"Error searching messages in {channel_username}: {e}")
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
    
    async def save_message(self, message_data: Dict) -> Optional[Post]:
        """Save message to database"""
        try:
            # Create unique ID combining channel and message ID
            unique_id = f"telegram_{message_data['channel_id']}_{message_data['id']}"
            
            # Check if message already exists
            existing_post = self.db_session.query(Post).filter_by(id=unique_id).first()
            if existing_post:
                logger.info(f"Message {unique_id} already exists")
                return existing_post
            
            # Create new post
            post = Post(
                id=unique_id,
                platform_id=self.platform.id,
                content=message_data['text'],
                author=message_data['channel'],
                author_id=str(message_data['channel_id']),
                post_url=f"https://t.me/{message_data['channel']}/{message_data['id']}",
                created_at=message_data['date'],
                views=message_data.get('views', 0),
                shares=message_data.get('forwards', 0),
                comments=message_data.get('replies', 0)
            )
            
            self.db_session.add(post)
            self.db_session.commit()
            
            # Analyze sentiment
            sentiment_result = self.sentiment_analyzer.analyze(message_data['text'])
            sentiment = Sentiment(
                post_id=post.id,
                sentiment_type=sentiment_result['sentiment'],
                confidence_score=sentiment_result['confidence'],
                sentiment_score=sentiment_result['score'],
                model_version=sentiment_result['model_version']
            )
            self.db_session.add(sentiment)
            
            # Extract and save keywords
            keywords = self.extract_keywords(message_data['text'])
            for keyword_text in keywords:
                keyword = self.db_session.query(Keyword).filter_by(keyword=keyword_text).first()
                if keyword:
                    keyword_match = KeywordMatch(
                        post_id=post.id,
                        keyword_id=keyword.id,
                        match_count=message_data['text'].lower().count(keyword_text.lower())
                    )
                    self.db_session.add(keyword_match)
            
            self.db_session.commit()
            logger.info(f"Saved message {unique_id}")
            return post
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            self.db_session.rollback()
            return None
    
    async def scrape_channels(self, channels: List[str] = None) -> int:
        """Scrape messages from multiple channels"""
        channels = channels or self.config.channels
        total_scraped = 0
        
        for channel in channels:
            logger.info(f"Scraping channel: {channel}")
            messages = await self.scrape_channel_history(channel)
            
            for message_data in messages:
                post = await self.save_message(message_data)
                if post:
                    total_scraped += 1
            
            # Rate limiting delay
            await asyncio.sleep(2)
        
        logger.info(f"Total messages scraped: {total_scraped}")
        return total_scraped
    
    async def scrape_keywords(self, keywords: List[str] = None) -> int:
        """Scrape messages for specific keywords"""
        keywords = keywords or self.config.keywords
        total_scraped = 0
        
        for channel in self.config.channels:
            for keyword in keywords:
                logger.info(f"Searching for '{keyword}' in {channel}")
                messages = await self.search_messages(channel, keyword)
                
                for message_data in messages:
                    post = await self.save_message(message_data)
                    if post:
                        total_scraped += 1
                
                # Rate limiting delay
                await asyncio.sleep(2)
        
        logger.info(f"Total messages scraped for keywords: {total_scraped}")
        return total_scraped
    
    async def setup_live_monitoring(self):
        """Set up live message monitoring"""
        logger.info("Setting up live message monitoring")
        
        # Get channel entities
        channel_entities = []
        for channel in self.config.channels:
            entity = await self.get_channel_entity(channel)
            if entity:
                channel_entities.append(entity)
        
        @self.client.on(events.NewMessage(chats=channel_entities))
        async def handle_new_message(event):
            try:
                message = event.message
                if message.text:
                    # Check if message contains keywords
                    keywords = self.extract_keywords(message.text)
                    if keywords:
                        logger.info(f"New message with keywords: {keywords}")
                        
                        # Get channel info
                        channel = await event.get_chat()
                        
                        message_data = {
                            'id': message.id,
                            'text': message.text,
                            'date': message.date,
                            'channel': channel.username or channel.title,
                            'channel_id': channel.id,
                            'views': getattr(message, 'views', 0),
                            'forwards': getattr(message, 'forwards', 0),
                            'replies': 0,
                            'from_id': message.from_id.user_id if message.from_id else None,
                            'grouped_id': message.grouped_id
                        }
                        
                        await self.save_message(message_data)
                        
            except Exception as e:
                logger.error(f"Error handling new message: {e}")
    
    async def continuous_scraping(self, interval_minutes: int = 30):
        """Run continuous scraping"""
        logger.info("Starting continuous Telegram scraping")
        
        # Set up live monitoring
        await self.setup_live_monitoring()
        
        while True:
            try:
                # Scrape channels
                scraped = await self.scrape_channels()
                logger.info(f"Scraped {scraped} messages in this cycle")
                
                # Wait for next cycle
                logger.info(f"Waiting {interval_minutes} minutes for next cycle")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous scraping")
                break
            except Exception as e:
                logger.error(f"Error in continuous scraping: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def run(self):
        """Main run method"""
        try:
            await self.authenticate()
            await self.continuous_scraping()
        finally:
            await self.client.disconnect()

# Example usage
async def main():
    # Configuration
    config = TelegramConfig(
        api_id=12345,  # Your API ID
        api_hash="your_api_hash",  # Your API hash
        phone_number="+1234567890",  # Your phone number
        channels=["@bitcoinmagazine", "@ethereum", "@defi_news"],  # Channels to monitor
        keywords=["Bitcoin", "Ethereum", "DeFi", "NFT", "crypto", "blockchain"]
    )
    
    # Database session
    from database_models import init_database
    Session = init_database("sqlite:///naramind_scraper.db")
    db_session = Session()
    
    # Initialize scraper
    scraper = TelegramScraper(config, db_session)
    
    # Start scraping
    await scraper.run()
    
    db_session.close()

if __name__ == "__main__":
    asyncio.run(main())