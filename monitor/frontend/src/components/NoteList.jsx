export default function NoteList({ notes, selectedId, onSelect, onNew, loading, error }) {
  return <section className="card"><div className="section-head"><h2>관찰 메모</h2><button onClick={onNew}>새 메모</button></div>
    {loading ? <p>불러오는 중...</p> : error ? <p className="error" role="alert">{error}</p> : notes.length === 0 ? <p>작성된 메모가 없습니다.</p> :
      <ul className="notes">{notes.map(note => <li key={note.id}><button className={selectedId === note.id ? 'selected link-button' : 'link-button'} onClick={() => onSelect(note.id)}>#{note.id} {note.title} <small>· {note.status}</small></button></li>)}</ul>}
  </section>
}
