import { api } from './client'

export interface CallLink {
  id: string
  user_id: string
  raw_link: string
  label: string
  is_active: boolean
  last_used_at: string | null
  created_at: string
}

export async function getCallLinks(): Promise<CallLink[]> {
  const { data } = await api.get('/call-links/')
  return data
}

export async function addCallLink(raw_link: string, label: string): Promise<CallLink> {
  const { data } = await api.post('/call-links/', { raw_link, label })
  return data
}

export async function deleteCallLink(id: string): Promise<void> {
  await api.delete(`/call-links/${id}`)
}

export async function testCallLink(id: string): Promise<{ valid: boolean; message: string }> {
  const { data } = await api.post(`/call-links/${id}/test`)
  return data
}
