import os

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)


def read_secret():
    secret_path = os.getenv(
        "DB_PASSWORD_FILE",
        "/run/secrets/db_password",
    )

    with open(secret_path, encoding="utf-8") as secret_file:
        return secret_file.read().strip()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=read_secret(),
    )


@app.get("/")
def index():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS counter (
                    id INTEGER PRIMARY KEY,
                    visits BIGINT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                INSERT INTO counter (id, visits)
                VALUES (1, 1)
                ON CONFLICT (id)
                DO UPDATE SET visits = counter.visits + 1
                RETURNING visits
                """
            )

            visits = cursor.fetchone()[0]

    return f"""
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="UTF-8">
        <title>Docker Final Project</title>
      </head>
      <body>
        <h1>Автоматический деплой работает!</h1>
        <p>Количество посещений: {visits}</p>
       <p>Release: rollback-test-v2</p>
      </body>
    </html>
    """


@app.get("/health")
def health():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return jsonify(status="healthy"), 200
    except Exception as error:
        return jsonify(status="unhealthy", error=str(error)), 503