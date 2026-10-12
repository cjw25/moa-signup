"use client";

import { useState } from "react";

const INITIAL_NOTES = [{ id: "initial-1", text: "첫 메모를 수정하거나 새 메모를 추가해 보세요." }];

export default function Notes() {
  const [notes, setNotes] = useState(INITIAL_NOTES);
  const [draft, setDraft] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");

  function resetForm() {
    setDraft("");
    setEditingId(null);
    setError("");
  }

  function submit(event) {
    event.preventDefault();
    const text = draft.trim();
    if (!text) {
      setError("공백이 아닌 메모 내용을 입력해 주세요.");
      return;
    }
    if (editingId === null) {
      setNotes(current => [...current, { id: crypto.randomUUID(), text }]);
    } else {
      setNotes(current => current.map(note => note.id === editingId ? { ...note, text } : note));
    }
    resetForm();
  }

  function edit(note) {
    setEditingId(note.id);
    setDraft(note.text);
    setError("");
  }

  function confirmDelete() {
    setNotes(current => current.filter(note => note.id !== deletingId));
    if (editingId === deletingId) resetForm();
    setDeletingId(null);
  }

  return (
    <div className="notes-layout">
      <section className="panel">
        <p className="eyebrow">NOTES</p><h1>내 메모</h1><p className="muted">같은 내용도 각각의 ID로 구분됩니다.</p>
        <form onSubmit={submit}>
          <label htmlFor="note-input">{editingId === null ? "새 메모" : "메모 수정"}</label>
          <textarea id="note-input" value={draft} onChange={event => { setDraft(event.target.value); setError(""); }} rows="5" placeholder="오늘 기억할 내용을 적어 보세요" />
          {error && <p className="error" role="alert">{error}</p>}
          <div className="actions"><button type="submit">{editingId === null ? "등록" : "수정 저장"}</button>{editingId !== null && <button type="button" className="secondary" onClick={resetForm}>수정 취소</button>}</div>
        </form>
      </section>
      <section className="panel"><div className="section-heading"><h2>메모 목록</h2><span>{notes.length}개</span></div>
        {notes.length === 0 ? <p className="empty">등록된 메모가 없습니다.</p> : <ul className="note-list">{notes.map(note => <li key={note.id}><p>{note.text}</p><div className="actions"><button className="secondary" onClick={() => edit(note)}>수정</button><button className="danger" onClick={() => setDeletingId(note.id)}>삭제</button></div></li>)}</ul>}
      </section>
      {deletingId !== null && <div className="dialog-backdrop"><div className="dialog panel" role="dialog" aria-modal="true" aria-labelledby="delete-title"><h2 id="delete-title">메모 삭제 확인</h2><p>선택한 메모만 삭제합니다. 계속하시겠습니까?</p><div className="actions"><button className="danger" onClick={confirmDelete}>삭제 확인</button><button className="secondary" onClick={() => setDeletingId(null)}>취소</button></div></div></div>}
    </div>
  );
}
