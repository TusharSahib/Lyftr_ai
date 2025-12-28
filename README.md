# 🚀 Lyftr AI – Full-Stack Web Scraper

**Lyftr AI** is a universal full-stack web scraper (MVP) that intelligently extracts structured content from modern websites — including JavaScript-rendered pages — and presents the results in a clean, interactive React UI.

It supports static scraping, Playwright-based rendering, user-like interactions (clicks, scrolls, pagination), and exports a schema-compliant JSON output.

---

## ✨ Key Features

- ✅ **Dual-mode scraping**
  - Static HTML scraping (BeautifulSoup)
  - JavaScript rendering with Playwright (auto fallback)

- ✅ **Smart section detection**
  - Semantic landmarks (`header`, `main`, `section`, `footer`)
  - Heading-based grouping (`h1`–`h3`)
  - Auto-labeling & type classification

- ✅ **Advanced interactions**
  - Tabs & buttons
  - “Load More” handling
  - Pagination
  - Infinite scroll (configurable depth)

- ✅ **Multi-page scraping**
  - Depth ≥ 3 with safe navigation

- ✅ **Noise filtering**
  - Cookie banners
  - Modals & overlays
  - Ads & tracking scripts

- ✅ **Schema-compliant JSON output**
  - Matches assignment specification exactly

- ✅ **Modern frontend**
  - React + Vite SPA
  - Accordion-based section viewer
  - Downloadable JSON

- ✅ **Production-ready**
  - Timeouts
  - Graceful error handling
  - Partial failure tolerance

---

## 🧰 Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI**
- **Playwright**
- **BeautifulSoup**
- **Pydantic**

### Frontend
- **React**
- **Vite**
- **Axios**
- **Modern CSS**

---

## 🚀 Quick Start (Recommended)

### Prerequisites
- Python **3.10+**
- Node.js **18+**
- ~2GB disk space (Playwright browsers)

``bash
chmod +x run.sh
./run.sh
Server starts at:

dts
Copy code
http://localhost:8000
🛠 Manual Setup (If run.sh fails)
Backend
bash
Copy code
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium

uvicorn main:app --host 0.0.0.0 --port 8000
Frontend
bash
Copy code
cd frontend
npm install
npm run build
cd ..
🖥️ Usage
Web Interface
Open http://localhost:8000

Enter a website URL

Click Scrape

View extracted sections

Expand sections to inspect JSON

Download full JSON result

🔌 API Endpoints
Health Check
bash
Copy code
curl http://localhost:8000/healthz
json
Copy code
{
  "status": "ok",
  "version": "1.0.0"
}
Scrape URL
bash
Copy code
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
Response (simplified)
json
Copy code
{
  "result": {
    "url": "https://example.com",
    "scrapedAt": "2025-12-28T23:02:00Z",
    "meta": {
      "title": "...",
      "description": "...",
      "language": "en",
      "canonical": null
    },
    "sections": [],
    "interactions": {
      "clicks": [],
      "scrolls": 0,
      "pages": []
    },
    "errors": []
  }
}
🌐 Recommended Test URLs
Static Content
https://en.wikipedia.org/wiki/Artificial_intelligence

https://developer.mozilla.org/en-US/docs/Web/JavaScript

JavaScript-Rendered
https://vercel.com

https://nextjs.org/docs

Pagination / Infinite Scroll
https://news.ycombinator.com

https://dev.to/t/javascript

https://unsplash.com/s/photos/nature

📁 Project Structure
stylus
Copy code
.
├── run.sh
├── requirements.txt
├── README.md
├── design_notes.md
├── capabilities.json
│
├── app/
│   ├── main.py
│   ├── scraper.py
│   ├── static_scraper.py
│   ├── js_scraper.py
│   ├── section_parser.py
│   ├── models.py
│   └── utils.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── App.css
│   │   └── main.jsx
│   └── dist/
🧠 Key Design Decisions
Static vs JS Rendering
First attempt: static HTML fetch

Fallback to Playwright if:

Content < 500 chars

Key selectors missing

Section Detection
Semantic landmarks

Heading hierarchy

Auto-generated labels

Section type inference (hero, faq, grid, etc.)

Interaction Strategy
Tabs: [role="tab"]

Load more: text matching

Pagination: numbered / “Next”

Infinite scroll: max 3 cycles

⚠️ Limitations
❌ Cloudflare-protected sites

❌ Login-required sites

❌ Video-only content

❌ Cross-domain crawling

⚡ Performance Notes
First run: ~3–5 seconds

Subsequent runs: ~1–3 seconds

Memory usage: ~200MB

Safe concurrency: ~5 scrapes

🧩 Environment Variables (Optional)
env
Copy code
SCRAPE_TIMEOUT=60
MAX_SCROLL_DEPTH=3
JS_RENDER_THRESHOLD=500
HEADLESS=true
🧪 Development Mode
Backend (hot reload)
bash
Copy code
uvicorn main:app --reload
Frontend (dev server)
bash
Copy code
cd frontend
npm run dev
Visit:
http://localhost:5173

📌 Submission Info
Created: December 2025

Author: Tushar Goyal

Language: Python + React

Assignment: Full-Stack Web Scraper

✅ Capabilities Summary
See capabilities.json for the full feature checklist.

📄 License
This project is provided for educational and evaluation purposes.
