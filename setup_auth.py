import _thread
import json
import logging
import os
import stat
import threading
import time

import flask
from oauth2client.client import flow_from_clientsecrets
from oauth2client.clientsecrets import InvalidClientSecretsError


def get_config():
    with open('config.json') as config:
        return type('Config', (object,), json.load(config))


def get_client():
    try:
        with open('client_secrets.json') as client_secrets:
            contents = json.load(client_secrets)
    except IOError:
        print('- client_secrets.json does not exist')
        return None

    redirect_uri = contents['web']['redirect_uris'][0]

    try:
        flow = flow_from_clientsecrets(
            'client_secrets.json',
            scope='https://www.googleapis.com/auth/gmail.labels',
            redirect_uri=redirect_uri,
        )
        flow.params['access_type'] = 'offline'
        flow.params['approval_prompt'] = 'force'
        return flow
    except InvalidClientSecretsError:
        print('- invalid client_secrets.json detected')
        return None


app = flask.Flask(__name__)

# Disable flask logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def sleep_and_exit():
    time.sleep(1)
    _thread.interrupt_main()


@app.route('/oauth2callback')
def oauth2callback():
    if 'error' in flask.request.args:
        msg = 'Error: {}'.format(flask.request.args['error'])
        print(msg)
        return msg

    flow = get_client()
    creds = flow.step2_exchange(flask.request.args['code'])
    with os.fdopen(
        os.open(
            'client_creds.json',
            os.O_WRONLY | os.O_CREAT,
            stat.S_IRUSR | stat.S_IWUSR,
        ),
        'w',
    ) as client_creds:
        client_creds.write(creds.to_json())
    print('client_creds.json has been written!')
    threading.Thread(target=sleep_and_exit).start()
    return 'Successfully authorized!'


def main():
    cfg = get_config()

    print('=' * 79)
    print('1: Create a project')
    print('=' * 79)
    print('- Set up a project here (use the dropdown at the top):')
    print('  https://console.developers.google.com/apis/credentials')
    print('- For instance, I created a project called "Road to inbox zero"')
    print(
        "- See https://support.google.com/cloud/answer/6251787 if you're "
        'having issues'
    )

    print('=' * 79)
    print('2: Create a Web Application oauth client id')
    print('=' * 79)
    print('- Select your project you just created in the dropdown at the top:')
    print('  https://console.developers.google.com/apis/credentials')
    print('- [Create credentials]')
    print('- [Oauth client ID]')
    print('- [Configure consent screen]')
    print("- Enter a project name, you shouldn't need to fill out the rest")
    print('- [Save]')
    print('- [Web application]')
    print('- Optionally name your client (not necessary)')
    print('- Set the authorized redirect URI')
    print('  (ex: http://localhost:{}/oauth2callback)'.format(cfg.port))
    print('[Create]')

    print('=' * 79)
    print('3: Download client_secrets.json')
    print('=' * 79)
    print(
        '- Download the client_secrets.json file and save it as '
        'client_secrets.json'
    )
    print('  (Be sure to `chmod 600 client_secrets.json`)')
    while get_client() is None:
        input("- Press enter once you've done so")

    print('=' * 79)
    print('4: Authorize your gmail user')
    print('=' * 79)
    print(' - Load {}'.format(get_client().step1_get_authorize_url()))

    try:
        app.run(debug=False, host=cfg.host, port=cfg.port)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    exit(main())
