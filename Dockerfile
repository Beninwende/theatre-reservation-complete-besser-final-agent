FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV THEATRE_PERSIST=1
ENV THEATRE_DB=/app/data/theatre.db
EXPOSE 8000 5000
