import sqlite3
import time

import httplib2
from apiclient.discovery import build
from oauth2client.client import Credentials


def _table_exists(db, name):
    return bool(db.execute(
        'SELECT name FROM sqlite_master WHERE type = "table" and name = ?',
        (name,)
    ).fetchall())


def connect_db():
    return sqlite3.connect('database.db')


def create_tables_if_not_existing():
    with connect_db() as db:
        if not _table_exists(db, 'data'):
            db.execute(
                'CREATE TABLE data (\n'
                '    timestamp_ms INT NOT NULL,\n'
                '    unread_count INT NOT NULL\n'
                ')'
            )


def get_service():
    with open('client_creds.json') as client_creds:
        creds = Credentials.new_from_json(client_creds.read())

    http_auth = creds.authorize(httplib2.Http())

    return build('gmail', 'v1', http=http_auth)


def insert_data(*args):
    with connect_db() as db:
        db.execute('INSERT INTO data VALUES (?, ?)', args)


def main():
    create_tables_if_not_existing()
    service = get_service()

    while True:
        ret = service.users().labels().get(userId='me', id='INBOX').execute()
        insert_data(int(time.time() * 1000), ret['threadsUnread'])
        print('{} unread thread(s)'.format(ret['threadsUnread']))
        time.sleep(15)


if __name__ == '__main__':
    exit(main())
