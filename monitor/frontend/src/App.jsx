import { useEffect, useState } from 'react'
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
  const [events, setEvents] = useState([])
  const [notes, setNotes] = useState([])
  const [selected, setSelected] = useState(null)
  const [mode, setMode] = useState('detail')
  const [eventsError, setEventsError] = useState('')
  const [notesError, setNotesError] = useState('')
  const [actionError, setActionError] = useState('')
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)

  async function refresh() {
    setLoading(true)
    setEventsError('')
    setNotesError('')
    const [eventResult, noteResult] = await Promise.allSettled([getEvents(), getNotes()])
    if (eventResult.status === 'fulfilled') setEvents(eventResult.value)
    else setEventsError(eventResult.reason.message)
    if (noteResult.status === 'fulfilled') setNotes(noteResult.value)
    else setNotesError(noteResult.reason.message)
    setLoading(false)
  }

  useEffect(() => { if (user) refresh() }, [user])

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

  if (!user) return <LoginForm onLogin={setUser} />

  return <main className="dashboard"><header className="topbar"><div><p className="eyebrow">MINI WATCH</p><h1>감시 대시보드</h1><p>{user.name}님, 안녕하세요.</p></div><div className="actions"><button onClick={refresh} disabled={loading}>목록 새로고침</button><button className="secondary" onClick={() => { setUser(null); setSelected(null); setEvents([]); setNotes([]); setMode('detail') }}>로그아웃</button></div></header>
    <EventList events={events} loading={loading} error={eventsError} />
    <div className="note-grid"><NoteList notes={notes} selectedId={selected?.id} loading={loading} error={notesError} onSelect={selectNote} onNew={() => { setSelected(null); setMode('new'); setActionError('') }} />
      <div>{mode === 'new' ? <NoteForm key="new" onSave={saveNote} onCancel={() => { setMode('detail'); setActionError('') }} busy={busy} error={actionError} /> : mode === 'edit' && selected ? <NoteForm key={selected.id} initial={selected} onSave={saveNote} onCancel={() => { setMode('detail'); setActionError('') }} busy={busy} error={actionError} /> : mode === 'delete' && selected ? <DeleteConfirm note={selected} onConfirm={removeNote} onCancel={() => { setMode('detail'); setActionError('') }} busy={busy} error={actionError} /> : selected ? <NoteDetail note={selected} onEdit={() => { setMode('edit'); setActionError('') }} onDelete={() => { setMode('delete'); setActionError('') }} /> : <section className="card"><p>메모를 선택하거나 새로 작성해 주세요.</p></section>}
        {mode === 'detail' && actionError && <p className="error" role="alert">{actionError}</p>}
      </div>
    </div>
  </main>
}
