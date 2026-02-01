"""
Milo Price Tracker - Complete Backend API
Integrates: FairPrice, Shopee, Lazada, Sheng Siong, Giant

To run:
pip install flask flask-cors playwright beautifulsoup4 apscheduler --break-system-packages
playwright install chromium
python complete_backend.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
from multi_platform_scraper import (
    FairPriceScraper, ShopeeScraper, LazadaScraper,
    ShengSiongScraper, GiantScraper
)
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
CORS(app)

# In-memory cache (use Redis or database in production)
cache = {
    'products': [],
    'last_updated': None,
    'by_platform': {}
}

CACHE_DURATION = 3600  # 1 hour


def get_cached_data():
    """Get cached data if still valid"""
    if cache['last_updated']:
        elapsed = (datetime.now() - cache['last_updated']).seconds
        if elapsed < CACHE_DURATION:
            return cache['products']
    return None


def update_cache(products):
    """Update cache with new data"""
    cache['products'] = products
    cache['last_updated'] = datetime.now()


def scrape_all_platforms():
    """Scrape all platforms and consolidate results"""
    print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] Starting scheduled scrape...")
    
    scrapers = {
        'fairprice': FairPriceScraper(),
        'shopee': ShopeeScraper(),
        'lazada': LazadaScraper(),
        'shengsiong': ShengSiongScraper(),
        'giant': GiantScraper()
    }
    
    all_products_by_platform = {}
    
    for platform_name, scraper in scrapers.items():
        try:
            products = scraper.scrape(headless=True, max_products=10)
            all_products_by_platform[platform_name] = products
            cache['by_platform'][platform_name] = products
        except Exception as e:
            print(f"  ❌ {platform_name}: {str(e)}")
            all_products_by_platform[platform_name] = []
    
    # Consolidate into comparison format
    consolidated = consolidate_products(all_products_by_platform)
    update_cache(consolidated)
    
    total = sum(len(products) for products in all_products_by_platform.values())
    print(f"  ✅ Scraping complete: {total} products across {len(scrapers)} platforms")
    
    return consolidated


def consolidate_products(products_by_platform):
    """
    Consolidate products from different platforms into comparison format
    
    This is simplified - in production you'd use fuzzy matching or ML
    to properly match same products across platforms
    """
    
    # For now, just group by similar names
    # In production, implement proper product matching algorithm
    
    consolidated = []
    product_id = 1
    
    # Get all unique product names (simplified matching)
    all_products = []
    for platform, products in products_by_platform.items():
        for product in products:
            all_products.append(product)
    
    # Group by rough name similarity (first 20 chars for demo)
    # TODO: Implement proper fuzzy matching
    seen_names = {}
    
    for product in all_products:
        # Simple key: first 20 chars lowercase, no spaces
        key = product['name'][:20].lower().replace(' ', '')
        
        if key not in seen_names:
            seen_names[key] = {
                'id': product_id,
                'name': product['name'],
                'type': product['type'],
                'prices': []
            }
            product_id += 1
        
        # Preserve all flash sale info
        price_info = {
            'platform': product['platform'],
            'price': product['price'],
            'originalPrice': product['original_price'],
            'flashSale': product['flash_sale'],
            'url': product['url']
        }
        
        # Add flash sale details if available
        if 'flash_sale_type' in product:
            price_info['flashSaleType'] = product['flash_sale_type']
        if 'flash_sale_end' in product and product['flash_sale_end']:
            price_info['flashSaleEnd'] = product['flash_sale_end']
        if 'discount_percent' in product:
            price_info['discountPercent'] = product['discount_percent']
        
        seen_names[key]['prices'].append(price_info)
    
    consolidated = list(seen_names.values())
    return consolidated


# API Routes

@app.route('/')
def home():
    """API home"""
    return jsonify({
        'name': 'Milo Price Tracker API',
        'version': '2.0',
        'platforms': ['fairprice', 'shopee', 'lazada', 'shengsiong', 'giant'],
        'endpoints': {
            'GET /api/products': 'Get all products with prices',
            'GET /api/products/:platform': 'Get products from specific platform',
            'POST /api/scrape': 'Trigger fresh scrape',
            'GET /api/status': 'Check API status',
            'GET /api/best-deals': 'Get best deals across platforms'
        }
    })


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with prices from all platforms"""
    
    # Check cache
    cached_data = get_cached_data()
    if cached_data:
        return jsonify({
            'products': cached_data,
            'lastUpdated': cache['last_updated'].isoformat(),
            'source': 'cache',
            'platforms': list(cache['by_platform'].keys())
        })
    
    # Scrape fresh data
    try:
        products = scrape_all_platforms()
        
        return jsonify({
            'products': products,
            'lastUpdated': datetime.now().isoformat(),
            'source': 'fresh_scrape',
            'platforms': list(cache['by_platform'].keys())
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Scraping failed',
            'products': []
        }), 500


