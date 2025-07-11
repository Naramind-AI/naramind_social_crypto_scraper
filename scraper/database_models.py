"""
Database models for the Naramind social media scraper
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Platform(Base):
    __tablename__ = 'platforms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="platform")
    rate_limits = relationship("RateLimit", back_populates="platform")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(String(255), primary_key=True)  # Platform-specific post ID
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    author_id = Column(String(255))
    post_url = Column(String(500))
    created_at = Column(DateTime, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Metadata
    language = Column(String(10))
    is_verified_author = Column(Boolean, default=False)
    
    # Relationships
    platform = relationship("Platform", back_populates="posts")
    sentiments = relationship("Sentiment", back_populates="post")
    keywords = relationship("KeywordMatch", back_populates="post")
    mentions = relationship("Mention", back_populates="post")

    # Indexes for performance
    __table_args__ = (
        Index('idx_platform_created', 'platform_id', 'created_at'),
        Index('idx_author_created', 'author', 'created_at'),
        Index('idx_scraped_at', 'scraped_at'),
    )

class Sentiment(Base):
    __tablename__ = 'sentiments'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(255), ForeignKey('posts.id'), nullable=False)
    sentiment_type = Column(String(20), nullable=False)  # positive, negative, neutral
    confidence_score = Column(Float, nullable=False)
    sentiment_score = Column(Float)  # -1 to 1 range
    model_version = Column(String(50))
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post = relationship("Post", back_populates="sentiments")

class Keyword(Base):
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(255), unique=True, nullable=False)
    category = Column(String(100))  # crypto, token, protocol, person, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    matches = relationship("KeywordMatch", back_populates="keyword")

class KeywordMatch(Base):
    __tablename__ = 'keyword_matches'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(255), ForeignKey('posts.id'), nullable=False)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    match_count = Column(Integer, default=1)
    match_positions = Column(Text)  # JSON string of positions
    
    # Relationships
    post = relationship("Post", back_populates="keywords")
    keyword = relationship("Keyword", back_populates="matches")

class Mention(Base):
    __tablename__ = 'mentions'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(255), ForeignKey('posts.id'), nullable=False)
    mentioned_user = Column(String(255), nullable=False)
    mentioned_user_id = Column(String(255))
    mention_type = Column(String(50))  # user, hashtag, cashtag
    
    # Relationships
    post = relationship("Post", back_populates="mentions")

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False)
    endpoint = Column(String(255), nullable=False)
    requests_made = Column(Integer, default=0)
    requests_limit = Column(Integer, nullable=False)
    reset_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="rate_limits")

class ScrapingJob(Base):
    __tablename__ = 'scraping_jobs'
    
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False)
    job_type = Column(String(100), nullable=False)  # keyword_search, user_timeline, etc.
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    posts_scraped = Column(Integer, default=0)
    errors = Column(Text)
    configuration = Column(Text)  # JSON string of job config
    
    # Relationships
    platform = relationship("Platform")

class ErrorLog(Base):
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey('platforms.id'))
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    
    # Relationships
    platform = relationship("Platform")

# Database initialization
def init_database(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

# Sample data initialization
def init_sample_data(session):
    # Create platforms
    platforms = [
        Platform(name='Twitter'),
        Platform(name='Telegram'),
        Platform(name='Reddit')
    ]
    
    for platform in platforms:
        session.add(platform)
    
    # Create keywords
    keywords = [
        Keyword(keyword='Bitcoin', category='crypto'),
        Keyword(keyword='BTC', category='crypto'),
        Keyword(keyword='Ethereum', category='crypto'),
        Keyword(keyword='ETH', category='crypto'),
        Keyword(keyword='DeFi', category='protocol'),
        Keyword(keyword='NFT', category='protocol'),
        Keyword(keyword='Solana', category='crypto'),
        Keyword(keyword='Cardano', category='crypto'),
        Keyword(keyword='Polygon', category='crypto'),
        Keyword(keyword='Chainlink', category='crypto'),
    ]
    
    for keyword in keywords:
        session.add(keyword)
    
    session.commit()
    print("Sample data initialized successfully!")

if __name__ == "__main__":
    # Example usage
    DATABASE_URL = "sqlite:///naramind_scraper.db"
    Session = init_database(DATABASE_URL)
    session = Session()
    init_sample_data(session)
    session.close()