"""Database layer for Todo CLI using SQLite."""

from __future__ import annotations
import os
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

DEFAULT_DB_DIR = os.path.expanduser("~/.local/share/todo-cli")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "todos.db")


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
                    tags TEXT DEFAULT '',
                    due_date TEXT DEFAULT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed')),
                    created_at TEXT DEFAULT (datetime('now', 'localtime')),
                    completed_at TEXT DEFAULT NULL
                );
                """
            )

    def add_todo(
        self,
        title: str,
        priority: str = "medium",
        tags: str = "",
        due_date: Optional[str] = None,
        notes: str = "",
    ) -> int:
        norm_priority = priority.lower() if priority else "medium"
        if norm_priority not in ("low", "medium", "high", "urgent"):
            norm_priority = "medium"

        norm_tags = ",".join(t.strip() for t in tags.split(",") if t.strip()) if tags else ""

        with self.conn:
            cur = self.conn.execute(
                """
                INSERT INTO todos (title, notes, priority, tags, due_date, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
                """,
                (title.strip(), notes.strip(), norm_priority, norm_tags, due_date),
            )
            return cur.lastrowid

    def get_todo(self, todo_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_todos(
        self,
        status: Optional[str] = "pending",
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM todos WHERE 1=1"
        params: List[Any] = []

        if status and status != "all":
            query += " AND status = ?"
            params.append(status)

        if priority and priority != "all":
            query += " AND priority = ?"
            params.append(priority.lower())

        if tag:
            query += " AND (',' || tags || ',') LIKE ?"
            params.append(f"%,{tag.strip()}%,")

        if search:
            query += " AND (title LIKE ? OR notes LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        # Order by status (pending first), priority weight, then id
        query += """
            ORDER BY 
                CASE status WHEN 'pending' THEN 0 ELSE 1 END,
                CASE priority 
                    WHEN 'urgent' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    WHEN 'low' THEN 4 
                    ELSE 5 
                END,
                id ASC
        """

        cur = self.conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def complete_todo(self, todo_id: int) -> bool:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            cur = self.conn.execute(
                "UPDATE todos SET status = 'completed', completed_at = ? WHERE id = ?",
                (now_str, todo_id),
            )
            return cur.rowcount > 0

    def uncomplete_todo(self, todo_id: int) -> bool:
        with self.conn:
            cur = self.conn.execute(
                "UPDATE todos SET status = 'pending', completed_at = NULL WHERE id = ?",
                (todo_id,),
            )
            return cur.rowcount > 0

    def update_todo(self, todo_id: int, **kwargs) -> bool:
        allowed = {"title", "notes", "priority", "tags", "due_date"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return False

        if "priority" in updates:
            p = updates["priority"].lower()
            if p not in ("low", "medium", "high", "urgent"):
                updates["priority"] = "medium"

        if "tags" in updates and updates["tags"] is not None:
            updates["tags"] = ",".join(t.strip() for t in updates["tags"].split(",") if t.strip())

        clauses = [f"{col} = ?" for col in updates.keys()]
        values = list(updates.values()) + [todo_id]

        with self.conn:
            cur = self.conn.execute(
                f"UPDATE todos SET {', '.join(clauses)} WHERE id = ?",
                values,
            )
            return cur.rowcount > 0

    def delete_todo(self, todo_id: int) -> bool:
        with self.conn:
            cur = self.conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            return cur.rowcount > 0

    def clear_completed(self) -> int:
        with self.conn:
            cur = self.conn.execute("DELETE FROM todos WHERE status = 'completed'")
            return cur.rowcount

    def get_stats(self) -> Dict[str, Any]:
        cur = self.conn.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'pending' AND priority = 'urgent' THEN 1 ELSE 0 END) as urgent_pending,
                SUM(CASE WHEN status = 'pending' AND priority = 'high' THEN 1 ELSE 0 END) as high_pending
            FROM todos
            """
        )
        row = cur.fetchone()
        total = row["total"] or 0
        completed = row["completed"] or 0
        pending = row["pending"] or 0
        rate = round((completed / total * 100), 1) if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "urgent_pending": row["urgent_pending"] or 0,
            "high_pending": row["high_pending"] or 0,
            "completion_rate": rate,
        }

    def close(self) -> None:
        if self.conn:
            self.conn.close()
