import { api } from './client'

export function getEvents(filters = {}) {
  const params = new URLSearchParams()
  if (filters.path) params.set('path', filters.path)
  if (filters.status) params.set('status', filters.status)
  const query = params.toString()
  return api(`/events${query ? `?${query}` : ''}`)
}
