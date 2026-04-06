import { api } from './client'

export interface User {
  id: string
  username: string
  is_admin: boolean
  is_active: boolean
  created_at: string
}

export async function register(username: string, password: string): Promise<string> {
  const { data } = await api.post('/auth/register', { username, password })
  return data.access_token
}

export async function login(username: string, password: string): Promise<string> {
  const { data } = await api.post('/auth/login', { username, password })
  return data.access_token
}

export async function refreshToken(refresh_token: string): Promise<string> {
  const { data } = await api.post('/auth/refresh', { refresh_token })
  return data.access_token
}

export async function logout(refresh_token: string): Promise<void> {
  await api.post('/auth/logout', { refresh_token })
}

export async function getMe(): Promise<User> {
  const { data } = await api.get('/auth/me')
  return data
}
