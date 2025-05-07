# pyright: basic
from unittest import TestCase, main

from sqlcompose import loads, load, CircularDependencyError
from sqlcompose.core.functions import compose

class Test(TestCase):
    def test_nonexisting(self):
        self.assertRaises(FileNotFoundError, load, "nonexisting.sql")
        self.assertRaises(FileNotFoundError, load, "tests/non_existing_include.sql")
        self.assertRaises(FileNotFoundError, compose, "select * from $INCLUDE(some_file_that_does_not_exist.sql)", "SQL", ".", ".")

        filename = "tests/existing_include.sql"
        with open(filename, "r", encoding="utf-8") as file:
            self.assertRaises(FileNotFoundError, compose, file.read(), filename, filename, ".")

    def test_reuse_composition(self):
        result = compose("select * from $INCLUDE(tests/includes/included-query3.sql)", "SQL", ".", ".")
        # print(result)
        self.assertTrue(len(result) > 0)


    def test_existing_file_by_path(self):
        result = load("tests/main-query.sql")
        # print(result)
        self.assertTrue(len(result) > 0)

    def test_sql(self):
        result = loads("SELECT * FROM $INCLUDE(tests/main-query.sql)")
        # print(result)
        self.assertTrue(len(result) > 0)

    def test_circular_dependency(self):
        self.assertRaises(CircularDependencyError, load, "tests/circular_left.sql")



if __name__ == '__main__':
    main()

