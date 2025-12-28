Lyftr AI Full-Stack Web Scraper
A universal website scraper (MVP) with intelligent content extraction, JS rendering, interaction handling, and a modern JSON viewer frontend.
Features
* ✅ Dual-mode scraping: Static HTML + Playwright JS rendering with smart fallback
* ✅ Smart section detection: Auto-grouping by landmarks, headings, and semantic elements
* ✅ Advanced interactions: Tab clicking, "Load More" buttons, pagination, infinite scroll
* ✅ Depth ≥ 3: Multi-page scraping with automatic navigation
* ✅ Noise filtering: Removes cookie banners, modals, overlays
* ✅ Schema compliance: Exact JSON structure per assignment spec
* ✅ Modern frontend: React SPA with Vite for interactive JSON viewing
* ✅ Production-ready: Error handling, timeouts, graceful degradation
Quick Start
Prerequisites
* Python 3.10+
* Node.js 18+ (for frontend)
* ~2GB disk space (for Playwright browsers)
Installation & Run

bash
chmod +x run.sh
./run.sh
The server will start on http://localhost:8000
Manual Setup (if run.sh fails)

bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Build frontend (one-time)
cd frontend
npm install
npm run build
cd ..

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
Usage
Web Interface
1. Open http://localhost:8000 in your browser
2. Enter a URL
3. Click "Scrape"
4. View sections in accordion format
5. Expand sections to see full JSON
6. Download complete JSON result
API Endpoints
Health Check

bash
curl http://localhost:8000/healthz
# Response: { "status": "ok", "version": "1.0.0" }
Scrape URL

bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
Response structure:

json
{
  "result": {
    "url": "https://example.com",
    "scrapedAt": "2025-12-28T23:02:00Z",
    "meta": { "title": "...", "description": "...", "language": "en", "canonical": null },
    "sections": [ { ... } ],
    "interactions": { "clicks": [], "scrolls": 0, "pages": ["https://example.com"] },
    "errors": []
  }
}
Testing URLs (Recommended)
Static Content
* https://en.wikipedia.org/wiki/Artificial_intelligence — Complete static page with sections and tables
* https://developer.mozilla.org/en-US/docs/Web/JavaScript — Static docs with headings and code
JavaScript-Rendered
* https://vercel.com/ — JS-heavy marketing site with tabs and dynamic content
* https://nextjs.org/docs — Dynamic docs with navigation
Pagination/Infinite Scroll
* https://news.ycombinator.com/ — Pagination links to multiple pages
* https://dev.to/t/javascript — Infinite scroll with lazy loading
* https://unsplash.com/s/photos/nature — Grid with infinite scroll
Project Structure

text
.
├── run.sh                          # Quick start script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── design_notes.md                 # Architecture & strategy
├── capabilities.json               # Feature compliance checklist
│
├── app/
│   ├── main.py                    # FastAPI app & static serving
│   ├── scraper.py                 # Core scraper logic
│   ├── static_scraper.py          # Static HTML extraction
│   ├── js_scraper.py              # Playwright JS rendering
│   ├── section_parser.py          # Section detection & parsing
│   ├── models.py                  # Pydantic models/schemas
│   └── utils.py                   # Helper functions
│
├── frontend/
│   ├── package.json               # Frontend dependencies
│   ├── vite.config.js             # Vite configuration
│   ├── index.html                 # HTML entry point
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── components/
│   │   │   ├── ScrapeForm.jsx     # URL input form
│   │   │   ├── SectionViewer.jsx  # Section display
│   │   │   └── JSONViewer.jsx     # JSON expandable tree
│   │   ├── App.css                # Global styles
│   │   └── main.jsx               # React entry point
│   └── dist/                      # Built frontend (auto-generated)
│
└── .gitignore
Key Design Decisions
Static vs JS Rendering
* First attempt: HTTP fetch + Beautiful Soup (fast, efficient)
* Fallback trigger: If main content < 500 chars or missing expected selectors
* JS rendering: Playwright with network idle + 2-second timeout
Section Detection
1. Group by semantic landmarks: <header>, <nav>, <main>, <section>, <footer>
2. Further subdivide by heading hierarchy (h1-h3)
3. Auto-label from first 5-7 words of content
4. Type detection: hero, nav, section, list, grid, faq, pricing, footer
Interaction Strategy
* Tab detection: [role="tab"] and <button aria-controls>
* Load More: Text matching "load more", "show more", "view more"
* Pagination: Follow <a rel="next"> or numbered pagination links
* Infinite Scroll: Scroll down, wait for network idle, repeat max 3x
Noise Filtering
Removed elements:
* Cookie/consent banners: .cookie-*, [data-consent]
* Newsletter modals: .newsletter-*, .modal-*
* Advertisements: .ad-*, [data-ad]
* Tracking scripts: <script> (non-inline)
Limitations & Known Issues
Current Scope
* ✅ Single-domain scraping (no cross-domain navigation)
* ✅ Chromium-only (fast, lightweight)
* ✅ Max 60-second timeout per scrape
* ✅ Max 50MB content per page
Sites That May Fail
* ❌ Cloudflare-protected sites — Blocks Playwright
* ❌ Sites requiring login — Not in scope
* ❌ Interactive 3D content — Not extracted
* ❌ Video-only sites — Metadata only, no transcription
Browser Detection
* Some sites detect Playwright headless flag → returns limited HTML
* Mitigation: Setting realistic user-agent headers
Performance Notes
* First scrape: ~3-5 seconds (browser startup)
* Subsequent scrapes: ~1-3 seconds (reused browser context)
* Memory usage: ~200MB for backend + browser
* Concurrency: Can handle ~5 concurrent scrapes safely
Troubleshooting
"Browser not found" Error

bash
python -m playwright install chromium
"Address already in use" (Port 8000)

bash
# Use different port
uvicorn app.main:app --port 8001
Slow startup on first run
* First build downloads Playwright browsers (~300MB)
* Subsequent runs use cached browsers
* Run once and it will be fast thereafter
Frontend not loading

bash
cd frontend
npm install
npm run build
cd ..
Capabilities Summary
See capabilities.json for detailed feature checklist.
* Static scraping: ✅ Implemented
* JS rendering: ✅ Implemented with fallback
* Click interactions (tabs): ✅ Implemented
* Load more clicks: ✅ Implemented
* Pagination: ✅ Implemented
* Infinite scroll: ✅ Implemented
* Noise filtering: ✅ Implemented
* HTML truncation: ✅ Implemented
API Schema Compliance
All required fields per assignment spec:
* ✅ result.url — exact match to input
* ✅ result.scrapedAt — ISO8601 UTC
* ✅ result.meta — title, description, language, canonical
* ✅ result.sections — full array with all required fields
* ✅ result.interactions — clicks, scrolls, pages
* ✅ result.errors — graceful error collection
Environment Variables (Optional)
Create .env file for custom config:

text
SCRAPE_TIMEOUT=60
MAX_SCROLL_DEPTH=3
JS_RENDER_THRESHOLD=500
HEADLESS=true
Development
Run with hot reload (backend)

bash
uvicorn app.main:app --reload
Run with hot reload (frontend)

bash
cd frontend
npm run dev
Then visit http://localhost:5173 (frontend dev server) and ensure it proxies to backend on 8000.
Submission Info
Created: December 2025 Language: Python 3.10+ / React Testing URLs:
1. https://en.wikipedia.org/wiki/Artificial_intelligence — Static content
2. https://vercel.com/ — JS-heavy with tabs
3. https://news.ycombinator.com/ — Pagination to depth 3
