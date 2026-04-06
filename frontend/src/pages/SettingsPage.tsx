import { useAuthStore } from '../store/authStore'
import Layout from '../components/Layout'

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user)

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 max-w-md">
        <h2 className="text-sm font-medium text-gray-400 mb-4">Profile</h2>
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500">Username</dt>
            <dd className="font-medium">{user?.username}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">Role</dt>
            <dd>{user?.is_admin ? 'Admin' : 'User'}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">Joined</dt>
            <dd className="text-gray-400">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
            </dd>
          </div>
        </dl>
      </div>
    </Layout>
  )
}
