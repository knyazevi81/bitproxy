import { SessionStatus } from '../api/sessions'

const colorMap: Record<SessionStatus, string> = {
  pending: 'bg-yellow-500 text-yellow-950',
  active: 'bg-green-500 text-green-950',
  terminated: 'bg-gray-500 text-gray-950',
  failed: 'bg-red-500 text-red-950',
}

export default function StatusBadge({ status }: { status: SessionStatus }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold uppercase ${colorMap[status]}`}>
      {status}
    </span>
  )
}
