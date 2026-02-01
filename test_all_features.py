"""
Comprehensive Test Script - Milo Price Tracker
Tests all features: scraping, flash sales, API endpoints, data consolidation
"""

import json
import time
from datetime import datetime


def print_header(title):
    """Print a nice header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_section(title):
    """Print a section header"""
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")


def test_scrapers():
    """Test 1: Run all platform scrapers"""
    print_header("TEST 1: PLATFORM SCRAPERS")
    
    from multi_platform_scraper import (
        FairPriceScraper, ShopeeScraper, LazadaScraper,
        ShengSiongScraper, GiantScraper
    )
    
    scrapers = {
        'FairPrice': FairPriceScraper(),
        'Shopee': ShopeeScraper(),
        'Lazada': LazadaScraper(),
        'Sheng Siong': ShengSiongScraper(),
        'Giant': GiantScraper()
    }
    
    results = {}
    
    for name, scraper in scrapers.items():
        print_section(f"Testing {name}")
        try:
            products = scraper.scrape(headless=True, max_products=5)
            results[name.lower().replace(' ', '')] = {
                'status': 'success',
                'product_count': len(products),
                'flash_sale_count': sum(1 for p in products if p.get('flash_sale', False)),
                'products': products
            }
            
            # Print summary
            print(f"\n  ✅ SUCCESS")
            print(f"     Products found: {len(products)}")
            print(f"     Flash sales: {results[name.lower().replace(' ', '')]['flash_sale_count']}")
            
            # Show sample product
            if products:
                sample = products[0]
                print(f"\n  📦 Sample Product:")
                print(f"     Name: {sample['name'][:50]}...")
                print(f"     Price: ${sample['price']:.2f}")
                if sample.get('flash_sale'):
                    print(f"     ⚡ FLASH SALE: {sample.get('flash_sale_type', 'unknown')}")
                    if sample.get('flash_sale_end'):
                        print(f"     Ends: {sample['flash_sale_end']}")
                    if sample.get('discount_percent'):
                        print(f"     Discount: {sample['discount_percent']}%")
        
        except Exception as e:
            results[name.lower().replace(' ', '')] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"\n  ❌ FAILED: {str(e)}")
    
    # Save results
    with open('/home/claude/test_results_scrapers.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


def test_flash_sale_detection(scraper_results):
    """Test 2: Flash sale detection accuracy"""
    print_header("TEST 2: FLASH SALE DETECTION")
    
    total_products = 0
    total_flash_sales = 0
    flash_sale_details = []
    
    for platform, data in scraper_results.items():
        if data['status'] == 'success':
            products = data['products']
            total_products += len(products)
            
            for product in products:
                if product.get('flash_sale'):
                    total_flash_sales += 1
                    flash_sale_details.append({
                        'platform': platform,
                        'name': product['name'],
                        'price': product['price'],
                        'original_price': product.get('original_price', product['price']),
                        'flash_sale_type': product.get('flash_sale_type', 'unknown'),
                        'flash_sale_end': product.get('flash_sale_end'),
                        'discount_percent': product.get('discount_percent', 0)
                    })
    
    print(f"\n  📊 FLASH SALE STATISTICS:")
    print(f"     Total products scraped: {total_products}")
    print(f"     Products on flash sale: {total_flash_sales}")
    print(f"     Flash sale rate: {(total_flash_sales/total_products*100) if total_products > 0 else 0:.1f}%")
    
    if flash_sale_details:
        print(f"\n  ⚡ FLASH SALE DETAILS:")
        for i, sale in enumerate(flash_sale_details, 1):
            print(f"\n     {i}. {sale['platform'].upper()}")
            print(f"        Product: {sale['name'][:45]}...")
            print(f"        Price: ${sale['price']:.2f} (was ${sale['original_price']:.2f})")
            print(f"        Type: {sale['flash_sale_type']}")
            print(f"        Discount: {sale['discount_percent']}%")
            if sale['flash_sale_end']:
                print(f"        Ends: {sale['flash_sale_end']}")
    else:
        print(f"\n  ℹ️  No flash sales found (this is normal if not during sale hours)")
    
    # Save results
    with open('/home/claude/test_results_flash_sales.json', 'w') as f:
        json.dump({
            'total_products': total_products,
            'total_flash_sales': total_flash_sales,
            'flash_sale_rate': (total_flash_sales/total_products*100) if total_products > 0 else 0,
            'flash_sale_details': flash_sale_details
        }, f, indent=2)
    
    return flash_sale_details


def test_backend_api():
    """Test 3: Backend API endpoints"""
    print_header("TEST 3: BACKEND API (requires server running)")
    
    import requests
    
    base_url = "http://localhost:5000"
    
    endpoints = {
        '/': 'API Info',
        '/api/status': 'Status Check',
        '/api/products': 'All Products',
        '/api/products/shopee': 'Shopee Products',
        '/api/best-deals': 'Best Deals',
        '/api/flash-sales': 'Flash Sales Only'
    }
    
    results = {}
    
    print("\n  💡 Make sure backend is running: python complete_backend.py")
    print("     Press Enter to start testing, or Ctrl+C to skip...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n  ⏭️  Skipping API tests")
        return {}
    
    for endpoint, name in endpoints.items():
        print_section(f"Testing {name} ({endpoint})")
        
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    'status': 'success',
                    'response': data
                }
                print(f"  ✅ SUCCESS (200 OK)")
                
                # Print relevant info
                if endpoint == '/api/status':
                    print(f"     Cache status: {data.get('cache_status')}")
                    print(f"     Cached products: {data.get('cached_products')}")
                elif endpoint == '/api/products':
                    print(f"     Products: {len(data.get('products', []))}")
                    print(f"     Platforms: {', '.join(data.get('platforms', []))}")
                elif endpoint == '/api/flash-sales':
                    print(f"     Flash sales: {data.get('total_flash_sales', 0)}")
                    print(f"     Platforms: {', '.join(data.get('platforms_with_flash_sales', []))}")
                elif endpoint == '/api/best-deals':
                    print(f"     Deals found: {len(data.get('best_deals', []))}")
                    print(f"     Total savings: ${data.get('total_potential_savings', 0):.2f}")
            else:
                results[endpoint] = {
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}"
                }
                print(f"  ❌ FAILED ({response.status_code})")
        
        except Exception as e:
            results[endpoint] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ FAILED: {str(e)}")
    
    # Save results
    with open('/home/claude/test_results_api.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


def test_data_quality(scraper_results):
    """Test 4: Data quality checks"""
    print_header("TEST 4: DATA QUALITY")
    
    issues = []
    warnings = []
    
    for platform, data in scraper_results.items():
        if data['status'] != 'success':
            continue
        
        products = data['products']
        
        for product in products:
            # Check for missing data
            if not product.get('name'):
                issues.append(f"{platform}: Product missing name")
            
            if product.get('price', 0) <= 0:
                issues.append(f"{platform}: Invalid price for {product.get('name', 'unknown')}")
            
            if not product.get('url'):
                warnings.append(f"{platform}: Missing URL for {product.get('name', 'unknown')[:30]}...")
            
            # Check flash sale data consistency
            if product.get('flash_sale'):
                if not product.get('flash_sale_type'):
                    warnings.append(f"{platform}: Flash sale missing type for {product.get('name', 'unknown')[:30]}...")
                
                original = product.get('original_price', 0)
                current = product.get('price', 0)
                
                if original > 0 and current > 0:
                    if current >= original:
                        warnings.append(f"{platform}: Flash sale price not lower than original for {product.get('name', 'unknown')[:30]}...")
    
    print(f"\n  🔍 DATA QUALITY REPORT:")
    print(f"     Issues found: {len(issues)}")
    print(f"     Warnings: {len(warnings)}")
    
    if issues:
        print(f"\n  ❌ ISSUES:")
        for issue in issues[:10]:  # Show first 10
            print(f"     • {issue}")
    
    if warnings:
        print(f"\n  ⚠️  WARNINGS:")
        for warning in warnings[:10]:  # Show first 10
            print(f"     • {warning}")
    
    if not issues and not warnings:
        print(f"\n  ✅ All data quality checks passed!")
    
    # Save results
    with open('/home/claude/test_results_quality.json', 'w') as f:
        json.dump({
            'issues': issues,
            'warnings': warnings,
            'issues_count': len(issues),
            'warnings_count': len(warnings)
        }, f, indent=2)
    
    return {'issues': issues, 'warnings': warnings}


def generate_final_report(scraper_results, flash_sale_data, api_results, quality_data):
    """Generate final comprehensive test report"""
    print_header("FINAL TEST REPORT")
    
    # Scraper summary
    print_section("SCRAPER RESULTS")
    scrapers_working = sum(1 for r in scraper_results.values() if r['status'] == 'success')
    scrapers_total = len(scraper_results)
    print(f"  Working: {scrapers_working}/{scrapers_total}")
    
    for platform, data in scraper_results.items():
        status = "✅" if data['status'] == 'success' else "❌"
        print(f"    {status} {platform.upper()}")
    
    # Flash sale summary
    print_section("FLASH SALE DETECTION")
    flash_sale_count = len(flash_sale_data) if flash_sale_data else 0
    print(f"  Flash sales detected: {flash_sale_count}")
    
    if flash_sale_count > 0:
        platforms_with_flash = set(f['platform'] for f in flash_sale_data)
        print(f"  Platforms with flash sales: {', '.join(platforms_with_flash)}")
    
    # API summary
    if api_results:
        print_section("API ENDPOINTS")
        api_working = sum(1 for r in api_results.values() if r['status'] == 'success')
        api_total = len(api_results)
        print(f"  Working: {api_working}/{api_total}")
    
    # Quality summary
    print_section("DATA QUALITY")
    print(f"  Issues: {quality_data['issues_count']}")
    print(f"  Warnings: {quality_data['warnings_count']}")
    
    # Overall status
    print_section("OVERALL STATUS")
    
    all_good = (
        scrapers_working >= 3 and  # At least 3 scrapers working
        quality_data['issues_count'] == 0  # No critical issues
    )
    
    if all_good:
        print("  🎉 ALL SYSTEMS GO! Everything is working great!")
    elif scrapers_working >= 2:
        print("  ⚠️  MOSTLY WORKING - Some features need attention")
    else:
        print("  ❌ NEEDS ATTENTION - Multiple systems not working")
    
    # Save complete report
    report = {
        'test_date': datetime.now().isoformat(),
        'scrapers': {
            'working': scrapers_working,
            'total': scrapers_total,
            'results': scraper_results
        },
        'flash_sales': {
            'count': flash_sale_count,
            'data': flash_sale_data
        },
        'api': {
            'working': len([r for r in api_results.values() if r['status'] == 'success']) if api_results else 0,
            'total': len(api_results) if api_results else 0,
            'results': api_results
        },
        'quality': quality_data,
        'overall_status': 'good' if all_good else 'needs_attention'
    }
    
    with open('/home/claude/FINAL_TEST_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n  📄 Full report saved to: FINAL_TEST_REPORT.json")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  🥤 MILO PRICE TRACKER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\n  This will test:")
    print("    1. All platform scrapers (FairPrice, Shopee, Lazada, Sheng Siong, Giant)")
    print("    2. Flash sale detection")
    print("    3. Backend API endpoints")
    print("    4. Data quality")
    print("\n  Duration: ~3-5 minutes")
    print("  Output: Test results saved to JSON files")
    print("\n" + "="*70)
    
    start_time = time.time()
    
    # Run tests
    scraper_results = test_scrapers()
    flash_sale_data = test_flash_sale_detection(scraper_results)
    api_results = test_backend_api()
    quality_data = test_data_quality(scraper_results)
    
    # Generate report
    generate_final_report(scraper_results, flash_sale_data, api_results, quality_data)
    
    elapsed = time.time() - start_time
    
    print(f"\n  ⏱️  Total test time: {elapsed:.1f} seconds")
    print("\n" + "="*70)
    print("  TESTING COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
