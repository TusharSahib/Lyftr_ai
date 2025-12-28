import React, { useState } from 'react'

function ScrapeForm({ onScrape, loading }) {
  const [url, setUrl] = useState('')
  const [urlError, setUrlError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    setUrlError('')

    if (!url.trim()) {
      setUrlError('Please enter a URL')
      return
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setUrlError('URL must start with http:// or https://')
      return
    }

    onScrape(url)
  }

  return (
    <div className="scrape-form-container">
      <form onSubmit={handleSubmit} className="scrape-form">
        <div className="form-group">
          <label htmlFor="url">Website URL</label>
          <input
            id="url"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            disabled={loading}
            className={urlError ? 'error' : ''}
          />
          {urlError && <span className="error-text">{urlError}</span>}
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="btn btn-primary btn-large"
        >
          {loading ? '⏳ Scraping...' : '🔍 Scrape Now'}
        </button>
      </form>

      <div className="suggested-urls">
        <p className="text-muted">Try these URLs:</p>
        <div className="url-chips">
          <button 
            className="url-chip"
            onClick={() => setUrl('https://en.wikipedia.org/wiki/Artificial_intelligence')}
          >
            Wikipedia (Static)
          </button>
          <button 
            className="url-chip"
            onClick={() => setUrl('https://vercel.com/')}
          >
            Vercel (JS-Heavy)
          </button>
          <button 
            className="url-chip"
            onClick={() => setUrl('https://news.ycombinator.com/')}
          >
            HackerNews (Pagination)
          </button>
        </div>
      </div>
    </div>
  )
}

export default ScrapeForm