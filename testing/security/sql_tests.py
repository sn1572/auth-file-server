#!/usr/bin/env python3


import sys, os, unittest
fs_root = os.path.abspath('../../')
sys.path.insert(0, fs_root)
from file_server import app, db
from db_manager import in_context


@in_context
def print_table_names():
    print(db.metadata.tables.keys())


class ExampleTest(unittest.TestCase):

    def drop_t(self):
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    #unittest.main()
    print_table_names()
