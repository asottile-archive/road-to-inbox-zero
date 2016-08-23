road-to-inbox-zero
==================

I went on vacation for two weeks and didn't read my email at all.  I wanted to
graph my progress as I processed my large inbox queue.

### Set things up
- `cp config.example.json config.json`
- `$EDITOR config.json`
- `make venv`
- `. venv/bin/activate`
- `python setup_auth.py`
- `python create_tables.py`

### Run the application
- `make venv`
- `. venv/bin/activate`
- `pgctl start`
