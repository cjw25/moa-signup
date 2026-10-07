export default function NoteDetail({ note, onEdit, onDelete }) {
  return <article className="card"><p className="muted">메모 #{note.id} · {note.status}</p><h2>{note.title}</h2><p className="note-body">{note.body}</p>
    <div className="actions"><button onClick={onEdit}>수정</button><button className="danger" onClick={onDelete}>삭제</button></div>
  </article>
}
