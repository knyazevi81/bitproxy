import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCallLinks, addCallLink, deleteCallLink, testCallLink } from '../api/callLinks'
import Modal from '../components/Modal'
import Layout from '../components/Layout'

export default function CallLinksPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ raw_link: '', label: '' })
  const [formError, setFormError] = useState('')
  const [testResults, setTestResults] = useState<Record<string, string>>({})

  const { data: links = [], isLoading } = useQuery({ queryKey: ['call-links'], queryFn: getCallLinks })

  const addMutation = useMutation({
    mutationFn: () => addCallLink(form.raw_link, form.label),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['call-links'] })
      setShowModal(false)
      setForm({ raw_link: '', label: '' })
    },
    onError: (err: any) => setFormError(err.response?.data?.detail || 'Failed to add link'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCallLink,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['call-links'] }),
  })

  const testMutation = useMutation({
    mutationFn: testCallLink,
    onSuccess: (result, id) => {
      setTestResults((prev) => ({ ...prev, [id]: result.message }))
    },
  })

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Call Links</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded font-medium text-sm"
        >
          + Add Link
        </button>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        {isLoading ? (
          <p className="text-center text-gray-500 py-8">Loading…</p>
        ) : links.length === 0 ? (
          <p className="text-center text-gray-600 py-8">No call links yet. Add one to start.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs uppercase border-b border-gray-800">
                <th className="px-4 py-2 text-left">Label</th>
                <th className="px-4 py-2 text-left">Link</th>
                <th className="px-4 py-2 text-left">Added</th>
                <th className="px-4 py-2 text-left">Last Used</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {links.map((l) => (
                <tr key={l.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="px-4 py-2 font-medium">{l.label}</td>
                  <td className="px-4 py-2 text-gray-400 text-xs font-mono max-w-xs truncate">
                    {l.raw_link.length > 40 ? l.raw_link.slice(0, 40) + '…' : l.raw_link}
                  </td>
                  <td className="px-4 py-2 text-gray-500 text-xs">
                    {new Date(l.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2 text-gray-500 text-xs">
                    {l.last_used_at ? new Date(l.last_used_at).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-2 space-x-2">
                    <button
                      onClick={() => testMutation.mutate(l.id)}
                      disabled={testMutation.isPending}
                      className="text-indigo-400 hover:text-indigo-300 text-xs"
                    >
                      Test
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(l.id)}
                      className="text-red-400 hover:text-red-300 text-xs"
                    >
                      Delete
                    </button>
                    {testResults[l.id] && (
                      <span className="text-gray-500 text-xs">{testResults[l.id]}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <Modal title="Add Call Link" onClose={() => setShowModal(false)}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Label</label>
              <input
                type="text"
                value={form.label}
                onChange={(e) => setForm({ ...form, label: e.target.value })}
                placeholder="My VK Call"
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">VK Call Link</label>
              <input
                type="url"
                value={form.raw_link}
                onChange={(e) => setForm({ ...form, raw_link: e.target.value })}
                placeholder="https://vk.com/call/join/..."
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            {formError && <p className="text-red-400 text-sm">{formError}</p>}
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-400 hover:text-white text-sm">
                Cancel
              </button>
              <button
                onClick={() => { setFormError(''); addMutation.mutate() }}
                disabled={addMutation.isPending || !form.raw_link || !form.label}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2 rounded text-sm"
              >
                {addMutation.isPending ? 'Adding…' : 'Add Link'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </Layout>
  )
}
