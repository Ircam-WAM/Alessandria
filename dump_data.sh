#/bin/bash
PYTHON_BIN=python

#$PYTHON_BIN ./manage.py dumpdata auth.User --indent 4 > alexandrie/fixtures/users.json
$PYTHON_BIN ./manage.py dumpdata alexandrie auth --indent 4 > alexandrie/fixtures/ref_data.json
