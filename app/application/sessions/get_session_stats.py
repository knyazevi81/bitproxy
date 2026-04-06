from datetime import datetime, timedelta
from uuid import UUID

from domain.repositories import SessionRepository
from domain.session import SessionStatus


async def get_stats_summary(user_id: UUID, session_repo: SessionRepository) -> dict:
    all_sessions = await session_repo.list_by_user(user_id)
    active = [s for s in all_sessions if s.status in (SessionStatus.ACTIVE, SessionStatus.PENDING)]

    total_bytes_sent = sum(s.bytes_sent for s in all_sessions)
    total_bytes_recv = sum(s.bytes_received for s in all_sessions)

    total_uptime_seconds = 0
    for s in all_sessions:
        if s.started_at:
            end = s.terminated_at or datetime.utcnow()
            total_uptime_seconds += (end - s.started_at).total_seconds()

    return {
        "total_sessions": len(all_sessions),
        "active_sessions": len(active),
        "total_bytes_sent": total_bytes_sent,
        "total_bytes_received": total_bytes_recv,
        "uptime_hours": round(total_uptime_seconds / 3600, 2),
    }


async def get_sessions_history(user_id: UUID, session_repo: SessionRepository) -> list[dict]:
    all_sessions = await session_repo.list_by_user(user_id)
    by_day: dict[str, dict] = {}
    for s in all_sessions:
        if s.started_at:
            day = s.started_at.date().isoformat()
            if day not in by_day:
                by_day[day] = {"date": day, "count": 0, "bytes_sent": 0, "bytes_received": 0}
            by_day[day]["count"] += 1
            by_day[day]["bytes_sent"] += s.bytes_sent
            by_day[day]["bytes_received"] += s.bytes_received
    return sorted(by_day.values(), key=lambda x: x["date"])
