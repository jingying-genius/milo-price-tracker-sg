"""
Multi-Platform Milo Price Scraper
Supports: FairPrice, Shopee, Lazada, Sheng Siong, Giant

Requirements:
pip install playwright beautifulsoup4 --break-system-packages
playwright install chromium
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re


class BaseScraper:
    """Base class for all scrapers with common utilities"""
    
    def __init__(self, platform_name, base_url, search_url):
        self.platform = platform_name
        self.base_url = base_url
        self.search_url = search_url
    
    def _categorize_milo_product(self, name):
        """Categorize Milo product into type"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['uht', 'packet', '200ml', 'tetra']):
            return 'uht'
        elif any(word in name_lower for word in ['powder', 'tin', 'refill', 'kg', 'sachet', 'gao']):
            return 'powder'
        elif any(word in name_lower for word in ['bottle', '1l', '1.5l', 'pet', 'drink']):
            return 'bottle'
        else:
            return 'other'
    
    def _extract_price(self, text):
        """Extract numeric price from text"""
        if not text:
            return 0.0
        price_text = text.replace(',', '').replace('$', '').replace('S', '')
        price_match = re.search(r'(\d+\.?\d*)', price_text)
        if price_match:
            return float(price_match.group(1))
        return 0.0


class FairPriceScraper(BaseScraper):
    """FairPrice scraper"""
    
    def __init__(self):
        super().__init__(
            'fairprice',
            'https://www.fairprice.com.sg',
            'https://www.fairprice.com.sg/search'
        )
    
    def scrape(self, headless=True, max_products=10):
        """Scrape FairPrice for Milo products"""
        print(f"\n🛒 Scraping {self.platform.upper()}...")
        products = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                url = f"{self.search_url}?query=milo"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(3)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                containers = (
                    soup.select('div[data-testid="product-container"]') or
                    soup.select('div.product-container') or
                    soup.select('div[class*="Product"]')[:max_products]
                )
                
                for container in containers[:max_products]:
                    try:
                        name_elem = (
                            container.select_one('div[data-testid="product-name"]') or
                            container.select_one('[class*="product-name"]') or
                            container.select_one('h3')
                        )
                        
                        if not name_elem:
                            continue
                        
                        name = name_elem.get_text(strip=True)
                        
                        price_elem = (
                            container.select_one('span[data-testid="product-price"]') or
                            container.select_one('[class*="price"]')
                        )
                        
                        price = self._extract_price(price_elem.get_text() if price_elem else "0")
                        
                        original_price_elem = container.select_one('[class*="original"]')
                        original_price = self._extract_price(original_price_elem.get_text() if original_price_elem else str(price))
                        
                        link_elem = container.select_one('a')
                        product_url = ""
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            product_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                        
                        products.append({
                            'name': name,
                            'type': self._categorize_milo_product(name),
                            'price': price,
                            'original_price': original_price if original_price > 0 else price,
                            'flash_sale': original_price > price and price > 0,
                            'url': product_url,
                            'platform': self.platform,
                            'scraped_at': datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            finally:
                browser.close()
        
        print(f"  ✅ Found {len(products)} products")
        return products


class ShopeeScraper(BaseScraper):
    """Shopee scraper with enhanced flash sale detection"""
    
    def __init__(self):
        super().__init__(
            'shopee',
            'https://shopee.sg',
            'https://shopee.sg/search'
        )
    
    def scrape(self, headless=True, max_products=10):
        """Scrape Shopee for Milo products with flash sale detection"""
        print(f"\n🛒 Scraping {self.platform.upper()}...")
        products = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                url = f"{self.search_url}?keyword=milo"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(5)  # Shopee needs more time for JS to load
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Shopee uses different selectors
                containers = (
                    soup.select('div[data-sqe="item"]') or
                    soup.select('div.shopee-search-item-result__item') or
                    soup.select('div[class*="item-card"]')[:max_products]
                )
                
                for container in containers[:max_products]:
                    try:
                        product = self._extract_product_with_flash_sale(container)
                        if product:
                            products.append(product)
                            
                            # Print flash sale info
                            if product['flash_sale']:
                                print(f"  ⚡ FLASH: {product['name'][:40]}... ${product['price']} (-{product['discount_percent']}%)")
                        
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            finally:
                browser.close()
        
        flash_count = sum(1 for p in products if p['flash_sale'])
        print(f"  ✅ Found {len(products)} products ({flash_count} flash sales)")
        return products
    
    def _extract_product_with_flash_sale(self, container):
        """Extract product with enhanced flash sale detection"""
        
        # Product name
        name_elem = (
            container.select_one('div[data-sqe="name"]') or
            container.select_one('div.shopee-item-card__text-name') or
            container.select_one('[class*="item-name"]') or
            container.find(text=re.compile(r'milo', re.IGNORECASE))
        )
        
        if not name_elem:
            return None
        
        name = name_elem if isinstance(name_elem, str) else name_elem.get_text(strip=True)
        
        # Price
        price_elem = (
            container.select_one('span[data-sqe="price"]') or
            container.select_one('span.shopee-item-card__current-price') or
            container.select_one('[class*="current-price"]')
        )
        
        price = self._extract_price(price_elem.get_text() if price_elem else "0")
        
        # Original price
        original_price_elem = (
            container.select_one('span[class*="original-price"]') or
            container.select_one('del') or
            container.select_one('[class*="price-before-discount"]')
        )
        
        original_price = self._extract_price(original_price_elem.get_text() if original_price_elem else str(price))
        
        # Enhanced flash sale detection
        flash_sale_info = self._detect_shopee_flash_sale(container, price, original_price)
        
        # URL
        link_elem = container.select_one('a[data-sqe="link"]') or container.select_one('a')
        product_url = ""
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            product_url = f"{self.base_url}{href}" if not href.startswith('http') else href
        
        # Discount percentage
        discount_percent = 0
        if original_price > price and price > 0:
            discount_percent = round(((original_price - price) / original_price) * 100, 1)
        
        return {
            'name': name,
            'type': self._categorize_milo_product(name),
            'price': price,
            'original_price': original_price if original_price > 0 else price,
            'flash_sale': flash_sale_info['is_flash_sale'],
            'flash_sale_type': flash_sale_info['sale_type'],
            'flash_sale_end': flash_sale_info.get('ends_at'),
            'discount_percent': discount_percent,
            'url': product_url,
            'platform': self.platform,
            'scraped_at': datetime.now().isoformat()
        }
    
    def _detect_shopee_flash_sale(self, container, current_price, original_price):
        """Detect Shopee flash sales with badges, timers, and indicators"""
        
        flash_info = {
            'is_flash_sale': False,
            'sale_type': 'normal',
            'ends_at': None
        }
        
        # Check for flash sale text indicators
        flash_indicators = [
            'flash sale', 'flash deal', 'lightning deal', 'limited time',
            'hourly sale', 'shopee live sale', 'limited offer'
        ]
        
        container_text = container.get_text().lower()
        
        for indicator in flash_indicators:
            if indicator in container_text:
                flash_info['is_flash_sale'] = True
                flash_info['sale_type'] = 'flash_sale'
                break
        
        # Check for flash sale badges
        flash_badges = container.select('[class*="flash"]') or container.select('[class*="Flash"]')
        if flash_badges:
            flash_info['is_flash_sale'] = True
            flash_info['sale_type'] = 'flash_sale'
        
        # Check for Shopee sale badges
        shopee_badges = (
            container.select('[class*="shopee-sale"]') or
            container.select('[class*="promotion"]')
        )
        if shopee_badges and not flash_info['is_flash_sale']:
            flash_info['is_flash_sale'] = True
            flash_info['sale_type'] = 'shopee_sale'
        
        # Check for countdown timer
        timer_elem = (
            container.select_one('[class*="countdown"]') or
            container.select_one('[class*="timer"]') or
            container.select_one('[class*="time-left"]')
        )
        
        if timer_elem:
            flash_info['is_flash_sale'] = True
            if flash_info['sale_type'] == 'normal':
                flash_info['sale_type'] = 'flash_sale'
            timer_text = timer_elem.get_text(strip=True)
            flash_info['ends_at'] = timer_text if timer_text else 'Soon'
        
        # Significant discount check (>20%)
        if not flash_info['is_flash_sale'] and original_price > current_price and current_price > 0:
            discount = ((original_price - current_price) / original_price) * 100
            if discount >= 20:
                flash_info['is_flash_sale'] = True
                flash_info['sale_type'] = 'discount'
        
        return flash_info


class LazadaScraper(BaseScraper):
    """Lazada scraper with enhanced flash sale detection"""
    
    def __init__(self):
        super().__init__(
            'lazada',
            'https://www.lazada.sg',
            'https://www.lazada.sg/catalog'
        )
    
    def scrape(self, headless=True, max_products=10):
        """Scrape Lazada for Milo products with flash sale detection"""
        print(f"\n🛒 Scraping {self.platform.upper()}...")
        products = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                url = f"{self.search_url}/?q=milo"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(5)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Lazada selectors
                containers = (
                    soup.select('div[data-qa-locator="product-item"]') or
                    soup.select('div.Bm3ON') or  # Lazada's product card class
                    soup.select('div[class*="product"]')[:max_products]
                )
                
                for container in containers[:max_products]:
                    try:
                        product = self._extract_product_with_flash_sale(container)
                        if product:
                            products.append(product)
                            
                            # Print flash sale info
                            if product['flash_sale']:
                                print(f"  ⚡ FLASH: {product['name'][:40]}... ${product['price']} (-{product['discount_percent']}%)")
                        
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            finally:
                browser.close()
        
        flash_count = sum(1 for p in products if p['flash_sale'])
        print(f"  ✅ Found {len(products)} products ({flash_count} flash sales)")
        return products
    
    def _extract_product_with_flash_sale(self, container):
        """Extract product with enhanced flash sale detection"""
        
        # Product name
        name_elem = (
            container.select_one('div[data-qa-locator="product-name"]') or
            container.select_one('div.RfADt') or
            container.select_one('[title]')
        )
        
        if not name_elem:
            return None
        
        name = name_elem.get('title', name_elem.get_text(strip=True))
        
        # Price
        price_elem = (
            container.select_one('span[data-qa-locator="product-price"]') or
            container.select_one('span.ooOxS') or
            container.select_one('[class*="price"]')
        )
        
        price = self._extract_price(price_elem.get_text() if price_elem else "0")
        
        # Original price
        original_price_elem = (
            container.select_one('del[class*="price"]') or
            container.select_one('[class*="original"]') or
            container.select_one('del')
        )
        
        original_price = self._extract_price(original_price_elem.get_text() if original_price_elem else str(price))
        
        # Enhanced flash sale detection
        flash_sale_info = self._detect_lazada_flash_sale(container, price, original_price)
        
        # URL
        link_elem = container.select_one('a')
        product_url = ""
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            product_url = f"{self.base_url}{href}" if not href.startswith('http') else href
        
        # Discount percentage
        discount_percent = 0
        if original_price > price and price > 0:
            discount_percent = round(((original_price - price) / original_price) * 100, 1)
        
        return {
            'name': name,
            'type': self._categorize_milo_product(name),
            'price': price,
            'original_price': original_price if original_price > 0 else price,
            'flash_sale': flash_sale_info['is_flash_sale'],
            'flash_sale_type': flash_sale_info['sale_type'],
            'flash_sale_end': flash_sale_info.get('ends_at'),
            'discount_percent': discount_percent,
            'url': product_url,
            'platform': self.platform,
            'scraped_at': datetime.now().isoformat()
        }
    
    def _detect_lazada_flash_sale(self, container, current_price, original_price):
        """Detect Lazada flash sales with LazFlash badges, timers, and indicators"""
        
        flash_info = {
            'is_flash_sale': False,
            'sale_type': 'normal',
            'ends_at': None
        }
        
        # Lazada flash sale indicators
        flash_indicators = [
            'lazflash', 'flash sale', 'flash deal', 'lightning deal',
            'limited time', 'limited quantity', 'ending soon', 'lazada sale'
        ]
        
        container_text = container.get_text().lower()
        
        for indicator in flash_indicators:
            if indicator in container_text:
                flash_info['is_flash_sale'] = True
                if 'lazflash' in indicator or 'flash' in indicator:
                    flash_info['sale_type'] = 'flash_sale'
                else:
                    flash_info['sale_type'] = 'lazada_sale'
                break
        
        # Check for flash sale badges
        flash_badges = (
            container.select('[class*="flash"]') or
            container.select('[class*="Flash"]') or
            container.select('[class*="LazFlash"]')
        )
        
        if flash_badges:
            flash_info['is_flash_sale'] = True
            flash_info['sale_type'] = 'flash_sale'
        
        # Check for sale tags
        sale_tags = (
            container.select('[class*="sale-tag"]') or
            container.select('[class*="promotion"]') or
            container.select('[class*="badge"]')
        )
        
        if sale_tags and not flash_info['is_flash_sale']:
            for tag in sale_tags:
                tag_text = tag.get_text().lower()
                if any(word in tag_text for word in ['flash', 'limited', 'ending']):
                    flash_info['is_flash_sale'] = True
                    flash_info['sale_type'] = 'flash_sale'
                    break
        
        # Check for countdown timer
        timer_elem = (
            container.select_one('[class*="countdown"]') or
            container.select_one('[class*="timer"]') or
            container.select_one('[class*="time-left"]')
        )
        
        if timer_elem:
            flash_info['is_flash_sale'] = True
            if flash_info['sale_type'] == 'normal':
                flash_info['sale_type'] = 'flash_sale'
            timer_text = timer_elem.get_text(strip=True)
            flash_info['ends_at'] = timer_text if timer_text else 'Soon'
        
        # Check for limited stock indicators
        stock_indicators = container.select('[class*="stock"]') or container.select('[class*="quantity"]')
        for indicator in stock_indicators:
            text = indicator.get_text().lower()
            if any(word in text for word in ['left', 'remaining', 'limited']):
                if not flash_info['is_flash_sale']:
                    flash_info['is_flash_sale'] = True
                    flash_info['sale_type'] = 'limited_stock'
        
        # Significant discount check (>15%)
        if not flash_info['is_flash_sale'] and original_price > current_price and current_price > 0:
            discount = ((original_price - current_price) / original_price) * 100
            if discount >= 15:
                flash_info['is_flash_sale'] = True
                flash_info['sale_type'] = 'discount'
        
        return flash_info


class ShengSiongScraper(BaseScraper):
    """Sheng Siong scraper"""
    
    def __init__(self):
        super().__init__(
            'shengsiong',
            'https://shengsiong.com.sg',
            'https://shengsiong.com.sg/search'
        )
    
    def scrape(self, headless=True, max_products=10):
        """Scrape Sheng Siong for Milo products"""
        print(f"\n🛒 Scraping {self.platform.upper()}...")
        products = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                url = f"{self.search_url}?q=milo"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(4)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Sheng Siong selectors
                containers = (
                    soup.select('div.product-item') or
                    soup.select('div[class*="product-card"]') or
                    soup.select('div[class*="Product"]')[:max_products]
                )
                
                for container in containers[:max_products]:
                    try:
                        name_elem = (
                            container.select_one('h3.product-name') or
                            container.select_one('div.product-title') or
                            container.select_one('[class*="name"]') or
                            container.select_one('h3')
                        )
                        
                        if not name_elem:
                            continue
                        
                        name = name_elem.get_text(strip=True)
                        
                        price_elem = (
                            container.select_one('span.price') or
                            container.select_one('[class*="price"]')
                        )
                        
                        price = self._extract_price(price_elem.get_text() if price_elem else "0")
                        
                        original_price_elem = container.select_one('[class*="original"]')
                        original_price = self._extract_price(original_price_elem.get_text() if original_price_elem else str(price))
                        
                        link_elem = container.select_one('a')
                        product_url = ""
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            product_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                        
                        products.append({
                            'name': name,
                            'type': self._categorize_milo_product(name),
                            'price': price,
                            'original_price': original_price if original_price > 0 else price,
                            'flash_sale': original_price > price and price > 0,
                            'url': product_url,
                            'platform': self.platform,
                            'scraped_at': datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            finally:
                browser.close()
        
        print(f"  ✅ Found {len(products)} products")
        return products


class GiantScraper(BaseScraper):
    """Giant scraper"""
    
    def __init__(self):
        super().__init__(
            'giant',
            'https://giant.sg',
            'https://giant.sg/search'
        )
    
    def scrape(self, headless=True, max_products=10):
        """Scrape Giant for Milo products"""
        print(f"\n🛒 Scraping {self.platform.upper()}...")
        products = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                url = f"{self.search_url}?q=milo"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(4)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Giant selectors
                containers = (
                    soup.select('div.product-tile') or
                    soup.select('div[class*="product-item"]') or
                    soup.select('div[class*="Product"]')[:max_products]
                )
                
                for container in containers[:max_products]:
                    try:
                        name_elem = (
                            container.select_one('h3.product-name') or
                            container.select_one('div.product-title') or
                            container.select_one('[class*="name"]') or
                            container.select_one('h3')
                        )
                        
                        if not name_elem:
                            continue
                        
                        name = name_elem.get_text(strip=True)
                        
                        price_elem = (
                            container.select_one('span.price') or
                            container.select_one('[class*="price"]')
                        )
                        
                        price = self._extract_price(price_elem.get_text() if price_elem else "0")
                        
                        original_price_elem = container.select_one('[class*="original"]')
                        original_price = self._extract_price(original_price_elem.get_text() if original_price_elem else str(price))
                        
                        link_elem = container.select_one('a')
                        product_url = ""
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            product_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                        
                        products.append({
                            'name': name,
                            'type': self._categorize_milo_product(name),
                            'price': price,
                            'original_price': original_price if original_price > 0 else price,
                            'flash_sale': original_price > price and price > 0,
                            'url': product_url,
                            'platform': self.platform,
                            'scraped_at': datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            finally:
                browser.close()
        
        print(f"  ✅ Found {len(products)} products")
        return products


def scrape_all_platforms(headless=True, max_products_per_platform=10):
    """Scrape all platforms and consolidate results"""
    
    print("\n" + "="*70)
    print("🥤 MILO PRICE TRACKER - MULTI-PLATFORM SCRAPER")
    print("="*70)
    
    scrapers = {
        'fairprice': FairPriceScraper(),
        'shopee': ShopeeScraper(),
        'lazada': LazadaScraper(),
        'shengsiong': ShengSiongScraper(),
        'giant': GiantScraper()
    }
    
    all_products = {}
    
    for platform, scraper in scrapers.items():
        try:
            products = scraper.scrape(headless=headless, max_products=max_products_per_platform)
            all_products[platform] = products
        except Exception as e:
            print(f"  ❌ Failed to scrape {platform}: {str(e)}")
            all_products[platform] = []
    
    return all_products


def main():
    """Run the multi-platform scraper"""
    
    # Scrape all platforms (set headless=False to watch it work)
    results = scrape_all_platforms(headless=False, max_products_per_platform=5)
    
    # Calculate totals
    total_products = sum(len(products) for products in results.values())
    
    # Save consolidated results
    output = {
        'scraped_at': datetime.now().isoformat(),
        'platforms': list(results.keys()),
        'total_products': total_products,
        'results': results
    }
    
    with open('/home/claude/milo_all_platforms.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SCRAPING SUMMARY")
    print("="*70)
    for platform, products in results.items():
        print(f"{platform.upper():.<20} {len(products)} products")
    print(f"{'TOTAL':.<20} {total_products} products")
    print("="*70)
    print(f"\n💾 Results saved to: milo_all_platforms.json")
    
    # Show sample products
    if total_products > 0:
        print("\n📦 SAMPLE PRODUCTS:")
        print("-"*70)
        for platform, products in results.items():
            if products:
                product = products[0]
                print(f"\n{platform.upper()}: {product['name'][:50]}...")
                print(f"  Price: ${product['price']:.2f}")
                if product['flash_sale']:
                    print(f"  ⚡ FLASH SALE (was ${product['original_price']:.2f})")


if __name__ == "__main__":
    main()
