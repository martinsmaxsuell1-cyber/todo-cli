import unittest
from unittest.mock import patch
import io
import os
import tempfile
from todocli.cli import run_cli
from todocli.db import Database


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()
        self.db = Database(db_path=self.temp_path)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def run_command(self, args):
        f = io.StringIO()
        with patch("sys.stdout", f):
            code = run_cli(args, db=self.db)
        return code, f.getvalue()

    def test_add_and_list(self):
        code, out = self.run_command(["add", "Criar testes unitários", "-p", "high", "-t", "dev"])
        self.assertEqual(code, 0)
        self.assertIn("Tarefa adicionada", out)

        code, out = self.run_command(["list"])
        self.assertEqual(code, 0)
        self.assertIn("Criar testes unitários", out)
        self.assertIn("#dev", out)

    def test_quick_add(self):
        code, out = self.run_command(["Nova tarefa rápida"])
        self.assertEqual(code, 0)
        self.assertIn("Tarefa adicionada", out)

        code, out = self.run_command(["list"])
        self.assertEqual(code, 0)
        self.assertIn("Nova tarefa rápida", out)

    def test_done_and_undo(self):
        t_id = self.db.add_todo("Testar conclusão")
        code, out = self.run_command(["done", str(t_id)])
        self.assertEqual(code, 0)
        self.assertIn("concluída", out.lower())

        todo = self.db.get_todo(t_id)
        self.assertEqual(todo["status"], "completed")

        code, out = self.run_command(["undo", str(t_id)])
        self.assertEqual(code, 0)
        todo = self.db.get_todo(t_id)
        self.assertEqual(todo["status"], "pending")

    def test_search_and_stats(self):
        self.db.add_todo("Estudar Termux", tags="android")
        code, out = self.run_command(["search", "Termux"])
        self.assertEqual(code, 0)
        self.assertIn("Estudar Termux", out)

        code, out = self.run_command(["stats"])
        self.assertEqual(code, 0)
        self.assertIn("Estatísticas", out)


if __name__ == "__main__":
    unittest.main()
