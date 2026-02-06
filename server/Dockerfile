# ---------- builder ----------
    FROM python:3.11-slim AS builder

    WORKDIR /app
    
    # Install build deps only here
    RUN apt-get update && apt-get install -y build-essential
    
    COPY requirements.txt .
    RUN pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels
    
    # ---------- runtime ----------
    FROM python:3.11-slim
    
    WORKDIR /app
    
    # Install only runtime deps
    COPY --from=builder /wheels /wheels
    RUN pip install --no-cache /wheels/*
    
    RUN mkdir -p /app/data
    
    COPY . .
    
    EXPOSE 8000

    CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
    