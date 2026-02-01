# 🥤 Milo Price Tracker - Singapore

A full-stack price tracking application that monitors Milo products across Shopee, Lazada, and FairPrice Online to help you find the best deals.

## 📁 What You Have

1. **milo-tracker.html** - Beautiful, fully functional frontend (works standalone with mock data)
2. **milo_tracker_backend.py** - Python backend template for real scraping
3. **README.md** - This file

## 🚀 Quick Start (Frontend Only)

The easiest way to see it in action:

1. Simply open `milo-tracker.html` in your web browser
2. That's it! It works with simulated data

The frontend currently shows mock data and simulates price updates every 10 seconds so you can see how it would work in real-time.

## 🔧 Full Stack Setup (With Real Scraping)

### Prerequisites

- Python 3.8+
- pip
- Modern web browser

### Step 1: Install Python Dependencies

```bash
pip install flask flask-cors requests beautifulsoup4 playwright --break-system-packages

# Install Playwright browsers
playwright install
```

### Step 2: Implement the Scrapers

Open `milo_tracker_backend.py` and implement the scraping logic in these methods:
- `scrape_shopee()` - Scrape Shopee.sg
- `scrape_lazada()` - Scrape Lazada.sg  
- `scrape_fairprice()` - Scrape FairPrice Online

Each method has detailed comments explaining what to do.

### Step 3: Run the Backend

```bash
python milo_tracker_backend.py
```

The API will start on http://localhost:5000

### Step 4: Connect Frontend to Backend

Update the frontend to fetch from your API instead of using mock data. In `milo-tracker.html`, replace the `mockData` object with:

```javascript
async function fetchProducts() {
    const response = await fetch('http://localhost:5000/api/products');
    const data = await response.json();
    return data;
}

async function init() {
    const data = await fetchProducts();
    mockData = data; // Replace mock data with real data
    document.getElementById('lastUpdate').textContent = data.lastUpdated;
    renderProducts();
    calculateSavings();
}
```

## 🎯 Features

### Current (Working Now)
- ✅ Beautiful, responsive UI with Milo-themed design
- ✅ Filter products by type (UHT, Powder, Bottles)
- ✅ Real-time price comparison across platforms
- ✅ Highlights best deals
- ✅ Shows flash sales
- ✅ Calculates potential savings
- ✅ Animated, smooth interactions

### To Implement (Backend)
- ⏳ Real scraping from Shopee, Lazada, FairPrice
- ⏳ Product matching across platforms
- ⏳ Database storage (PostgreSQL)
- ⏳ Price history tracking
- ⏳ Scheduled scraping (every hour)
- ⏳ Price drop alerts (email/Telegram)
- ⏳ Charts showing price trends over time

## 🔍 How Product Matching Works

The trickiest part is matching the same product across different platforms since they use different naming:

**Example:**
- Shopee: "Milo Chocolate Malt Milk UHT 200ml x 24"
- Lazada: "MILO UHT Packet 200ML*24 - Case"
- FairPrice: "Milo UHT 200ml (24-pack)"

**Strategies:**
1. Extract key attributes (brand, type, size, quantity)
2. Fuzzy string matching (using fuzzywuzzy library)
3. Use Claude API to help normalize product names
4. Manual mapping for popular products
5. Build confidence scores and flag uncertain matches for review

## 📊 Technical Architecture

```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │  ← Beautiful UI, filters, animations
└────────┬────────┘
         │
         │ HTTP Requests
         │
┌────────▼────────┐
│   Flask API     │
│  (Python)       │  ← REST endpoints
└────────┬────────┘
         │
    ┌────┴────┐
    │ Scrapers│
    └────┬────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Shopee │  │ Lazada │  │FairPrice│
└────────┘  └────────┘  └────────┘
```

## 🛠️ Scraping Challenges & Solutions

### Challenge 1: Anti-Scraping Measures
**Solution:** 
- Use Playwright (headless browser) instead of requests
- Add random delays between requests
- Rotate user agents
- Respect robots.txt

### Challenge 2: Dynamic Content (JavaScript)
**Solution:**
- Use Playwright to wait for content to load
- Look for specific selectors that indicate page is ready

### Challenge 3: Rate Limiting
**Solution:**
- Implement exponential backoff
- Cache results for 1 hour
- Scrape during off-peak hours

### Challenge 4: Changing HTML Structure
**Solution:**
- Use multiple selectors as fallbacks
- Test scrapers regularly
- Set up alerts when scrapers fail

## 📅 Recommended Scraping Schedule

- **Regular products:** Every 6 hours
- **Flash sale times:** Every 30 minutes
- **Major sale days (11.11, 12.12):** Every 15 minutes

## 💾 Database Schema (Recommended)

```sql
-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500),
    type VARCHAR(50),  -- 'uht', 'powder', 'bottle'
    normalized_name VARCHAR(500),  -- For matching
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prices table (historical tracking)
CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    platform VARCHAR(50),  -- 'shopee', 'lazada', 'fairprice'
    price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    flash_sale BOOLEAN,
    url TEXT,
    scraped_at TIMESTAMP DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX idx_prices_product_date ON prices(product_id, scraped_at);
```

## 🚨 Legal Considerations

**Important:** Web scraping can violate Terms of Service. Consider:

1. **Check ToS:** Read each platform's Terms of Service
2. **robots.txt:** Respect robots.txt directives
3. **Rate limiting:** Don't overwhelm their servers
4. **Personal use vs Commercial:** This impacts legality
5. **API alternatives:** Check if they offer official APIs

For personal use and small scale, you're usually fine. For commercial use, consult a lawyer.

## 📱 Future Enhancements

- **Mobile app:** React Native version
- **Browser extension:** Quick price check while browsing
- **Telegram bot:** Price alerts via Telegram
- **More products:** Expand beyond Milo
- **More stores:** Add Giant, Sheng Siong, Cold Storage
- **Price predictions:** ML model to predict future prices
- **Shopping list:** Track multiple products you want to buy

## 🤝 Contributing

Want to improve this? Here's what needs work:

1. Implement actual scraping logic
2. Add database integration
3. Build price history charts
4. Add user authentication (for saving favorite products)
5. Implement email/Telegram alerts

## 📝 Notes from Jing

This is a fully working prototype! The frontend is production-ready and works beautifully right now with mock data.

The backend is a well-structured template - you just need to fill in the actual scraping logic. I've left detailed comments showing you exactly what needs to be done.

The hardest part will be the product matching across platforms. You might want to start by manually mapping the top 10-20 most popular Milo products, then build the automated matching for the long tail.

Let me know if you want me to:
1. Build actual scraping code for one platform as an example
2. Add more features to the frontend (price history charts, alerts, etc.)
3. Set up database integration
4. Deploy this somewhere (Heroku, Railway, etc.)

Have fun tracking those Milo deals! 🥤✨
