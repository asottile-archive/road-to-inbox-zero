import calendar
import datetime
import sqlite3
import time

import httplib2
from apiclient.discovery import build
from oauth2client.client import Credentials


def connect_db():
    return sqlite3.connect('database.db')


def get_service():
    with open('client_creds.json') as client_creds:
        creds = Credentials.new_from_json(client_creds.read())

    http_auth = creds.authorize(httplib2.Http())

    return build('gmail', 'v1', http=http_auth)


def get_next_sha(db):
    (maxsha,), = db.execute('SELECT MAX(sha) FROM metric_data').fetchall()
    maxsha = int(maxsha if maxsha is not None else '-1')
    return '{:040d}'.format(maxsha + 1)


def insert_data(timestamp, unread_count):
    with connect_db() as db:
        next_sha = get_next_sha(db)
        db.execute(
            'INSERT INTO metric_data VALUES (?, ?, ?, ?)',
            (next_sha, 0, timestamp, unread_count),
        )


def get_timestamp():
    return calendar.timegm(datetime.datetime.now().utctimetuple())


def main():
    service = get_service()

    while True:
        ret = service.users().labels().get(userId='me', id='INBOX').execute()
        insert_data(get_timestamp(), ret['threadsUnread'])
        print('{} unread thread(s)'.format(ret['threadsUnread']))
        time.sleep(15)


if __name__ == '__main__':
    exit(main())
