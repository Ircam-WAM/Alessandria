#/bin/bash
PYTHON_BIN=python
DB_PATH=db/bibli.sqlite3
rm -f $DB_PATH
rm -rf alexandrie/migrations
$PYTHON_BIN ./manage.py migrate && \
$PYTHON_BIN ./manage.py loaddata --app alexandrie ref_data
$PYTHON_BIN ./manage.py runserver
