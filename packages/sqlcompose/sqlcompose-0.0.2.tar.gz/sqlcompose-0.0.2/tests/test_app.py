# pyright: basic
from unittest import TestCase, main

from sqlcompose.core.app import app

class Test(TestCase):
    # def test_nonexisting(self):
    #     _result, code = app(["nonexisting.sql"])
    #     self.assertEqual(code, 1)

    def test_missing_args(self):
        _result, code = app([])
        self.assertEqual(code, 2)

    def test_existing_file_by_path(self):
        result, code = app(["tests/main-query.sql"])
        self.assertGreater(len(result), 0)
        self.assertEqual(code, 0)

    def test_sql(self):
        result, code = app(["SELECT * FROM $INCLUDE(tests/main-query.sql)"])
        # print(result)
        self.assertGreater(len(result), 0)
        self.assertEqual(code, 0)


if __name__ == '__main__':
    main()

