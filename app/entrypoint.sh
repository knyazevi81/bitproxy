#!/bin/bash

set -e

# echo "Прогоняются миграции..."
# alembic upgrade head

echo "Запускается приложение..."
# exec uvicorn app.presentation.fastapi.main:app --host 0.0.0.0 --port 8000
exec uvicorn presentation.main:app --host 0.0.0.0 --port 8000