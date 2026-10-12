"use client";

import { useEffect, useState } from "react";
import { createNote, deleteNote, getMe, getNote, listNotes, login, logout, updateNote } from "../lib/api";

const blank = { title: "", body: "", status: "확인 전" };

export default function MemoDashboard() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [notes, setNotes] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(blank);
  const [editingId, setEditingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;
    async function restore() {
      try {
        const result = await getMe();
        const rows = await listNotes();
        if (active) { setUser(result.user); setNotes(rows); }
      } catch (failure) {
        if (active && failure.status !== 401) setError(failure.message);
      } finally { if (active) setChecking(false); }
    }
    restore();
    return () => { active = false; };
  }, []);

  function report(failure) {
    setMessage(""); setError(failure.message);
    if (failure.status === 401) { setUser(null); setNotes([]); setSelected(null); }
  }

  async function submitLogin(event) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const result = await login(credentials.username, credentials.password);
      const rows = await listNotes();
      setUser(result.user); setNotes(rows); setCredentials({ username: "", password: "" });
    } catch (failure) { report(failure); }
    finally { setBusy(false); }
  }

  async function refresh() {
    setError("");
    try {
      setNotes(await listNotes());
      if (selected) {
        try { setSelected(await getNote(selected.id)); }
        catch (failure) { if (failure.status === 404) setSelected(null); else throw failure; }
      }
    } catch (failure) { report(failure); }
  }

  async function selectNote(id) {
    setError(""); setMessage("");
    try { setSelected(await getNote(id)); }
    catch (failure) { report(failure); }
  }

  function resetForm() { setEditingId(null); setForm(blank); }

  function startEdit(note) {
    setEditingId(note.id); setForm({ title: note.title, body: note.body, status: note.status });
    setError(""); setMessage("");
  }

  async function submitNote(event) {
    event.preventDefault(); setError(""); setMessage("");
    const values = { title: form.title.trim(), body: form.body.trim(), status: form.status };
    if (!values.title || !values.body) { setError("제목과 내용을 모두 입력해 주세요."); return; }
    setBusy(true);
    try {
      const saved = editingId === null ? await createNote(values) : await updateNote(editingId, values);
      setNotes(await listNotes()); setSelected(saved); resetForm();
      setMessage(editingId === null ? "메모를 저장했습니다." : "메모를 수정했습니다.");
    } catch (failure) { report(failure); }
    finally { setBusy(false); }
  }

  async function confirmDelete() {
    const id = deletingId; setDeletingId(null); setBusy(true); setError(""); setMessage("");
    try {
      await deleteNote(id); setNotes(await listNotes());
      if (selected?.id === id) setSelected(null);
      if (editingId === id) resetForm();
      setMessage("메모를 삭제했습니다.");
    } catch (failure) { report(failure); }
    finally { setBusy(false); }
  }

  async function signOut() {
    setBusy(true);
    try { await logout(); setUser(null); setNotes([]); setSelected(null); resetForm(); setMessage(""); setError(""); }
    catch (failure) { report(failure); }
    finally { setBusy(false); }
  }

  return <main className="shell">
    <header className="topbar"><div><p className="eyebrow">MINI-WATCH / POSTGRESQL</p><h1>관찰 메모</h1><p className="sub">Flask API와 연결된 기록을 확인하고 관리합니다.</p></div>{user && <div className="user"><span>{user.name || user.username}</span><button className="ghost" onClick={signOut} disabled={busy}>로그아웃</button></div>}</header>
    {error && <p className="notice error" role="alert">{error}</p>}
    {message && <p className="notice success" role="status">{message}</p>}
    {checking ? <p className="panel">로그인 상태를 확인하고 있습니다.</p> : !user ? <section className="panel login"><h2>운영자 로그인</h2><p className="sub">기존 Flask 감시 서비스의 운영자 계정으로 로그인하세요.</p><form onSubmit={submitLogin}><label>아이디<input value={credentials.username} onChange={event => setCredentials({ ...credentials, username: event.target.value })} autoComplete="username" /></label><label>비밀번호<input type="password" value={credentials.password} onChange={event => setCredentials({ ...credentials, password: event.target.value })} autoComplete="current-password" /></label><button disabled={busy}>로그인</button></form></section> : <div className="grid">
      <section className="panel"><div className="section-head"><h2>메모 목록</h2><button className="ghost" onClick={refresh} disabled={busy}>새로고침</button></div><p className="sub">{notes.length}개의 저장된 메모</p>{notes.length ? <ul className="note-list">{notes.map(note => <li key={note.id}><button className="note-select" onClick={() => selectNote(note.id)}><span className="pill">{note.status}</span><strong>{note.title}</strong><small>#{note.id} · 상세 보기</small></button></li>)}</ul> : <p className="empty">저장된 메모가 없습니다. 오른쪽에서 첫 메모를 작성해 보세요.</p>}</section>
      <div className="stack"><section className="panel"><h2>{editingId === null ? "새 메모" : `메모 #${editingId} 수정`}</h2><form onSubmit={submitNote}><label>제목<input value={form.title} onChange={event => setForm({ ...form, title: event.target.value })} /></label><label>내용<textarea rows="5" value={form.body} onChange={event => setForm({ ...form, body: event.target.value })} /></label><label>처리 상태<select value={form.status} onChange={event => setForm({ ...form, status: event.target.value })}><option>확인 전</option><option>확인 중</option><option>완료</option></select></label><div className="actions"><button disabled={busy}>{editingId === null ? "등록" : "수정 저장"}</button>{editingId !== null && <button type="button" className="ghost" onClick={resetForm}>수정 취소</button>}</div></form></section>
      <section className="panel"><h2>메모 상세</h2>{selected ? <article><p className="sub">#{selected.id} · {selected.status}</p><h3>{selected.title}</h3><p className="body-text">{selected.body}</p><div className="actions"><button className="ghost" onClick={() => startEdit(selected)}>수정</button><button className="danger" onClick={() => setDeletingId(selected.id)} disabled={busy}>삭제</button></div></article> : <p className="empty">왼쪽 목록에서 메모를 선택하세요.</p>}</section></div>
    </div>}
    {deletingId !== null && <div className="backdrop"><div className="panel dialog" role="dialog" aria-modal="true" aria-labelledby="delete-title"><h2 id="delete-title">메모 삭제 확인</h2><p>이 메모를 삭제하시겠습니까?</p><div className="actions"><button className="danger" onClick={confirmDelete}>삭제 확인</button><button className="ghost" onClick={() => setDeletingId(null)}>취소</button></div></div></div>}
  </main>;
}
