import React, { useState, useEffect } from 'react';
import { Activity, Database, MessageCircle, TrendingUp, AlertCircle, Shield, Settings, BarChart3 } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalPosts: 15847,
    positiveSentiment: 68,
    negativeSentiment: 23,
    neutralSentiment: 9,
    activeKeywords: 142,
    platforms: ['Twitter', 'Telegram', 'Reddit']
  });

  const [recentPosts, setRecentPosts] = useState([
    {
      id: 1,
      platform: 'Twitter',
      content: 'Bitcoin breaking new resistance levels! #BTC #crypto',
      sentiment: 'positive',
      score: 0.85,
      timestamp: '2 minutes ago',
      author: '@cryptotrader123',
      keywords: ['Bitcoin', 'BTC', 'resistance']
    },
    {
      id: 2,
      platform: 'Telegram',
      content: 'Ethereum upgrade looking promising for DeFi protocols',
      sentiment: 'positive',
      score: 0.72,
      timestamp: '5 minutes ago',
      author: 'DeFi_Channel',
      keywords: ['Ethereum', 'DeFi', 'upgrade']
    },
    {
      id: 3,
      platform: 'Reddit',
      content: 'Market volatility concerns rising among investors',
      sentiment: 'negative',
      score: -0.64,
      timestamp: '8 minutes ago',
      author: 'r/CryptoCurrency',
      keywords: ['volatility', 'market', 'investors']
    }
  ]);

  const getSentimentColor = (sentiment) => {
    switch(sentiment) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      case 'neutral': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getPlatformIcon = (platform) => {
    switch(platform) {
      case 'Twitter': return '🐦';
      case 'Telegram': return '✈️';
      case 'Reddit': return '🔗';
      default: return '📱';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-8 h-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">Naramind</h1>
              </div>
              <span className="text-sm text-gray-500">Social Media Crypto Intelligence</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live Monitoring</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {[
              { key: 'overview', label: 'Overview', icon: BarChart3 },
              { key: 'posts', label: 'Live Posts', icon: MessageCircle },
              { key: 'sentiment', label: 'Sentiment', icon: TrendingUp },
              { key: 'settings', label: 'Settings', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Posts</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.totalPosts.toLocaleString()}</p>
                  </div>
                  <Database className="w-8 h-8 text-blue-600" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Positive Sentiment</p>
                    <p className="text-3xl font-bold text-green-600">{stats.positiveSentiment}%</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-600" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Active Keywords</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.activeKeywords}</p>
                  </div>
                  <MessageCircle className="w-8 h-8 text-purple-600" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Platforms</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.platforms.length}</p>
                  </div>
                  <Shield className="w-8 h-8 text-indigo-600" />
                </div>
              </div>
            </div>

            {/* Platform Status */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-medium text-gray-900">Platform Status</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {stats.platforms.map((platform) => (
                    <div key={platform} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{getPlatformIcon(platform)}</span>
                        <div>
                          <p className="font-medium text-gray-900">{platform}</p>
                          <p className="text-sm text-gray-500">Active</p>
                        </div>
                      </div>
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'posts' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-medium text-gray-900">Recent Posts</h3>
              </div>
              <div className="divide-y">
                {recentPosts.map((post) => (
                  <div key={post.id} className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-lg">{getPlatformIcon(post.platform)}</span>
                          <span className="text-sm font-medium text-gray-900">{post.platform}</span>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm text-gray-500">{post.author}</span>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm text-gray-500">{post.timestamp}</span>
                        </div>
                        <p className="text-gray-900 mb-3">{post.content}</p>
                        <div className="flex items-center space-x-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(post.sentiment)}`}>
                            {post.sentiment} ({post.score > 0 ? '+' : ''}{post.score})
                          </span>
                          <div className="flex items-center space-x-1">
                            {post.keywords.map((keyword, idx) => (
                              <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'sentiment' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Distribution</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Positive</span>
                  <span className="text-sm font-medium text-green-600">{stats.positiveSentiment}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{width: `${stats.positiveSentiment}%`}}></div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Negative</span>
                  <span className="text-sm font-medium text-red-600">{stats.negativeSentiment}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{width: `${stats.negativeSentiment}%`}}></div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Neutral</span>
                  <span className="text-sm font-medium text-gray-600">{stats.neutralSentiment}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gray-500 h-2 rounded-full" style={{width: `${stats.neutralSentiment}%`}}></div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Trending Keywords</h3>
              <div className="space-y-3">
                {['Bitcoin', 'Ethereum', 'DeFi', 'NFT', 'Altcoins', 'Blockchain'].map((keyword, idx) => (
                  <div key={keyword} className="flex items-center justify-between">
                    <span className="text-sm text-gray-900">{keyword}</span>
                    <span className="text-xs text-gray-500">{Math.floor(Math.random() * 1000) + 100} mentions</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-medium text-gray-900">Monitoring Configuration</h3>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Keywords to Monitor</label>
                <textarea
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="3"
                  placeholder="Bitcoin, Ethereum, DeFi, NFT, Altcoins..."
                  defaultValue="Bitcoin, Ethereum, DeFi, NFT, Altcoins, Blockchain, Web3, Crypto"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Influencers to Track</label>
                <textarea
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="3"
                  placeholder="@elonmusk, @VitalikButerin, @cz_binance..."
                  defaultValue="@elonmusk, @VitalikButerin, @cz_binance, @aantonop, @SatoshiLite"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-900">Twitter Monitoring</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-900">Telegram Monitoring</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-900">Reddit Monitoring</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;