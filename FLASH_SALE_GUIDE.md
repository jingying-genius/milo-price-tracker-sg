# ⚡ Flash Sale Detection - Complete Guide

## 🎯 Current Implementation

### Basic Detection (In multi_platform_scraper.py)

**What it does:**
```python
flash_sale = original_price > price and price > 0
```

**Limitations:**
- ❌ Only checks if current price < original price
- ❌ Doesn't detect actual "Flash Sale" badges
- ❌ Misses time-limited deals without price changes
- ❌ Can't distinguish between flash sales vs regular discounts

## 🔥 Enhanced Detection (NEW - In enhanced_flash_sale_scraper.py)

### For Shopee

**Detects:**
1. ✅ **Flash Sale Badges** - Looks for "Flash Sale", "Flash Deal", "Lightning Deal" text
2. ✅ **Countdown Timers** - Detects timer elements showing when sale ends
3. ✅ **Shopee Sale Tags** - Special Shopee promotion indicators
4. ✅ **Price Discounts** - Significant discounts (>20%)
5. ✅ **Limited Time Offers** - "Limited Time", "Hourly Sale" indicators

**Sale Types Identified:**
- `flash_sale` - Actual flash sales with badges/timers
- `shopee_sale` - Shopee-wide promotions (9.9, 11.11, etc.)
- `discount` - Regular discount (>20% off)
- `normal` - No special sale

**Example Output:**
```json
{
  "name": "Milo UHT 200ML X 24",
  "price": 9.88,
  "original_price": 19.00,
  "flash_sale": true,
  "flash_sale_type": "flash_sale",
  "flash_sale_end": "2h 15m",
  "discount_percent": 48.0,
  "platform": "shopee"
}
```

### For Lazada

**Detects:**
1. ✅ **LazFlash Badges** - Lazada's flash sale program
2. ✅ **Flash Sale Tags** - "Flash Sale", "Lightning Deal" labels
3. ✅ **Countdown Timers** - Time remaining indicators
4. ✅ **Limited Stock** - "X items left", "Limited quantity"
5. ✅ **Price Discounts** - Significant discounts (>15%)

**Sale Types Identified:**
- `flash_sale` - LazFlash or flash deals
- `lazada_sale` - Lazada-wide promotions
- `limited_stock` - Limited quantity deals
- `discount` - Regular discount (>15% off)
- `normal` - No special sale

**Example Output:**
```json
{
  "name": "Milo Powder 2kg",
  "price": 17.95,
  "original_price": 24.90,
  "flash_sale": true,
  "flash_sale_type": "flash_sale",
  "flash_sale_end": "Ends in 1h 30m",
  "discount_percent": 27.9,
  "platform": "lazada"
}
```

## 📊 Detection Strategy

### Shopee Flash Sale Indicators

```python
# Text-based indicators
flash_indicators = [
    'flash sale',
    'flash deal',
    'lightning deal',
    'limited time',
    'hourly sale',
    'shopee live sale'
]

# HTML class-based
flash_badges = container.select('[class*="flash"]')
shopee_badges = container.select('[class*="shopee-sale"]')
timer = container.select_one('[class*="countdown"]')
```

### Lazada Flash Sale Indicators

```python
# Text-based indicators
flash_indicators = [
    'lazflash',
    'flash sale',
    'flash deal',
    'lightning deal',
    'limited time',
    'limited quantity',
    'ending soon',
    'lazada sale'
]

# HTML class-based
flash_badges = container.select('[class*="LazFlash"]')
timer = container.select_one('[class*="countdown"]')
stock = container.select('[class*="stock"]')
```

## 🔍 How Flash Sales Work on Each Platform

### Shopee Flash Sales

**Types:**
1. **Hourly Flash Deals** - Change every hour (12pm, 1pm, 2pm, etc.)
2. **Shopee Live Sales** - During live streaming sessions
3. **9.9 / 11.11 / 12.12 Sales** - Major sale events
4. **Lightning Deals** - Very short duration (15-30 min)

**How to Spot:**
- Orange "Flash Sale" badge
- Countdown timer in red
- Limited stock counter
- Special pricing valid for limited time

**Example on Shopee:**
```
[FLASH SALE] ⚡
Milo UHT 200ml x 24
$9.88 (was $19.00)
⏰ Ends in 2h 15m
🔥 Only 15 left!
```

### Lazada Flash Sales

**Types:**
1. **LazFlash** - Lazada's official flash sale program
2. **Lightning Deals** - Time-limited offers
3. **11.11 / 12.12 Campaigns** - Mega sale events
4. **Limited Quantity Deals** - "X items only at this price"

**How to Spot:**
- "LazFlash" badge
- Timer showing time left
- "Limited time offer" tag
- Stock counter ("Only X left")

**Example on Lazada:**
```
[LAZFLASH] ⚡
Milo Activ-Go 2kg
$17.95 (was $24.90) -28%
⏰ 1h 30m left
📦 Only 8 items left
```

