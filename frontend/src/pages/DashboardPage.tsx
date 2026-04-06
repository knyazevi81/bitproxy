import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getActiveSessions, createSession, deleteSession } from '../api/sessions'
import { getStatsSummary } from '../api/stats'
import { getCallLinks } from '../api/callLinks'
import StatusBadge from '../components/StatusBadge'
import Modal from '../components/Modal'
import Layout from '../components/Layout'

function formatBytes(b: number) {
  if (b < 1024) return `${b} B`
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`
  return `${(b / 1024 / 1024).toFixed(1)} MB`
}

function formatUptime(startedAt: string | null) {
  if (!startedAt) return '—'
  const diff = Date.now() - new Date(startedAt).getTime()
  const s = Math.floor(diff / 1000)
  const m = Math.floor(s / 60)
  const h = Math.floor(m / 60)
  if (h > 0) return `${h}h ${m % 60}m`
  if (m > 0) return `${m}m ${s % 60}s`
  return `${s}s`
}

export default function DashboardPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ call_link_id: '', listen_port: '0', peer_addr: '127.0.0.1:51820' })
  const [formError, setFormError] = useState('')

  const { data: summary } = useQuery({ queryKey: ['stats-summary'], queryFn: getStatsSummary, refetchInterval: 10_000 })
  const { data: active = [] } = useQuery({ queryKey: ['active-sessions'], queryFn: getActiveSessions, refetchInterval: 5_000 })
  const { data: callLinks = [] } = useQuery({ queryKey: ['call-links'], queryFn: getCallLinks })

  const createMutation = useMutation({
    mutationFn: createSession,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['active-sessions'] })
      qc.invalidateQueries({ queryKey: ['stats-summary'] })
      setShowModal(false)
      setForm({ call_link_id: '', listen_port: '0', peer_addr: '127.0.0.1:51820' })
    },
    onError: (err: any) => setFormError(err.response?.data?.detail || 'Failed to create session'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteSession,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['active-sessions'] })
      qc.invalidateQueries({ queryKey: ['stats-summary'] })
    },
  })

  const handleCreate = () => {
    setFormError('')
    if (!form.call_link_id) { setFormError('Select a call link'); return }
    createMutation.mutate({
      call_link_id: form.call_link_id,
      listen_port: parseInt(form.listen_port),
      peer_addr: form.peer_addr,
    })
  }

  const stats = [
    { label: 'Active Sessions', value: summary?.active_sessions ?? '—' },
    { label: 'Total Sessions', value: summary?.total_sessions ?? '—' },
    { label: 'Total Uptime', value: summary ? `${summary.uptime_hours}h` : '—' },
    { label: 'Traffic Out', value: summary ? formatBytes(summary.total_bytes_sent) : '—' },
  ]

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded font-medium text-sm transition-colors"
        >
          + New Session
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((s) => (
          <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{s.label}</p>
            <p className="text-2xl font-bold mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Active sessions table */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-800 text-sm font-medium text-gray-400">
          Active Sessions
        </div>
        {active.length === 0 ? (
          <p className="text-center text-gray-600 py-8">No active sessions</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs uppercase border-b border-gray-800">
                <th className="px-4 py-2 text-left">ID</th>
                <th className="px-4 py-2 text-left">Port</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Uptime</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {active.map((s) => (
                <tr key={s.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="px-4 py-2">
                    <Link to={`/sessions/${s.id}`} className="text-indigo-400 hover:underline font-mono text-xs">
                      {s.id.slice(0, 8)}…
                    </Link>
                  </td>
                  <td className="px-4 py-2 font-mono">{s.listen_port}</td>
                  <td className="px-4 py-2"><StatusBadge status={s.status} /></td>
                  <td className="px-4 py-2 text-gray-400">{formatUptime(s.started_at)}</td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => deleteMutation.mutate(s.id)}
                      className="text-red-400 hover:text-red-300 text-xs"
                    >
                      Stop
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <Modal title="New Session" onClose={() => setShowModal(false)}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Call Link</label>
              <select
                value={form.call_link_id}
                onChange={(e) => setForm({ ...form, call_link_id: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="">Select…</option>
                {callLinks.map((l) => (
                  <option key={l.id} value={l.id}>{l.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Listen Port (0 = auto)</label>
              <input
                type="number"
                value={form.listen_port}
                onChange={(e) => setForm({ ...form, listen_port: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Peer Address</label>
              <input
                type="text"
                value={form.peer_addr}
                onChange={(e) => setForm({ ...form, peer_addr: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            {formError && <p className="text-red-400 text-sm">{formError}</p>}
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-400 hover:text-white text-sm">
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={createMutation.isPending}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2 rounded text-sm"
              >
                {createMutation.isPending ? 'Starting…' : 'Start Session'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </Layout>
  )
}
