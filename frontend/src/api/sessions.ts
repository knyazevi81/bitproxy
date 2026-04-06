import { api } from './client'

export type SessionStatus = 'pending' | 'active' | 'terminated' | 'failed'

export interface Session {
  id: string
  user_id: string
  call_link_id: string
  status: SessionStatus
  listen_port: number
  peer_addr: string
  pid: number | null
  started_at: string | null
  terminated_at: string | null
  bytes_sent: number
  bytes_received: number
  last_seen_at: string | null
}

export interface CreateSessionPayload {
  call_link_id: string
  listen_port?: number
  peer_addr?: string
  streams_count?: number
  use_udp?: boolean
}

export async function getSessions(): Promise<Session[]> {
  const { data } = await api.get('/sessions/')
  return data
}

export async function getActiveSessions(): Promise<Session[]> {
  const { data } = await api.get('/sessions/active')
  return data
}

export async function getSession(id: string): Promise<Session> {
  const { data } = await api.get(`/sessions/${id}`)
  return data
}

export async function createSession(payload: CreateSessionPayload): Promise<Session> {
  const { data } = await api.post('/sessions/', {
    listen_port: 0,
    peer_addr: '127.0.0.1:51820',
    streams_count: 8,
    use_udp: false,
    ...payload,
  })
  return data
}

export async function deleteSession(id: string): Promise<void> {
  await api.delete(`/sessions/${id}`)
}

export async function getSessionLogs(id: string, lines = 50): Promise<string[]> {
  const { data } = await api.get(`/sessions/${id}/logs`, { params: { lines } })
  return data.lines
}
