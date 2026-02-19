"""
Market Intelligence Module
Handles sentiment analysis, news monitoring, and Fear & Greed Index
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    print("Warning: newsapi-python not available. News features will be limited.")

from config import Config


class MarketIntelligence:
    """Market intelligence and sentiment analysis"""
    
    def __init__(self):
        """Initialize market intelligence"""
        self.config = Config
        self.news_client = None
        
        if NEWSAPI_AVAILABLE and Config.NEWS_API_KEY:
            try:
                self.news_client = NewsApiClient(api_key=Config.NEWS_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize NewsAPI client: {e}")
        
        self.fear_greed_cache = None
        self.fear_greed_cache_time = None
    
    def get_fear_greed_index(self) -> Dict[str, any]:
        """Get Fear & Greed Index from alternative.me API"""
        # Check cache (update every hour)
        if self.fear_greed_cache and self.fear_greed_cache_time:
            time_diff = (datetime.utcnow() - self.fear_greed_cache_time).total_seconds()
            if time_diff < self.config.FEAR_GREED_UPDATE_INTERVAL:
                return self.fear_greed_cache
        
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    fng_data = data['data'][0]
                    
                    value = int(fng_data['value'])
                    classification = fng_data['value_classification']
                    
                    result = {
                        'value': value,
                        'classification': classification,
                        'timestamp': datetime.utcnow().isoformat(),
                        'normalized_score': self._normalize_fear_greed(value)
                    }
                    
                    # Update cache
                    self.fear_greed_cache = result
                    self.fear_greed_cache_time = datetime.utcnow()
                    
                    return result
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
        
        # Return neutral values if API fails
        return {
            'value': 50,
            'classification': 'Neutral',
            'timestamp': datetime.utcnow().isoformat(),
            'normalized_score': 0
        }
    
    def _normalize_fear_greed(self, value: int) -> float:
        """Normalize Fear & Greed Index to -1 to 1 scale"""
        # 0-24: Extreme Fear (-1 to -0.5)
        # 25-44: Fear (-0.5 to -0.1)
        # 45-55: Neutral (-0.1 to 0.1)
        # 56-75: Greed (0.1 to 0.5)
        # 76-100: Extreme Greed (0.5 to 1)
        
        if value < 25:
            return -1 + (value / 25) * 0.5
        elif value < 45:
            return -0.5 + ((value - 25) / 20) * 0.4
        elif value < 55:
            return -0.1 + ((value - 45) / 10) * 0.2
        elif value < 75:
            return 0.1 + ((value - 55) / 20) * 0.4
        else:
            return 0.5 + ((value - 75) / 25) * 0.5
    
    def get_crypto_news(self, symbols: List[str] = None, hours: int = 24) -> List[Dict]:
        """Fetch recent cryptocurrency news"""
        if not self.news_client:
            return self._get_mock_news()
        
        try:
            # Build query
            keywords = ['cryptocurrency', 'crypto', 'bitcoin', 'blockchain']
            if symbols:
                # Add specific crypto names
                symbol_map = {
                    'BTC': 'bitcoin',
                    'ETH': 'ethereum',
                    'BNB': 'binance',
                    'XRP': 'ripple',
                    'ADA': 'cardano',
                    'SOL': 'solana',
                    'DOGE': 'dogecoin',
                    'DOT': 'polkadot',
                    'LTC': 'litecoin'
                }
                for symbol in symbols:
                    crypto_name = symbol_map.get(symbol.replace('USDT', ''))
                    if crypto_name:
                        keywords.append(crypto_name)
            
            query = ' OR '.join(keywords[:5])  # Limit query size
            
            # Fetch news
            from_date = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            articles = self.news_client.get_everything(
                q=query,
                from_param=from_date,
                language='en',
                sort_by='publishedAt',
                page_size=20
            )
            
            news_list = []
            for article in articles.get('articles', []):
                news_list.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'sentiment_score': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', '')),
                })
            
            return news_list
        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._get_mock_news()
    
    def _get_mock_news(self) -> List[Dict]:
        """Return mock news data when API is not available"""
        return [
            {
                'title': 'Cryptocurrency Market Update',
                'description': 'Market showing mixed signals',
                'source': 'Mock Source',
                'url': '',
                'published_at': datetime.utcnow().isoformat(),
                'sentiment_score': 0.0
            }
        ]
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis of text"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Simple keyword-based sentiment
        positive_words = ['bullish', 'gain', 'rise', 'surge', 'rally', 'growth', 'profit', 
                         'positive', 'strong', 'breakthrough', 'adoption', 'success']
        negative_words = ['bearish', 'loss', 'fall', 'crash', 'decline', 'drop', 'negative',
                         'weak', 'concern', 'risk', 'threat', 'failure', 'scam']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total
        return max(-1, min(1, sentiment))
    
    def get_overall_sentiment(self, news_articles: List[Dict] = None, 
                            fear_greed: Dict = None) -> Dict[str, float]:
        """Calculate overall market sentiment"""
        if news_articles is None:
            news_articles = self.get_crypto_news(hours=12)
        
        if fear_greed is None:
            fear_greed = self.get_fear_greed_index()
        
        # Calculate news sentiment
        if news_articles:
            news_sentiments = [article.get('sentiment_score', 0) for article in news_articles]
            avg_news_sentiment = sum(news_sentiments) / len(news_sentiments)
        else:
            avg_news_sentiment = 0
        
        # Get Fear & Greed sentiment
        fg_sentiment = fear_greed.get('normalized_score', 0)
        
        # Weighted combination (60% F&G, 40% News)
        overall_sentiment = (fg_sentiment * 0.6) + (avg_news_sentiment * 0.4)
        
        return {
            'overall_sentiment': overall_sentiment,
            'news_sentiment': avg_news_sentiment,
            'fear_greed_sentiment': fg_sentiment,
            'fear_greed_value': fear_greed.get('value', 50),
            'fear_greed_classification': fear_greed.get('classification', 'Neutral'),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_sentiment_score(self, overall_sentiment: Dict = None) -> Tuple[float, str]:
        """
        Calculate sentiment score (0-20 points) for trading signal
        
        Scoring:
        - Extreme Fear (-1 to -0.6): 20 points (contrarian buy)
        - Fear (-0.6 to -0.2): 15 points (buy)
        - Neutral (-0.2 to 0.2): 10 points
        - Greed (0.2 to 0.6): 15 points (sell)
        - Extreme Greed (0.6 to 1): 20 points (contrarian sell)
        """
        if overall_sentiment is None:
            overall_sentiment = self.get_overall_sentiment()
        
        sentiment_value = overall_sentiment.get('overall_sentiment', 0)
        
        # Contrarian approach: Extreme fear is buying opportunity
        if sentiment_value < -0.6:
            return 20, 'EXTREME_FEAR_BUY'
        elif sentiment_value < -0.2:
            return 15, 'FEAR_BUY'
        elif sentiment_value < 0.2:
            return 10, 'NEUTRAL'
        elif sentiment_value < 0.6:
            return 12, 'GREED_CAUTION'
        else:
            return 8, 'EXTREME_GREED_SELL'
    
    def get_social_sentiment(self, symbol: str) -> Dict[str, any]:
        """Get social media sentiment (placeholder for future implementation)"""
        # This would integrate with Twitter API, Reddit API, etc.
        # For now, return neutral sentiment
        return {
            'symbol': symbol,
            'sentiment_score': 0.0,
            'mentions_count': 0,
            'trending': False,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_market_intelligence_summary(self) -> Dict[str, any]:
        """Get comprehensive market intelligence summary"""
        fear_greed = self.get_fear_greed_index()
        news = self.get_crypto_news(hours=24)
        overall_sentiment = self.get_overall_sentiment(news, fear_greed)
        sentiment_score, sentiment_signal = self.calculate_sentiment_score(overall_sentiment)
        
        return {
            'fear_greed_index': fear_greed,
            'recent_news_count': len(news),
            'overall_sentiment': overall_sentiment,
            'sentiment_score': sentiment_score,
            'sentiment_signal': sentiment_signal,
            'timestamp': datetime.utcnow().isoformat()
        }
