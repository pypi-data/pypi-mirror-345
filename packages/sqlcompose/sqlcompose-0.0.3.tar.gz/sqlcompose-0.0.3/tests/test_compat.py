# pyright: basic
from unittest import TestCase, main
from sys import platform

from sqlcompose.core.compat import fix_path, get_relative_path

class Test(TestCase):

    def test_fix_path(self):
        if platform == "win32":
            tests = {
                "sql\\file.sql" : "sql\\file.sql",
                "sql\\file.sql" : "sql/file.sql",
            }
        else:
            tests = {
                "sql/file.sql" : "sql\\file.sql",
                "sql/file.sql" : "sql/file.sql",
            }

        for expected_result, file_path in tests.items():
            result = fix_path(file_path)
            self.assertEqual(result, expected_result)


    def test_get_relative_path(self):
        if platform == "win32":
            tests = {
                "sql\\file.sql" : ("sql\\file.sql", "sql\\file.sql"),
                "sql\\file.sql" : ("sql\\file.sql", "c:\\app\\"),
                "sql\\file.sql" : ("c:\\app\\sql\\file.sql", "c:\\app\\"),
            }

            p = "sql\\file.sql"
            self.assertEqual(p, get_relative_path(p, p))
        else:
            tests = {
                "sql/file.sql" : ("sql/file.sql", "sql/file.sql"),
                "sql/file.sql" : ("sql/file.sql", "/app/"),
                "sql/file.sql" : ("/app/sql/file.sql", "/app/"),
            }
            p = "sql/file.sql"
            self.assertEqual(p, get_relative_path(p, p))

        for expected_result, (file_path, root) in tests.items():
            result = get_relative_path(file_path, root)
            self.assertEqual(result, expected_result)


if __name__ == '__main__':
    main()

