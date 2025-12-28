import React from 'react'

function JSONViewer({ data, depth = 0 }) {
  const [expanded, setExpanded] = React.useState(depth < 2)

  if (data === null) return <span className="json-null">null</span>
  if (typeof data === 'boolean') return <span className="json-bool">{String(data)}</span>
  if (typeof data === 'number') return <span className="json-number">{data}</span>
  if (typeof data === 'string') return <span className="json-string">"{data}"</span>

  if (Array.isArray(data)) {
    if (data.length === 0) return <span className="json-bracket">[]</span>

    return (
      <div className="json-array">
        <span className="json-bracket">[</span>
        {expanded && (
          <div className="json-content">
            {data.map((item, idx) => (
              <div key={idx} className="json-item">
                <JSONViewer data={item} depth={depth + 1} />
                {idx < data.length - 1 && <span className="json-comma">,</span>}
              </div>
            ))}
          </div>
        )}
        <span className="json-bracket">]</span>
      </div>
    )
  }

  if (typeof data === 'object') {
    const keys = Object.keys(data)
    if (keys.length === 0) return <span className="json-bracket">{}</span>

    return (
      <div className="json-object">
        <span 
          className="json-toggle"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '▼' : '▶'} {keys.length} properties
        </span>

        {expanded && (
          <div className="json-content">
            {keys.map((key, idx) => (
              <div key={idx} className="json-property">
                <span className="json-key">"{key}"</span>
                <span className="json-colon">:</span>
                <JSONViewer data={data[key]} depth={depth + 1} />
                {idx < keys.length - 1 && <span className="json-comma">,</span>}
              </div>
            ))}
          </div>
        )}
        <span className="json-bracket">{'}'}</span>
      </div>
    )
  }

  return <span className="json-unknown">{String(data)}</span>
}

export default JSONViewer