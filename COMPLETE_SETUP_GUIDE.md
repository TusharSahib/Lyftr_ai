Complete Setup & File Structure Guide
Project Overview
Lyftr AI Full-Stack Web Scraper is a production-ready web scraping application with:
* Intelligent static/JS rendering fallback strategy
* Advanced interaction handling (tabs, load more, pagination, infinite scroll)
* Beautiful React frontend with JSON viewer
* Full compliance with Lyftr AI assignment schema

Directory Structure

text
lyftr-scraper/
│
├── run.sh                          # 🟢 START HERE - Quick launch script
├── requirements.txt                # Python dependencies
├── README.md                       # Full documentation
├── design_notes.md                 # Architecture & strategy details
├── capabilities.json               # Feature checklist
├── .gitignore                      # Git ignore rules
│
├── app/                            # 🔧 BACKEND PACKAGE
│   ├── __init__.py                 # Package init
│   ├── main.py                     # FastAPI app + health/scrape endpoints
│   ├── models.py                   # Pydantic schema models
│   ├── scraper.py                  # Main orchestrator (static + JS fallback)
│   ├── static_scraper.py           # Static HTML fetching (httpx)
│   ├── js_scraper.py               # JS rendering + interactions (Playwright)
│   ├── section_parser.py           # HTML → sections parsing
│   └── utils.py                    # Helper functions
│
└── frontend/                       # 🎨 FRONTEND PACKAGE
    ├── package.json                # Node dependencies
    ├── vite.config.js              # Vite configuration
    ├── index.html                  # HTML entry point
    ├── src/
    │   ├── main.jsx                # React entry point
    │   ├── App.jsx                 # Main app component
    │   ├── App.css                 # Global styles
    │   └── components/
    │       ├── ScrapeForm.jsx       # URL input form
    │       ├── SectionViewer.jsx    # Section display
    │       └── JSONViewer.jsx       # Expandable JSON tree
    │
    └── dist/                       # Built frontend (auto-generated)
        ├── index.html              # Production HTML
        └── assets/                 # JS/CSS bundles

File Descriptions
Root Files
run.sh (Shell Script)
* Creates Python virtual environment
* Installs backend + frontend dependencies
* Builds React frontend
* Launches FastAPI server on port 8000
* Run this first: chmod +x run.sh && ./run.sh
requirements.txt (Python Dependencies)

text
fastapi==0.109.0              # Web framework
uvicorn[standard]==0.27.0     # ASGI server
httpx==0.26.0                 # Async HTTP client
beautifulsoup4==4.12.2        # HTML parsing
playwright==1.40.0            # Browser automation
lxml==4.9.3                   # XML/HTML parser
pydantic==2.5.0               # Data validation
python-dotenv==1.0.0          # Environment variables
Backend (app/)
app/main.py
* FastAPI application setup
* /healthz endpoint → returns {"status": "ok"}
* /scrape endpoint → POST with {"url": "..."}
* Serves static frontend files
* CORS middleware for frontend communication
app/models.py
* Pydantic models defining exact schema
* ScraperResult - complete output
* Section, Metadata, Interactions, ScraperError
* Built-in validation and JSON serialization
app/scraper.py (Main Orchestrator)

python
class WebScraper:
    async def scrape(url) → ScraperResult
        ├─ Stage 1: Static fetch with httpx
        ├─ Check content quality
        ├─ If insufficient → Stage 2: Playwright JS rendering
        ├─ Parse sections from HTML
        ├─ Extract metadata
        ├─ Handle interactions (clicks, scrolls, pagination)
        └─ Return structured JSON
app/static_scraper.py
* Fast HTTP fetch using httpx
* Realistic user-agent headers
* 10-second timeout
* Returns raw HTML
app/js_scraper.py
* Playwright-based JavaScript rendering
* Sophisticated interaction handling:
    * Tab clicking with [role="tab"]
    * "Load More" button detection and clicking
    * Pagination link following (depth ≥ 3)
    * Infinite scroll detection (height comparison)
* Wait strategies:
    1. Network idle (best)
    2. Selector wait (fallback)
    3. Fixed 2-second sleep (last resort)
app/section_parser.py
* Converts HTML → semantic sections
* Grouping strategy:
    1. Landmark elements: <header>, <nav>, <main>, <footer>
    2. Heading-based: <h1>, <h2>, <h3>
    3. Content blocks: significant <div> elements
* Type detection: hero, nav, section, list, grid, faq, pricing, footer, unknown
* Auto-labeling from first 5-7 words
* Link absolutization
* Image extraction
* Table parsing
app/utils.py
* make_absolute_url() - relative → absolute conversion
* same_domain() - URL domain matching
* truncate_html() - preserve structure while truncating
* clean_text() - normalize whitespace
Frontend (frontend/)
frontend/package.json

json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "scripts": {
    "dev": "vite",           // Dev server
    "build": "vite build",   // Production build
    "preview": "vite preview" // Preview build
  }
}
frontend/src/App.jsx (Main React Component)
* URL input form with validation
* Scraping state management
* Results display with tabs:
    * Sections accordion
    * Metadata grid
    * Interactions summary
