import React from 'react'

function SectionViewer({ sections }) {
  return (
    <div className="section-viewer">
      {sections.map((section, idx) => (
        <div key={idx} className="section-card">
          <div className="section-card-header">
            <h3>{section.label}</h3>
            <span className="section-type-badge">{section.type}</span>
          </div>
          <div className="section-card-body">
            <p>{section.content.text.substring(0, 200)}...</p>
            <div className="section-stats">
              <span>🔗 {section.content.links.length} links</span>
              <span>🖼️ {section.content.images.length} images</span>
              <span>📝 {section.content.headings.length} headings</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default SectionViewer