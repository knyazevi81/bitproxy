import { api } from './client'

export interface StatsSummary {
  total_sessions: number
  active_sessions: number
  total_bytes_sent: number
  total_bytes_received: number
  uptime_hours: number
}

export interface DayHistory {
  date: string
  count: number
  bytes_sent: number
  bytes_received: number
}

export async function getStatsSummary(): Promise<StatsSummary> {
  const { data } = await api.get('/stats/summary')
  return data
}

export async function getSessionsHistory(): Promise<DayHistory[]> {
  const { data } = await api.get('/stats/sessions-history')
  return data
}
