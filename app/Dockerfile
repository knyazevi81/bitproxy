FROM python:3.12-slim

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Run migrations then start uvicorn
CMD ["sh", "-c", "uvicorn presentation.main:app --host 0.0.0.0 --port 8000"]