* JSON download functionality
* Error/loading states
frontend/src/App.css (Complete Styling)
* Modern gradient design
* Responsive layout
* JSON syntax highlighting
* Accessible forms and buttons
* Mobile-friendly
frontend/src/components/
* ScrapeForm.jsx - URL input + suggested URLs
* SectionViewer.jsx - Section card display
* JSONViewer.jsx - Expandable JSON tree with syntax coloring

Setup Instructions
Prerequisites

bash
# Check versions
python3 --version      # 3.10+
node --version         # 18+
npm --version          # 8+
Option 1: Quick Start (Recommended)

bash
git clone <repo-url>
cd lyftr-scraper
chmod +x run.sh
./run.sh
Then visit http://localhost:8000 in your browser.
Option 2: Manual Setup

bash
# Backend setup
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install chromium

# Frontend setup
cd frontend
npm install
npm run build
cd ..

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000

API Endpoints
Health Check

bash
curl http://localhost:8000/healthz

Response:
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-12-28T23:02:00Z"
}
Scrape URL

bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

Response:
{
  "result": {
    "url": "https://example.com",
    "scrapedAt": "2025-12-28T23:02:00Z",
    "meta": { "title": "...", "description": "...", ... },
    "sections": [ ... ],
    "interactions": { "clicks": [], "scrolls": 0, "pages": [...] },
    "errors": []
  }
}

Testing
Provided Test URLs
1. Static Content
    * https://en.wikipedia.org/wiki/Artificial_intelligence
    * Expected: Landmark sections + h2 grouping
    * Strategy: Static only (no JS needed)
2. JavaScript-Heavy
    * https://vercel.com/
    * Expected: Tab interactions, dynamic content
    * Strategy: JS rendering triggered
3. Pagination/Scroll
    * https://news.ycombinator.com/
    * Expected: Multiple pages (depth ≥ 3)
    * Strategy: Pagination link following
Test Locally

bash
# Test health
curl http://localhost:8000/healthz

# Test with your URL
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-url.com"}'

Configuration
Environment Variables (Optional)
Create .env file in project root:

text
# Timeouts (seconds)
SCRAPE_TIMEOUT=60
FETCH_TIMEOUT=10
RENDER_TIMEOUT=15

# Thresholds
STATIC_CONTENT_MIN_LENGTH=500
JS_RENDER_THRESHOLD=500

# Browser
HEADLESS=true
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

Performance Notes
* First scrape: 3-5 seconds (browser startup)
* Subsequent scrapes: 1-3 seconds
* Memory: ~200MB for backend + browser
* Concurrency: Safe for 5 concurrent scrapes

Troubleshooting
Issue	Solution
"Browser not found"	Run: python -m playwright install chromium
"Port 8000 in use"	Change port: uvicorn app.main:app --port 8001
Frontend blank	Run: cd frontend && npm install && npm run build
"No sections found"	Try a different URL; check backend logs
JavaScript timeout	Some sites block Playwright; check errors[]
Key Implementation Details
Static vs JS Decision
Score calculation:
* Base score = text length
* +300 if has <main> or <article>
* +200 if has h1-h3 heading
* Threshold: 500 points
If score < threshold → trigger JS rendering
Section Type Detection
* Hero: heading + image in header area
* Nav: navigation elements or menu
* List: multiple <ul> or <ol> items
* Grid: 4+ images in layout
* FAQ: question/answer pattern or "faq" in label
* Pricing: currency symbols + table rows
* Footer: in <footer> or "copyright" text
* Section: default type
Interaction Strategies
1. Tabs: Click [role='tab'] and button[aria-controls]
2. Load More: Match text patterns "load more", "show more", etc.
3. Pagination: Follow <a rel="next"> links (max 3 pages)
4. Infinite Scroll: Monitor scroll height changes (max 3 scrolls)
Noise Filtering
Removed elements:
* .cookie-banner, .cookie-notice
* .modal, .popup, [role="dialog"]
* [data-ad-slot], .ad-container
* .newsletter-popup, .modal-backdrop

Deployment
Heroku

bash
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
Docker

text
FROM python:3.11-slim
RUN apt-get update && apt-get install -y nodejs npm
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python -m playwright install chromium
RUN cd frontend && npm install && npm run build && cd ..
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

Support & Debugging
Enable Debug Logging

python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
Check Logs

bash
# Tail server logs
tail -f server.log
Verify Schema Compliance
Response object includes:
* ✅ url - exact match
* ✅ scrapedAt - ISO8601
* ✅ meta - title, description, language, canonical
* ✅ sections - array with all required fields
* ✅ interactions - clicks, scrolls, pages
* ✅ errors - error objects with phase

Credits
Built for: Lyftr AI Full-Stack Assignment Version: 1.0.0 Last Updated: December 2025

Quick Reference
Command	Purpose
./run.sh	Start everything
curl http://localhost:8000/healthz	Check server
curl -X POST http://localhost:8000/scrape -d '{"url":"..."}' -H "Content-Type: application/json"	Scrape URL
http://localhost:8000	Open frontend
Ctrl+C	Stop server
cd frontend && npm run build	Rebuild frontend
python -m playwright install chromium	Setup browser
Ready to scrape? Run ./run.sh and visit http://localhost:8000! 🚀
