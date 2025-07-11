# Naramind Social Media Crypto Scraper

A comprehensive social media monitoring system designed to track cryptocurrency conversations across Twitter, Telegram, and Reddit platforms with real-time sentiment analysis and intelligent data processing.

## 🚀 Features

### Multi-Platform Monitoring
- **Twitter**: Real-time tweet scraping using Twitter API v2
- **Telegram**: Channel monitoring with Telethon client
- **Reddit**: Subreddit and post tracking via PRAW
- **Unified Data Model**: Consistent data structure across all platforms

### Advanced Analytics
- **Sentiment Analysis**: Crypto-specific sentiment detection with confidence scoring
- **Keyword Tracking**: Monitor cryptocurrencies, tokens, protocols, and influencers
- **Real-time Processing**: Live data ingestion with immediate analysis
- **Trend Detection**: Identify emerging topics and sentiment shifts

### Production-Ready Architecture
- **Rate Limit Management**: Intelligent handling of API restrictions
- **Error Recovery**: Robust error handling with automatic retry mechanisms
- **Scalable Design**: Horizontal and vertical scaling capabilities
- **Job Orchestration**: Centralized management of scraping tasks
- **Monitoring Dashboard**: Real-time system health and performance metrics

### Data Intelligence
- **Structured Storage**: Comprehensive database schema with relationships
- **Metadata Extraction**: Author information, engagement metrics, timestamps
- **Keyword Matching**: Advanced pattern recognition for crypto terms
- **Historical Analysis**: Time-series data for trend analysis

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Dashboard │    │   Orchestrator   │    │   Data Storage  │
│                 │    │                  │    │                 │
│ • Real-time UI  │◄──►│ • Job Scheduling │◄──►│ • SQLAlchemy    │
│ • Configuration │    │ • Error Handling │    │ • Relationships │
│ • Monitoring    │    │ • Rate Limiting  │    │ • Indexing      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
        │   Twitter    │ │  Telegram   │ │   Reddit   │
        │   Scraper    │ │   Scraper   │ │  Scraper   │
        │              │ │             │ │            │
        │ • API v2     │ │ • Telethon  │ │ • PRAW     │
        │ • Real-time  │ │ • Channels  │ │ • Subreddits│
        │ • Keywords   │ │ • Messages  │ │ • Posts     │
        └──────────────┘ └─────────────┘ └────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                    ┌───────────▼──────────┐
                    │  Sentiment Analyzer  │
                    │                      │
                    │ • TextBlob + NLTK    │
                    │ • Crypto Keywords    │
                    │ • Confidence Scoring │
                    └──────────────────────┘
```

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+ (for web dashboard)
- SQLite or PostgreSQL
- 4GB+ RAM recommended
- Stable internet connection

### API Credentials Required

#### Twitter API v2
1. Create a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com)
2. Create a new app and generate:
   - Bearer Token
   - Consumer Key & Secret
   - Access Token & Secret

#### Telegram API
1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in and create a new application
3. Obtain:
   - API ID
   - API Hash
   - Phone number for authentication

#### Reddit API
1. Create a Reddit account and visit [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Create a new application (script type)
3. Obtain:
   - Client ID
   - Client Secret
   - Username & Password

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/Naramind-AI/naramind_social_crypto_scraper.git
cd naramind_social_crypto_scraper
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 3. Frontend Setup
```bash
# Install Node.js dependencies
npm install

# Build the dashboard
npm run build
```

### 4. Database Initialization
```bash
# Initialize database with sample data
python scraper/database_models.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///naramind_scraper.db
# For PostgreSQL: postgresql://user:password@localhost/naramind_db

# Twitter API Credentials
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_CONSUMER_KEY=your_consumer_key_here
TWITTER_CONSUMER_SECRET=your_consumer_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# Telegram API Credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890

# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here

# Scraping Configuration
SCRAPING_INTERVAL=15  # minutes between scraping cycles
MAX_POSTS_PER_CYCLE=100
LOG_LEVEL=INFO

# Monitoring Keywords (comma-separated)
CRYPTO_KEYWORDS=Bitcoin,BTC,Ethereum,ETH,DeFi,NFT,Solana,Cardano,Polygon,Chainlink

