import sqlite3
import logging
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection(db_path='users.db'):
    """Context manager для безопасной работы с БД"""
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка БД: {e}", exc_info=True)
        raise
    finally:
        conn.close()


def init_db():
    """Создаёт таблицу если её нет"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id          INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE,
                    name        TEXT NOT NULL,
                    phone       TEXT NOT NULL,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}", exc_info=True)
        raise


def save_user(telegram_id: int, name: str, phone: str):
    """Сохраняет или обновляет пользователя"""
    if not name or len(name) > 100:
        raise ValueError("Некорректное имя пользователя")
    if not phone or len(phone) < 7 or len(phone) > 20:
        raise ValueError("Некорректный номер телефона")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (telegram_id, name, phone)
                VALUES (?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    name  = excluded.name,
                    phone = excluded.phone
            """, (telegram_id, name, phone))
            logger.debug(f"Пользователь {telegram_id} сохранён в БД")
    except sqlite3.IntegrityError as e:
        logger.error(f"Ошибка уникальности при сохранении {telegram_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователя {telegram_id}: {e}", exc_info=True)
        raise


def get_user(telegram_id: int):
    """Возвращает пользователя по telegram_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            return row
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {telegram_id}: {e}", exc_info=True)
        return None


def get_all_users():
    """Получает всех пользователей из БД"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, telegram_id, name, phone, created_at 
                FROM users 
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка получения всех пользователей: {e}", exc_info=True)
        return []
