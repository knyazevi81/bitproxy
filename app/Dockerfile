FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD requirements.txt /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN apt install ping curl

# исправить перенос всего репозитория
COPY . /app 

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]