# Telegram Channels to Monitor
TELEGRAM_CHANNELS=@bitcoinmagazine,@ethereum,@defi_news,@crypto

# Reddit Subreddits to Monitor
REDDIT_SUBREDDITS=CryptoCurrency,Bitcoin,ethereum,DeFi,NFT,altcoins
```

### Platform-Specific Configuration

#### Twitter Setup
```python
# Configure keywords and search parameters
TWITTER_KEYWORDS = [
    "Bitcoin", "BTC", "Ethereum", "ETH", "DeFi", "NFT",
    "Solana", "Cardano", "Polygon", "Chainlink", "Uniswap"
]

# Influencer accounts to monitor
TWITTER_INFLUENCERS = [
    "@elonmusk", "@VitalikButerin", "@cz_binance", 
    "@aantonop", "@SatoshiLite"
]
```

#### Telegram Setup
```python
# Channels and groups to monitor
TELEGRAM_CHANNELS = [
    "@bitcoinmagazine",    # Bitcoin Magazine
    "@ethereum",           # Ethereum Official
    "@defi_news",         # DeFi News
    "@crypto",            # General Crypto
    "@blockchain"         # Blockchain News
]
```

#### Reddit Setup
```python
# Subreddits to monitor
REDDIT_SUBREDDITS = [
    "CryptoCurrency",     # Main crypto subreddit
    "Bitcoin",            # Bitcoin discussions
    "ethereum",           # Ethereum community
    "DeFi",              # DeFi protocols
    "NFT",               # NFT marketplace
    "altcoins",          # Alternative cryptocurrencies
    "CryptoNews",        # Crypto news
    "CryptoMarkets"      # Market discussions
]
```

## 🚀 Usage

### Quick Start

1. **Start the Web Dashboard**:
```bash
npm run dev
```

2. **Run Individual Scrapers**:
```bash
# Twitter scraper
python scraper/twitter_scraper.py

# Telegram scraper
python scraper/telegram_scraper.py

# Reddit scraper
python scraper/reddit_scraper.py
```

3. **Run Complete System**:
```bash
python scraper/main_orchestrator.py
```

### Advanced Usage

#### Custom Scraping Configuration
```python
from scraper.main_orchestrator import NaramindOrchestrator, ScrapingConfig

# Create custom configuration
config = ScrapingConfig(
    keywords=["Bitcoin", "Ethereum", "DeFi"],
    scraping_interval=10,  # 10 minutes
    max_posts_per_cycle=50,
    database_url="postgresql://user:pass@localhost/naramind"
)

# Initialize and start orchestrator
orchestrator = NaramindOrchestrator(config)
await orchestrator.start_continuous_scraping()
```

#### Sentiment Analysis
```python
from scraper.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze single text
result = analyzer.analyze("Bitcoin is going to the moon! 🚀")
print(f"Sentiment: {result['sentiment']}")
print(f"Score: {result['score']:.3f}")
print(f"Confidence: {result['confidence']:.3f}")

# Batch analysis
texts = ["Bullish on ETH", "Market crash incoming", "HODL strong"]
results = analyzer.batch_analyze(texts)

# Get summary statistics
summary = analyzer.get_sentiment_summary(texts)
print(f"Overall sentiment: {summary['overall_sentiment']}")
```

#### Database Queries
```python
from scraper.database_models import Session, Post, Sentiment, Platform

session = Session()

# Get recent posts with positive sentiment
positive_posts = session.query(Post).join(Sentiment).filter(
    Sentiment.sentiment_type == 'positive',
    Sentiment.confidence_score > 0.7
).limit(10).all()

# Get posts by platform
twitter_posts = session.query(Post).join(Platform).filter(
    Platform.name == 'Twitter'
).count()

