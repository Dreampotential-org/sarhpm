#!/bin/sh
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
exec "$@"
