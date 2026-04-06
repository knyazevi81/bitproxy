import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getSessions, deleteSession } from '../api/sessions'
import StatusBadge from '../components/StatusBadge'
import Layout from '../components/Layout'

export default function SessionsPage() {
  const qc = useQueryClient()
  const { data: sessions = [], isLoading } = useQuery({ queryKey: ['sessions'], queryFn: getSessions })

  const deleteMutation = useMutation({
    mutationFn: deleteSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  })

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Sessions</h1>
      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        {isLoading ? (
          <p className="text-center text-gray-500 py-8">Loading…</p>
        ) : sessions.length === 0 ? (
          <p className="text-center text-gray-600 py-8">No sessions yet</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs uppercase border-b border-gray-800">
                <th className="px-4 py-2 text-left">ID</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Port</th>
                <th className="px-4 py-2 text-left">Peer</th>
                <th className="px-4 py-2 text-left">Started</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="px-4 py-2">
                    <Link to={`/sessions/${s.id}`} className="text-indigo-400 hover:underline font-mono text-xs">
                      {s.id.slice(0, 8)}…
                    </Link>
                  </td>
                  <td className="px-4 py-2"><StatusBadge status={s.status} /></td>
                  <td className="px-4 py-2 font-mono">{s.listen_port}</td>
                  <td className="px-4 py-2 text-gray-400 font-mono text-xs">{s.peer_addr}</td>
                  <td className="px-4 py-2 text-gray-500 text-xs">
                    {s.started_at ? new Date(s.started_at).toLocaleString() : '—'}
                  </td>
                  <td className="px-4 py-2">
                    {(s.status === 'active' || s.status === 'pending') && (
                      <button
                        onClick={() => deleteMutation.mutate(s.id)}
                        className="text-red-400 hover:text-red-300 text-xs mr-2"
                      >
                        Stop
                      </button>
                    )}
                    <Link to={`/sessions/${s.id}`} className="text-gray-400 hover:text-white text-xs">
                      Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Layout>
  )
}
