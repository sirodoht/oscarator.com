#!/usr/local/bin/bash

set -e
set -x

# make sure linting checks pass
make lint

# static
python manage.py collectstatic --noinput

# start postgres server
set +e
DID_WE_START_PG=0
PGDATA=postgres-data/ pg_ctl status | grep 'is running'
# if pg is running, grep will succeed, which means exit code 0
if [ ${PIPESTATUS[1]} -eq 1 ]; then
    PGDATA=postgres-data/ pg_ctl start
    DID_WE_START_PG=1
fi
set -e

# make sure latest requirements are installed
pip install -r requirements.txt

# stop postgres server
if [ $DID_WE_START_PG -eq 1 ]; then
    PGDATA=postgres-data/ pg_ctl stop
fi

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
