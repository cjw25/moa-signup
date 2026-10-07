export default function DeleteConfirm({ note, onConfirm, onCancel, busy, error }) {
  return <section className="card"><h2>삭제 확인</h2><p>“{note.title}” 메모를 삭제하시겠습니까?</p>
    {error && <p className="error" role="alert">{error}</p>}
    <div className="actions"><button className="danger" disabled={busy} onClick={onConfirm}>삭제 확정</button><button className="secondary" onClick={onCancel}>취소</button></div>
  </section>
}
