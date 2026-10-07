import { useState } from 'react'

export default function NoteForm({ initial, onSave, onCancel, busy, error }) {
  const [title, setTitle] = useState(initial?.title || '')
  const [body, setBody] = useState(initial?.body || '')
  return <section className="card"><h2>{initial ? '메모 수정' : '새 메모'}</h2><form onSubmit={event => { event.preventDefault(); onSave({ title, body }) }}>
    <label>제목<input value={title} onChange={event => setTitle(event.target.value)} /></label>
    <label>내용<textarea rows="8" value={body} onChange={event => setBody(event.target.value)} /></label>
    {error && <p className="error" role="alert">{error}</p>}
    <div className="actions"><button disabled={busy}>저장</button><button type="button" className="secondary" onClick={onCancel}>취소</button></div>
  </form></section>
}
