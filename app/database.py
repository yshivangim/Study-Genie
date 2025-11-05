import reflex as rx
import datetime
import json
import logging
import os
from typing import TypedDict
import asyncio
from sqlalchemy import text


class GeneratedContentHistory(TypedDict):
    id: int
    topic: str
    mode: str
    content: str
    created_at: str


def _create_db_and_tables_sync():
    """Synchronous function to create database and tables."""
    engine = rx.Model.get_db_engine()
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
    with engine.connect() as conn:
        try:
            if not os.path.exists(schema_path):
                with open(schema_path, "w") as f:
                    f.write("""
                    CREATE TABLE IF NOT EXISTS generatedcontenthistory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        mode TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    """)
            with open(schema_path) as f:
                create_script = f.read()
            conn.exec_driver_sql(create_script)
            conn.commit()
        except Exception as e:
            logging.exception(f"Error creating database tables: {e}")


async def create_db_and_tables():
    await asyncio.to_thread(_create_db_and_tables_sync)


def _add_history_sync(
    topic: str, mode: str, content: str
) -> GeneratedContentHistory | None:
    """Synchronous function to add a history item."""
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            insert_stmt = text(
                "INSERT INTO generatedcontenthistory (topic, mode, content, created_at) VALUES (:topic, :mode, :content, :created_at)"
            )
            params = {
                "topic": topic,
                "mode": mode,
                "content": content,
                "created_at": datetime.datetime.now().isoformat(),
            }
            cursor = conn.execute(insert_stmt, params)
            conn.commit()
            new_id = cursor.lastrowid
            select_stmt = text("SELECT * FROM generatedcontenthistory WHERE id = :id")
            result = conn.execute(select_stmt, {"id": new_id})
            row = result.first()
            if row:
                return GeneratedContentHistory(
                    id=row[0],
                    topic=row[1],
                    mode=row[2],
                    content=row[3],
                    created_at=row[4],
                )
        except Exception as e:
            logging.exception(f"Error adding history: {e}")
    return None


async def add_history(
    topic: str, mode: str, content: str
) -> GeneratedContentHistory | None:
    return await asyncio.to_thread(_add_history_sync, topic, mode, content)


def _get_all_history_sync() -> list[GeneratedContentHistory]:
    """Synchronous function to get all history items."""
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            stmt = text(
                "SELECT id, topic, mode, content, created_at FROM generatedcontenthistory ORDER BY created_at DESC"
            )
            result = conn.execute(stmt)
            rows = result.fetchall()
            return [
                GeneratedContentHistory(
                    id=row[0],
                    topic=row[1],
                    mode=row[2],
                    content=row[3],
                    created_at=row[4],
                )
                for row in rows
            ]
        except Exception as e:
            logging.exception(f"Error fetching history: {e}")
            return []


async def get_all_history() -> list[GeneratedContentHistory]:
    return await asyncio.to_thread(_get_all_history_sync)