# Get trending keywords
from sqlalchemy import func
trending = session.query(
    Keyword.keyword,
    func.count(KeywordMatch.id).label('mentions')
).join(KeywordMatch).group_by(Keyword.keyword).order_by(
    func.count(KeywordMatch.id).desc()
).limit(10).all()
```

## 📊 Database Schema

### Core Tables

#### Platforms
```sql
CREATE TABLE platforms (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Posts
```sql
CREATE TABLE posts (
    id VARCHAR(255) PRIMARY KEY,
    platform_id INTEGER REFERENCES platforms(id),
    content TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    author_id VARCHAR(255),
    post_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    language VARCHAR(10),
    is_verified_author BOOLEAN DEFAULT FALSE
);
```

#### Sentiments
```sql
CREATE TABLE sentiments (
    id INTEGER PRIMARY KEY,
    post_id VARCHAR(255) REFERENCES posts(id),
    sentiment_type VARCHAR(20) NOT NULL,
    confidence_score FLOAT NOT NULL,
    sentiment_score FLOAT,
    model_version VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Keywords
```sql
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY,
    keyword VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relationships
- `platforms` → `posts` (one-to-many)
- `posts` → `sentiments` (one-to-many)
- `posts` → `keyword_matches` (one-to-many)
- `keywords` → `keyword_matches` (one-to-many)

## 🔧 API Rate Limits

### Twitter API v2
- **Search Tweets**: 300 requests per 15 minutes
- **User Timeline**: 75 requests per 15 minutes
- **Rate Limit Headers**: Automatically monitored
- **Retry Strategy**: Exponential backoff with jitter

### Telegram API
- **No Official Limits**: But flood protection exists
- **Flood Wait**: Automatic handling of temporary bans
- **Respectful Delays**: 1-2 seconds between requests
- **Session Management**: Persistent sessions to avoid re-authentication

### Reddit API
- **OAuth Limits**: 60 requests per minute
- **PRAW Integration**: Built-in rate limiting
- **Request Queuing**: Automatic request spacing
- **Error Handling**: Retry on temporary failures

## 📈 Monitoring and Maintenance

### Health Checks
```python
# Check system health
orchestrator = NaramindOrchestrator(config)
stats = orchestrator.get_stats()

print(f"Active scrapers: {stats['active_scrapers']}")
print(f"System running: {stats['running']}")
print(f"Platform stats: {stats['platform_stats']}")
```

### Performance Metrics
- **Throughput**: Posts scraped per hour
- **Latency**: Time from post creation to database storage
- **Error Rate**: Failed requests vs successful requests
- **Sentiment Accuracy**: Manual validation of sentiment scores

### Logging Configuration
```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('naramind_scraper.log'),
        logging.StreamHandler()
    ]
)
```

### Database Maintenance
```sql
-- Clean old data (older than 30 days)
DELETE FROM posts WHERE scraped_at < datetime('now', '-30 days');

-- Optimize database
VACUUM;
ANALYZE;

-- Check table sizes
SELECT 
    name,
    COUNT(*) as row_count
FROM sqlite_master 
WHERE type='table';
```

## 🔒 Security and Compliance

### Data Privacy
- **Minimal Data Collection**: Only public posts and metadata
- **No Personal Information**: Avoid collecting private user data
- **Data Retention**: Configurable retention policies
- **Anonymization**: Option to anonymize user identifiers

### API Compliance
- **Terms of Service**: Strict adherence to platform ToS
- **Rate Limiting**: Respectful API usage
- **Attribution**: Proper source attribution
- **Content Guidelines**: Respect platform content policies

### Security Best Practices
```python
# Environment variable management
from dotenv import load_dotenv
load_dotenv()

# Secure credential storage
import os
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Input validation
def validate_keyword(keyword):
    if not keyword or len(keyword) > 100:
        raise ValueError("Invalid keyword")
    return keyword.strip()
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scraper/main_orchestrator.py"]
```

### Production Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  scraper:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/naramind
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: naramind
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    restart: unless-stopped

volumes:
  postgres_data:
```

### Scaling Strategies

#### Horizontal Scaling
- **Multiple Scrapers**: Deploy separate instances per platform
- **Load Balancing**: Distribute scraping load across instances
- **Database Sharding**: Partition data by platform or time
- **Message Queues**: Use Redis/RabbitMQ for job distribution

#### Vertical Scaling
- **Database Optimization**: Indexes, query optimization
- **Caching**: Redis for frequently accessed data
- **Async Processing**: Concurrent scraping operations
- **Resource Monitoring**: CPU, memory, and network usage

## 🐛 Troubleshooting

### Common Issues

#### Authentication Failures
```bash
# Check credentials
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Twitter Bearer Token:', bool(os.getenv('TWITTER_BEARER_TOKEN')))
print('Telegram API ID:', bool(os.getenv('TELEGRAM_API_ID')))
print('Reddit Client ID:', bool(os.getenv('REDDIT_CLIENT_ID')))
"
```

#### Rate Limit Issues
```python
# Monitor rate limits
from scraper.database_models import Session, RateLimit

session = Session()
rate_limits = session.query(RateLimit).all()
for limit in rate_limits:
    print(f"{limit.platform.name}: {limit.requests_made}/{limit.requests_limit}")
```

#### Database Connection Problems
```python
# Test database connection
from scraper.database_models import init_database

try:
    Session = init_database("sqlite:///test.db")
    session = Session()
    print("Database connection successful")
    session.close()
except Exception as e:
    print(f"Database error: {e}")
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('scraper').setLevel(logging.DEBUG)

# Test individual components
from scraper.sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
result = analyzer.analyze("Test message")
print(f"Debug result: {result}")
```

### Performance Optimization
```python
# Database query optimization
from sqlalchemy import text

# Use raw SQL for complex queries
result = session.execute(text("""
    SELECT p.platform_id, COUNT(*) as post_count
    FROM posts p
    WHERE p.created_at > datetime('now', '-1 day')
    GROUP BY p.platform_id
"""))

# Batch processing
posts = session.query(Post).limit(1000).all()
for batch in [posts[i:i+100] for i in range(0, len(posts), 100)]:
    # Process batch
    pass
```

## 📚 API Reference

### Orchestrator API
```python
class NaramindOrchestrator:
    def __init__(self, config: ScrapingConfig)
    async def start_continuous_scraping(self)
    async def run_single_cycle(self) -> Dict
    def get_stats(self) -> Dict
    def stop(self)
```

### Scraper APIs
```python
class TwitterScraper:
    def scrape_keywords(self, keywords: List[str]) -> int
    def search_tweets(self, query: str) -> List[Dict]
    def get_user_timeline(self, user_id: str) -> List[Dict]

class TelegramScraper:
    async def scrape_channels(self) -> int
    async def search_messages(self, channel: str, query: str) -> List[Dict]
    async def setup_live_monitoring(self)

class RedditScraper:
    def scrape_subreddits(self, subreddits: List[str]) -> int
    def search_posts(self, query: str) -> List[Dict]
    def get_post_comments(self, post_id: str) -> List[Dict]
```

### Sentiment Analysis API
```python
class SentimentAnalyzer:
    def analyze(self, text: str) -> Dict
    def batch_analyze(self, texts: List[str]) -> List[Dict]
    def get_sentiment_summary(self, texts: List[str]) -> Dict
```

## 🤝 Contributing

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/Naramind-AI/naramind_social_crypto_scraper.git
cd naramind_social_crypto_scraper.git

# Create development branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
flake8 scraper/
black scraper/
```

### Code Standards
- **PEP 8**: Python code style guidelines
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Document all classes and methods
- **Testing**: Write unit tests for new features
- **Error Handling**: Comprehensive exception handling

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Submit pull request with description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Telegram Community**: [t.me/Naramind_AI](https://t.me/Naramind_AI)

### Professional Services
- **Custom Implementation**: Tailored scraping solutions
- **Enterprise Support**: 24/7 support and SLA
- **Training**: Team training and workshops
- **Consulting**: Architecture and optimization consulting

## 🙏 Acknowledgments

- **Twitter API**: For providing comprehensive social media data access
- **Telegram**: For open API enabling channel monitoring
- **Reddit**: For PRAW library and API access
- **NLTK**: For natural language processing capabilities
- **TextBlob**: For sentiment analysis functionality
- **SQLAlchemy**: For robust database ORM
- **React**: For modern web dashboard framework

---

**Disclaimer**: This scraper is designed for research and analysis purposes. Users are responsible for complying with all applicable laws and platform terms of service when using this software. Always respect rate limits and privacy guidelines.
