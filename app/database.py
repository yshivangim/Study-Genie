import reflex as rx
import datetime
import json
import logging
import os
from typing import TypedDict
import asyncio
from sqlalchemy import text


class User(TypedDict):
    id: int
    username: str
    email: str
    password_hash: str
    created_at: str


class GeneratedContentHistory(TypedDict):
    id: int
    topic: str
    mode: str
    content: str
    created_at: str
    user_id: int


def _create_db_and_tables_sync():
    """Synchronous function to create database and tables."""
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            conn.exec_driver_sql("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """)
            conn.exec_driver_sql("""
                CREATE TABLE IF NOT EXISTS generatedcontenthistory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """)
            conn.commit()
        except Exception as e:
            logging.exception(f"Error creating database tables: {e}")


async def create_db_and_tables():
    await asyncio.to_thread(_create_db_and_tables_sync)


def _add_history_sync(
    topic: str, mode: str, content: str, user_id: int
) -> GeneratedContentHistory | None:
    """Synchronous function to add a history item."""
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            insert_stmt = text(
                "INSERT INTO generatedcontenthistory (topic, mode, content, created_at, user_id) VALUES (:topic, :mode, :content, :created_at, :user_id)"
            )
            params = {
                "topic": topic,
                "mode": mode,
                "content": content,
                "created_at": datetime.datetime.now().isoformat(),
                "user_id": user_id,
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
                    user_id=row[5],
                )
        except Exception as e:
            logging.exception(f"Error adding history: {e}")
    return None


async def add_history(
    topic: str, mode: str, content: str, user_id: int
) -> GeneratedContentHistory | None:
    return await asyncio.to_thread(_add_history_sync, topic, mode, content, user_id)


def _get_all_history_sync(user_id: int) -> list[GeneratedContentHistory]:
    """Synchronous function to get all history items for a user."""
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            stmt = text(
                "SELECT id, topic, mode, content, created_at, user_id FROM generatedcontenthistory WHERE user_id = :user_id ORDER BY created_at DESC"
            )
            result = conn.execute(stmt, {"user_id": user_id})
            rows = result.fetchall()
            return [
                GeneratedContentHistory(
                    id=row[0],
                    topic=row[1],
                    mode=row[2],
                    content=row[3],
                    created_at=row[4],
                    user_id=row[5],
                )
                for row in rows
            ]
        except Exception as e:
            logging.exception(f"Error fetching history: {e}")
            return []


async def get_all_history(user_id: int) -> list[GeneratedContentHistory]:
    return await asyncio.to_thread(_get_all_history_sync, user_id)


def _add_user_sync(username: str, email: str, password_hash: str) -> User | None:
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            stmt = text(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (:username, :email, :password_hash, :created_at)"
            )
            params = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.datetime.now().isoformat(),
            }
            cursor = conn.execute(stmt, params)
            conn.commit()
            new_id = cursor.lastrowid
            select_stmt = text("SELECT * FROM users WHERE id = :id")
            result = conn.execute(select_stmt, {"id": new_id})
            row = result.first()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    created_at=row[4],
                )
        except Exception as e:
            logging.exception(f"Error adding user: {e}")
    return None


async def add_user(username: str, email: str, password_hash: str) -> User | None:
    return await asyncio.to_thread(_add_user_sync, username, email, password_hash)


def _get_user_by_email_sync(email: str) -> User | None:
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            stmt = text("SELECT * FROM users WHERE email = :email")
            result = conn.execute(stmt, {"email": email})
            row = result.first()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    created_at=row[4],
                )
        except Exception as e:
            logging.exception(f"Error fetching user by email: {e}")
    return None


async def get_user_by_email(email: str) -> User | None:
    return await asyncio.to_thread(_get_user_by_email_sync, email)


def _get_user_by_username_sync(username: str) -> User | None:
    engine = rx.Model.get_db_engine()
    with engine.connect() as conn:
        try:
            stmt = text("SELECT * FROM users WHERE username = :username")
            result = conn.execute(stmt, {"username": username})
            row = result.first()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    created_at=row[4],
                )
        except Exception as e:
            logging.exception(f"Error fetching user by username: {e}")
    return None


async def get_user_by_username(username: str) -> User | None:
    return await asyncio.to_thread(_get_user_by_username_sync, username)