FROM python:3.13-alpine AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


FROM python:3.13-alpine

RUN addgroup -S appgroup \
    && adduser -S -G appgroup -u 10001 appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup app.py .

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]