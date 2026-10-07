import { api } from './client'

export function getNotes() { return api('/notes') }
export function getNote(id) { return api(`/notes/${id}`) }
export function createNote(values) { return api('/notes', { method: 'POST', body: JSON.stringify(values) }) }
export function updateNote(id, values) { return api(`/notes/${id}`, { method: 'PUT', body: JSON.stringify(values) }) }
export function deleteNote(id) { return api(`/notes/${id}`, { method: 'DELETE' }) }