@app.route('/api/products/<platform>', methods=['GET'])
def get_platform_products(platform):
    """Get products from specific platform"""
    
    valid_platforms = ['fairprice', 'shopee', 'lazada', 'shengsiong', 'giant']
    
    if platform not in valid_platforms:
        return jsonify({
            'error': f'Invalid platform. Choose from: {", ".join(valid_platforms)}'
        }), 400
    
    if platform in cache['by_platform']:
        return jsonify({
            'platform': platform,
            'products': cache['by_platform'][platform],
            'lastUpdated': cache['last_updated'].isoformat() if cache['last_updated'] else None
        })
    
    # Scrape specific platform
    scrapers = {
        'fairprice': FairPriceScraper(),
        'shopee': ShopeeScraper(),
        'lazada': LazadaScraper(),
        'shengsiong': ShengSiongScraper(),
        'giant': GiantScraper()
    }
    
    try:
        scraper = scrapers[platform]
        products = scraper.scrape(headless=True, max_products=10)
        
        return jsonify({
            'platform': platform,
            'products': products,
            'count': len(products),
            'lastUpdated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'platform': platform
        }), 500


@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger a fresh scrape of all platforms"""
    try:
        products = scrape_all_platforms()
        
        return jsonify({
            'status': 'success',
            'products_scraped': len(products),
            'platforms': list(cache['by_platform'].keys()),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/best-deals', methods=['GET'])
def get_best_deals():
    """Get the best deals (lowest prices) across all platforms"""
    
    cached_data = get_cached_data()
    if not cached_data:
        # Try to scrape
        cached_data = scrape_all_platforms()
    
    # Find best deals
    best_deals = []
    
    for product in cached_data:
        if len(product['prices']) > 1:
            # Sort by price
            sorted_prices = sorted(product['prices'], key=lambda x: x['price'])
            best_price = sorted_prices[0]
            worst_price = sorted_prices[-1]
            
            savings = worst_price['price'] - best_price['price']
            
            if savings > 0:
                best_deals.append({
                    'product': product['name'],
                    'best_platform': best_price['platform'],
                    'best_price': best_price['price'],
                    'worst_platform': worst_price['platform'],
                    'worst_price': worst_price['price'],
                    'savings': round(savings, 2),
                    'savings_percent': round((savings / worst_price['price']) * 100, 1)
                })
    
    # Sort by savings (highest first)
    best_deals.sort(key=lambda x: x['savings'], reverse=True)
    
    return jsonify({
        'best_deals': best_deals[:10],  # Top 10
        'total_potential_savings': round(sum(d['savings'] for d in best_deals), 2)
    })


@app.route('/api/flash-sales', methods=['GET'])
def get_flash_sales():
    """Get ONLY products that are currently on flash sale"""
    
    cached_data = get_cached_data()
    if not cached_data:
        # Try to scrape
        cached_data = scrape_all_platforms()
    
    # Find flash sales
    flash_sales = []
    
    for product in cached_data:
        # Check if any platform has this on flash sale
        flash_sale_prices = [p for p in product['prices'] if p.get('flashSale')]
        
        if flash_sale_prices:
            # Sort by price (cheapest flash sale first)
            flash_sale_prices.sort(key=lambda x: x['price'])
            best_flash_sale = flash_sale_prices[0]
            
            flash_sales.append({
                'product': product['name'],
                'type': product['type'],
                'platform': best_flash_sale['platform'],
                'price': best_flash_sale['price'],
                'original_price': best_flash_sale.get('originalPrice', best_flash_sale['price']),
                'discount_percent': best_flash_sale.get('discountPercent', 0),
                'flash_sale_type': best_flash_sale.get('flashSaleType', 'flash_sale'),
                'flash_sale_end': best_flash_sale.get('flashSaleEnd'),
                'url': best_flash_sale['url'],
                'all_platforms': [{
                    'platform': p['platform'],
                    'price': p['price'],
                    'is_flash_sale': p.get('flashSale', False),
                    'flash_sale_type': p.get('flashSaleType')
                } for p in product['prices']]
            })
    
    # Sort by discount percentage (best deals first)
    flash_sales.sort(key=lambda x: x['discount_percent'], reverse=True)
    
    return jsonify({
        'flash_sales': flash_sales,
        'total_flash_sales': len(flash_sales),
        'platforms_with_flash_sales': list(set(f['platform'] for f in flash_sales))
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get API status"""
    
    platform_stats = {}
    for platform, products in cache['by_platform'].items():
        platform_stats[platform] = len(products)
    
    return jsonify({
        'status': 'running',
        'cache_status': 'active' if cache['last_updated'] else 'empty',
        'last_updated': cache['last_updated'].isoformat() if cache['last_updated'] else None,
        'cached_products': len(cache['products']),
        'cache_age_seconds': (datetime.now() - cache['last_updated']).seconds if cache['last_updated'] else None,
        'platforms': platform_stats
    })


