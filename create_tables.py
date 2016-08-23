import sqlite3

from git_code_debt import create_tables


def main():
    create_tables.main(('database.db', '--skip-default-metrics'))
    with sqlite3.connect('database.db') as db:
        db.execute('INSERT INTO metric_names VALUES (0, "InboxCount")')


if __name__ == '__main__':
    exit(main())
