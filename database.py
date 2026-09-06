import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Crear tabla si no existe
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN DEFAULT FALSE
                );
            """
            )

            # 2. Revisar si la tabla esta vacia
            cur.execute("SELECT COUNT(*) FROM tasks;")
            count = cur.fetchone()["count"]

            # 3. Sembrar datos iniciales si no hay tareas
            if count == 0:
                cur.execute(
                    """
                    INSERT INTO tasks (title, done) VALUES
                    ('Comprar leche', false),
                    ('Estudiar Docker', true),
                    ('Completar A3', false);
                """
                )
            conn.commit()