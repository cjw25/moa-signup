import { useEffect, useState } from 'react'
import { getMe, logout } from './api/auth'
import { getEvents } from './api/events'
import { createNote, deleteNote, getNote, getNotes, updateNote } from './api/notes'
import LoginForm from './components/LoginForm'
import EventList from './components/EventList'
import NoteList from './components/NoteList'
import NoteDetail from './components/NoteDetail'
import NoteForm from './components/NoteForm'
import DeleteConfirm from './components/DeleteConfirm'

export default function App() {
  const [user, setUser] = useState(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [authError, setAuthError] = useState('')
  const [events, setEvents] = useState([])
  const [notes, setNotes] = useState([])
  const [selected, setSelected] = useState(null)
  const [mode, setMode] = useState('detail')
  const [eventsError, setEventsError] = useState('')
  const [notesError, setNotesError] = useState('')
  const [actionError, setActionError] = useState('')
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [filters, setFilters] = useState({ path: '', status: '' })

  async function refresh(nextFilters = filters) {
    setLoading(true)
    setEventsError('')
    setNotesError('')
    const [eventResult, noteResult] = await Promise.allSettled([getEvents(nextFilters), getNotes()])
    if (eventResult.status === 'fulfilled') setEvents(eventResult.value)
    else setEventsError(eventResult.reason.message)
    if (noteResult.status === 'fulfilled') setNotes(noteResult.value)
    else setNotesError(noteResult.reason.message)
    setLoading(false)
  }

  useEffect(() => {
    getMe().then(result => setUser(result.user)).catch(cause => {
      if (cause.status !== 401) setAuthError(cause.message)
    }).finally(() => setCheckingSession(false))
  }, [])

  useEffect(() => { if (user) refresh() }, [user])

  function applyFilters(nextFilters) {
    setFilters(nextFilters)
    refresh(nextFilters)
  }

  async function signOut() {
    try {
      await logout()
      setUser(null)
      setSelected(null)
      setEvents([])
      setNotes([])
      setMode('detail')
      setAuthError('')
    } catch (cause) {
      setActionError(cause.message)
    }
  }

  async function selectNote(id) {
    setActionError('')
    try {
      setSelected(await getNote(id))
      setMode('detail')
    } catch (cause) {
      setActionError(cause.message)
    }
  }

  async function saveNote(values) {
    setActionError('')
    setBusy(true)
    try {
      const saved = mode === 'edit' ? await updateNote(selected.id, values) : await createNote(values)
      setSelected(saved)
      setMode('detail')
      await refresh()
    } catch (cause) {
      setActionError(cause.message)
    } finally {
      setBusy(false)
    }
  }

  async function removeNote() {
    setActionError('')
    setBusy(true)
    try {
      await deleteNote(selected.id)
      setSelected(null)
      setMode('detail')
      await refresh()
    } catch (cause) {
      setActionError(cause.message)
    } finally {
      setBusy(false)
    }
  }

  if (checkingSession) return <main className="login card"><p>로그인 상태를 확인하는 중...</p></main>
  if (!user) return <LoginForm onLogin={nextUser => { setAuthError(''); setUser(nextUser) }} initialError={authError} />

  return <main className="dashboard"><header className="topbar"><div><p className="eyebrow">MINI WATCH</p><h1>감시 대시보드</h1><p>{user.name}님, 안녕하세요.</p></div><div className="actions"><button onClick={() => refresh()} disabled={loading}>목록 새로고침</button><button className="secondary" onClick={signOut}>로그아웃</button></div></header>
    <EventList events={events} loading={loading} error={eventsError} filters={filters} onApply={applyFilters} onClear={() => applyFilters({ path: '', status: '' })} />
    <div className="note-grid"><NoteList notes={notes} selectedId={selected?.id} loading={loading} error={notesError} onSelect={selectNote} onNew={() => { setSelected(null); setMode('new'); setActionError('') }} />
      <div>{mode === 'new' ? <NoteForm key="new" onSave={saveNote} onCancel={() => { setMode('detail'); setActionError('') }} busy={busy} error={actionError} /> : mode === 'edit' && selected ? <NoteForm key={selected.id} initial={selected} onSave={saveNote} onCancel={() => { setMode('detail'); setActionError('') }} busy={busy} error={actionError} /> : mode === 'delete' && selected ? <DeleteConfirm note={selected} onConfirm={removeNote} onCancel={() => { setMode('detail'); setActionError('') }} busy={busy} error={actionError} /> : selected ? <NoteDetail note={selected} onEdit={() => { setMode('edit'); setActionError('') }} onDelete={() => { setMode('delete'); setActionError('') }} /> : <section className="card"><p>메모를 선택하거나 새로 작성해 주세요.</p></section>}
        {mode === 'detail' && actionError && <p className="error" role="alert">{actionError}</p>}
      </div>
    </div>
  </main>
}
