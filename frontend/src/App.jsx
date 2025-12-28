import React, { useState } from 'react'
import axios from 'axios'
import './App.css'
import ScrapeForm from './components/ScrapeForm'
import SectionViewer from './components/SectionViewer'
import JSONViewer from './components/JSONViewer'

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [expandedSection, setExpandedSection] = useState(null)

  const handleScrape = async (url) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setExpandedSection(null)

    try {
      const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

      const response = await axios.post(`${API_BASE}/scrape`, { url })

      setResult(response.data.result)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Scraping failed')
    } finally {
      setLoading(false)
    }
  }

  const downloadJSON = () => {
    if (!result) return
    
    const json = JSON.stringify(result, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `scrape-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🚀 Lyftr AI Web Scraper</h1>
          <p>Universal website scraper with intelligent content extraction</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {/* Form Section */}
          <ScrapeForm onScrape={handleScrape} loading={loading} />

          {/* Error Section */}
          {error && (
            <div className="error-box">
              <h3>❌ Error</h3>
              <p>{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="loading-box">
              <div className="spinner"></div>
              <p>Scraping website...</p>
            </div>
          )}

          {/* Result Section */}
          {result && !loading && (
            <div className="result-section">
              {/* Header with actions */}
              <div className="result-header">
                <div>
                  <h2>✅ Scrape Complete</h2>
                  <p className="meta-info">
                    <strong>URL:</strong> {result.url}<br/>
                    <strong>Scraped:</strong> {new Date(result.scrapedAt).toLocaleString()}<br/>
                    <strong>Sections:</strong> {result.sections.length} | 
                    <strong> Pages Visited:</strong> {result.interactions.pages.length} | 
                    <strong> Scroll Actions:</strong> {result.interactions.scrolls}
                  </p>
                </div>
                <button className="btn btn-primary" onClick={downloadJSON}>
                  📥 Download JSON
                </button>
              </div>

              {/* Tabs */}
              <div className="tabs">
                <button className="tab-btn active">Sections</button>
                <button className="tab-btn">Metadata</button>
                <button className="tab-btn">Interactions</button>
              </div>

              {/* Sections Accordion */}
              <div className="sections-container">
                <h3>Page Sections ({result.sections.length})</h3>
                {result.sections.length > 0 ? (
                  <div className="sections-list">
                    {result.sections.map((section, idx) => (
                      <div key={idx} className="section-item">
                        <div 
                          className="section-header"
                          onClick={() => setExpandedSection(expandedSection === idx ? null : idx)}
                        >
                          <span className="section-title">
                            {idx + 1}. {section.label}
                            <span className="section-type">{section.type}</span>
                          </span>
                          <span className="toggle-icon">
                            {expandedSection === idx ? '▼' : '▶'}
                          </span>
                        </div>
                        
                        {expandedSection === idx && (
                          <div className="section-content">
                            <JSONViewer data={section} />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No sections extracted</p>
                )}
              </div>

              {/* Metadata */}
              <div className="metadata-section">
                <h3>Page Metadata</h3>
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <strong>Title:</strong>
                    <p>{result.meta.title || '(empty)'}</p>
                  </div>
                  <div className="metadata-item">
                    <strong>Description:</strong>
                    <p>{result.meta.description || '(empty)'}</p>
                  </div>
                  <div className="metadata-item">
                    <strong>Language:</strong>
                    <p>{result.meta.language}</p>
                  </div>
                  <div className="metadata-item">
                    <strong>Canonical URL:</strong>
                    <p>{result.meta.canonical || '(none)'}</p>
                  </div>
                </div>
              </div>

              {/* Interactions */}
              <div className="interactions-section">
                <h3>Interaction Summary</h3>
                <div className="interactions-grid">
                  <div className="interaction-item">
                    <strong>Pages Visited:</strong>
                    <ul>
                      {result.interactions.pages.map((page, idx) => (
                        <li key={idx}>{page}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="interaction-item">
                    <strong>Clicks Performed:</strong>
                    {result.interactions.clicks.length > 0 ? (
                      <ul>
                        {result.interactions.clicks.map((click, idx) => (
                          <li key={idx}>{click}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>(none)</p>
                    )}
                  </div>
                  <div className="interaction-item">
                    <strong>Scroll Actions:</strong>
                    <p>{result.interactions.scrolls}</p>
                  </div>
                </div>
              </div>

              {/* Errors */}
              {result.errors.length > 0 && (
                <div className="errors-section">
                  <h3>⚠️ Errors Encountered</h3>
                  <div className="errors-list">
                    {result.errors.map((err, idx) => (
                      <div key={idx} className="error-item">
                        <strong>{err.phase}:</strong> {err.message}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>🔧 Lyftr AI Full-Stack Assignment v1.0.0</p>
      </footer>
    </div>
  )
}

export default App