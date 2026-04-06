import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getSession, getSessionLogs, deleteSession } from '../api/sessions'
import StatusBadge from '../components/StatusBadge'
import Layout from '../components/Layout'

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: session, isLoading } = useQuery({
    queryKey: ['session', id],
    queryFn: () => getSession(id!),
    refetchInterval: 5_000,
  })

  const { data: logs = [] } = useQuery({
    queryKey: ['session-logs', id],
    queryFn: () => getSessionLogs(id!),
    refetchInterval: 3_000,
    enabled: !!session,
  })

  const stopMutation = useMutation({
    mutationFn: () => deleteSession(id!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['session', id] })
      qc.invalidateQueries({ queryKey: ['sessions'] })
    },
  })

  if (isLoading) {
    return (
      <Layout>
        <p className="text-gray-500">Loading…</p>
      </Layout>
    )
  }

  if (!session) {
    return (
      <Layout>
        <p className="text-red-400">Session not found</p>
      </Layout>
    )
  }

  const rows = [
    ['ID', <span className="font-mono text-xs">{session.id}</span>],
    ['Status', <StatusBadge status={session.status} />],
    ['Port', session.listen_port],
    ['Peer', <span className="font-mono text-xs">{session.peer_addr}</span>],
    ['PID', session.pid ?? '—'],
    ['Started', session.started_at ? new Date(session.started_at).toLocaleString() : '—'],
    ['Terminated', session.terminated_at ? new Date(session.terminated_at).toLocaleString() : '—'],
    ['Bytes Sent', session.bytes_sent],
    ['Bytes Received', session.bytes_received],
    ['Last Seen', session.last_seen_at ? new Date(session.last_seen_at).toLocaleString() : '—'],
  ]

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate(-1)} className="text-gray-500 hover:text-white text-sm mr-4">← Back</button>
          <span className="text-xl font-bold">Session Detail</span>
        </div>
        {(session.status === 'active' || session.status === 'pending') && (
          <button
            onClick={() => stopMutation.mutate()}
            disabled={stopMutation.isPending}
            className="bg-red-700 hover:bg-red-600 disabled:opacity-50 text-white px-4 py-2 rounded text-sm"
          >
            {stopMutation.isPending ? 'Stopping…' : 'Stop Session'}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-3">Metadata</h2>
          <dl className="space-y-2">
            {rows.map(([label, value]) => (
              <div key={String(label)} className="flex justify-between text-sm">
                <dt className="text-gray-500">{label}</dt>
                <dd className="text-white">{value as any}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      {/* Logs */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-800 text-sm font-medium text-gray-400 flex justify-between">
          <span>Process Logs</span>
          <span className="text-xs text-gray-600">auto-refreshes every 3s</span>
        </div>
        <div className="p-4 font-mono text-xs text-green-400 bg-gray-950 max-h-96 overflow-y-auto space-y-0.5">
          {logs.length === 0 ? (
            <p className="text-gray-600">No logs yet…</p>
          ) : (
            logs.map((line, i) => <div key={i}>{line}</div>)
          )}
        </div>
      </div>
    </Layout>
  )
}
