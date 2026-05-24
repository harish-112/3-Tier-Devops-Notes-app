import { useState, useEffect } from 'react'

const API = import.meta.env.VITE_API_URL || '/api'

export default function App() {
  const [notes, setNotes] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState(null)

  const fetchNotes = async () => {
    try {
      const res = await fetch(`${API}/notes/`)
      const data = await res.json()
      setNotes(data)
    } catch (e) {
      setError('Could not reach API')
    }
  }

  const addNote = async () => {
    if (!text.trim()) return
    await fetch(`${API}/notes/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text }),
    })
    setText('')
    fetchNotes()
  }

  useEffect(() => { fetchNotes() }, [])

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>📝 DevOps Notes</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <input
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addNote()}
          placeholder="Write a note…"
          style={{ flex: 1, padding: '8px 12px', fontSize: 16 }}
        />
        <button onClick={addNote} style={{ padding: '8px 20px', fontSize: 16 }}>
          Add
        </button>
      </div>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {notes.map(n => (
          <li key={n.id} style={{
            padding: '10px 14px', marginBottom: 8,
            background: '#f5f5f5', borderRadius: 8
          }}>
            {n.content}
          </li>
        ))}
      </ul>
    </div>
  )
}
