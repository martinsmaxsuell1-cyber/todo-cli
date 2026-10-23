import unittest
import sqlite3
import os
import tempfile
from todocli.db import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use a temporary database file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()
        self.db = Database(db_path=self.temp_path)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_add_and_get_todo(self):
        todo_id = self.db.add_todo(
            title="Aprender Python 3.14",
            priority="high",
            tags="dev,python",
            due_date="2026-12-31",
            notes="Estudar novas features",
        )
        self.assertIsInstance(todo_id, int)
        self.assertGreater(todo_id, 0)

        todo = self.db.get_todo(todo_id)
        self.assertIsNotNone(todo)
        self.assertEqual(todo["title"], "Aprender Python 3.14")
        self.assertEqual(todo["priority"], "high")
        self.assertEqual(todo["tags"], "dev,python")
        self.assertEqual(todo["status"], "pending")
        self.assertIsNone(todo["completed_at"])

    def test_complete_and_uncomplete_todo(self):
        todo_id = self.db.add_todo("Comprar mantimentos")
        self.assertTrue(self.db.complete_todo(todo_id))
        
        todo = self.db.get_todo(todo_id)
        self.assertEqual(todo["status"], "completed")
        self.assertIsNotNone(todo["completed_at"])

        # Undo complete
        self.assertTrue(self.db.uncomplete_todo(todo_id))
        todo = self.db.get_todo(todo_id)
        self.assertEqual(todo["status"], "pending")
        self.assertIsNone(todo["completed_at"])

    def test_list_and_filters(self):
        self.db.add_todo("Tarefa 1", priority="low", tags="pessoal")
        self.db.add_todo("Tarefa 2", priority="high", tags="trabalho")
        self.db.add_todo("Tarefa 3", priority="urgent", tags="trabalho")

        # Test filter by priority
        highs = self.db.list_todos(priority="high")
        self.assertEqual(len(highs), 1)
        self.assertEqual(highs[0]["title"], "Tarefa 2")

        # Test filter by tag
        work = self.db.list_todos(tag="trabalho")
        self.assertEqual(len(work), 2)

        # Test search
        found = self.db.list_todos(search="Tarefa 1")
        self.assertEqual(len(found), 1)

    def test_delete_and_clear(self):
        id1 = self.db.add_todo("Item 1")
        id2 = self.db.add_todo("Item 2")
        self.db.complete_todo(id1)

        self.assertTrue(self.db.delete_todo(id2))
        self.assertIsNone(self.db.get_todo(id2))

        # Clear completed
        cleared = self.db.clear_completed()
        self.assertEqual(cleared, 1)
        self.assertIsNone(self.db.get_todo(id1))

    def test_stats(self):
        id1 = self.db.add_todo("T1", priority="urgent")
        id2 = self.db.add_todo("T2", priority="high")
        self.db.complete_todo(id1)

        stats = self.db.get_stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(stats["completion_rate"], 50.0)


if __name__ == "__main__":
    unittest.main()
