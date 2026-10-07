import { api } from './client'

export function getEvents() { return api('/events') }