# Scheduled scraping
def init_scheduler():
    """Initialize background scheduler for automatic scraping"""
    scheduler = BackgroundScheduler()
    
    # Scrape every hour
    scheduler.add_job(
        func=scrape_all_platforms,
        trigger="interval",
        hours=1,
        id='scrape_job',
        name='Scrape all platforms',
        replace_existing=True
    )
    
    scheduler.start()
    
    # Shut down scheduler on app exit
    atexit.register(lambda: scheduler.shutdown())
    
    print("⏰ Scheduler initialized - scraping every hour")


if __name__ == '__main__':
    import os
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║     🥤 Milo Price Tracker API - ALL PLATFORMS INTEGRATED     ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    ✅ Integrated Platforms:
    ┌─────────────────────────────────────────────────────────────┐
    │  1. FairPrice    - Singapore's trusted supermarket          │
    │  2. Shopee       - Leading e-commerce platform              │
    │  3. Lazada       - Major online marketplace                 │
    │  4. Sheng Siong  - Value-for-money supermarket              │
    │  5. Giant        - Wide variety at great prices             │
    └─────────────────────────────────────────────────────────────┘
    
    📡 API Endpoints:
    ┌─────────────────────────────────────────────────────────────┐
    │ GET  /                          - API info                  │
    │ GET  /api/products              - All products              │
    │ GET  /api/products/<platform>   - Platform-specific         │
    │ POST /api/scrape                - Trigger fresh scrape      │
    │ GET  /api/best-deals            - Top 10 savings            │
    │ GET  /api/status                - API status                │
    └─────────────────────────────────────────────────────────────┘
    
    ⏰ Auto-scraping: Every 1 hour
    💾 Cache duration: 1 hour
    🌐 Server: http://0.0.0.0:{}
    
    Starting server...
    """.format(port))
    
    # Initialize scheduler for automatic scraping
    init_scheduler()
    
    # Run initial scrape
    print("\n🚀 Running initial scrape...")
    try:
        scrape_all_platforms()
    except Exception as e:
        print(f"⚠️  Initial scrape failed: {str(e)}")
        print("   Will retry on first API request or after 1 hour")
    
    # Start Flask server
    # Use debug=False in production (Railway)
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
    app.run(
        debug=not is_production, 
        host='0.0.0.0', 
        port=port, 
        use_reloader=False
    )