## 🎯 Flash Sale vs Regular Discount

### Flash Sale Characteristics:
- ⏰ **Time-limited** - Usually 1-4 hours
- 📊 **Limited stock** - Specific quantity allocated
- 🏷️ **Special badge** - "Flash Sale", "LazFlash" indicator
- ⏱️ **Countdown timer** - Shows urgency
- 💰 **Deep discount** - Usually >20% off

### Regular Discount Characteristics:
- 📅 **Longer duration** - Days or weeks
- 🔄 **Unlimited stock** - No quantity limit
- 🏷️ **Generic badge** - Just shows discount %
- ❌ **No timer** - No urgency indicator
- 💵 **Moderate discount** - Usually 10-20% off

## 📈 Using the Enhanced Scraper

### Test It:
```bash
python enhanced_flash_sale_scraper.py
```

This will:
1. Scrape Shopee for Milo products
2. Scrape Lazada for Milo products
3. Identify which are flash sales
4. Show sale type, discount %, and end time
5. Save results to `flash_sale_test.json`

### Integrate into Backend:

Replace the basic scrapers in `multi_platform_scraper.py` with the enhanced versions:

```python
# Replace ShopeeScraper with EnhancedShopeeScraper
# Replace LazadaScraper with EnhancedLazadaScraper
```

## 💡 Frontend Display Ideas

### Show Flash Sales Prominently:

```javascript
// In your frontend
if (product.flash_sale) {
    // Add special styling
    productCard.classList.add('flash-sale');
    
    // Show flash sale badge
    badge.innerHTML = `⚡ ${product.flash_sale_type.toUpperCase()}`;
    
    // Show countdown if available
    if (product.flash_sale_end) {
        timer.innerHTML = `⏰ Ends: ${product.flash_sale_end}`;
    }
    
    // Show discount percentage
    discount.innerHTML = `-${product.discount_percent}%`;
}
```

### Sort by Flash Sales:

```javascript
// Show flash sales first
products.sort((a, b) => {
    if (a.flash_sale && !b.flash_sale) return -1;
    if (!a.flash_sale && b.flash_sale) return 1;
    return b.discount_percent - a.discount_percent;
});
```

### Flash Sale Notifications:

```javascript
// Alert users about flash sales
const flashSales = products.filter(p => p.flash_sale);
if (flashSales.length > 0) {
    showNotification(`🔥 ${flashSales.length} flash sales available!`);
}
```

## 🎨 Visual Indicators

### Recommended Styling:

**Flash Sale Badge:**
```css
.flash-sale-badge {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-weight: 700;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
```

**Countdown Timer:**
```css
.countdown-timer {
    background: #FF4444;
    color: white;
    padding: 0.5rem;
    border-radius: 10px;
    font-family: monospace;
    font-weight: bold;
}
```

## 📊 Comparison Table

| Feature | Basic Detection | Enhanced Detection |
|---------|----------------|-------------------|
| Price comparison | ✅ | ✅ |
| Flash sale badges | ❌ | ✅ |
| Countdown timers | ❌ | ✅ |
| Sale type identification | ❌ | ✅ |
| End time extraction | ❌ | ✅ |
| Stock indicators | ❌ | ✅ |
| Discount % | ❌ | ✅ |
| Platform-specific sales | ❌ | ✅ |

## 🚀 Next Steps

### Immediate:
1. Test enhanced scraper on live sites
2. Verify flash sale detection accuracy
3. Update backend to use enhanced scrapers
4. Update frontend to display flash sale info

### Advanced:
1. **Price alerts** - Notify when flash sales start
2. **Historical tracking** - Track which products go on flash sale often
3. **Best time to buy** - Analyze when flash sales happen
4. **Auto-purchase** - Alert when favorite items flash sale (don't auto-buy, just alert!)

## ⚠️ Important Notes

### Limitations:
- Flash sale detection relies on HTML structure
- Platforms may change their HTML at any time
- Timers show relative time ("2h 15m"), not exact end time
- Some flash sales may not have all indicators

### Best Practices:
- Run scrapers frequently during sale periods (9.9, 11.11, etc.)
- Cache flash sale data for shorter periods (15-30 min)
- Verify flash sales before notifying users
- Account for timezone differences

### Testing:
Best times to test flash sale detection:
- **Shopee**: Every hour (12pm, 1pm, 2pm, etc.)
- **Lazada**: 10am-2pm, 8pm-11pm (peak flash sale times)
- **Major sales**: 9.9, 11.11, 12.12 events

## 🎯 Summary

**Basic Scraper:**
- ✅ Good enough for general price comparison
- ❌ Misses actual flash sale indicators

**Enhanced Scraper:**
- ✅ Detects real flash sales with badges/timers
- ✅ Identifies sale types (flash vs regular)
- ✅ Extracts countdown timers
- ✅ Calculates discount percentages
- ✅ Platform-specific detection

**Recommendation:**
Use enhanced scraper for production - it provides much richer data and accurately identifies genuine flash sales vs regular discounts!
