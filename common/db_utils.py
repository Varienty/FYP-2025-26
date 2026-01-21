import os
from typing import Any, Dict, List, Optional, Tuple

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# Load .env if present from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'student_attendance'),
    'port': int(os.getenv('DB_PORT', '3306')),
}

_pool: Optional[pooling.MySQLConnectionPool] = None

def _get_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="app_pool",
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            pool_reset_session=True,
            **DB_CONFIG,
        )
    return _pool


def get_connection():
    return _get_pool().get_connection()


def query_one(sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()


def query_all(sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql: str, params: Tuple[Any, ...] = ()) -> int:
    """Execute INSERT/UPDATE/DELETE. Returns affected rows."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()
