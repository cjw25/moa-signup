import { api } from './client'

export function login(username, password) {
  return api('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
}

export function getMe() { return api('/auth/me') }
export function logout() { return api('/auth/logout', { method: 'POST' }) }
