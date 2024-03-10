#!/usr/local/bin/bash

set -e
set -x

# make sure linting checks pass
make lint

# static
python manage.py collectstatic --noinput

# make sure latest requirements are installed
pip install -r requirements.txt

# push origin
git push -v origin master

# pull on server and reload
ssh root@oscarator.com 'cd /opt/apps/oscarator \
    && git pull \
    && source venv/bin/activate \
    && pip install -r requirements.txt \
    && python3 manage.py collectstatic --noinput \
    && source .envrc \
    && python3 manage.py migrate \
    && touch /etc/uwsgi/vassals/oscarator.ini'
