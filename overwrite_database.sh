#!/usr/bin/env bash
# overwrite_database.sh
# Overwrites local sqlite database with production one.


set -o errexit
set -o nounset
set -o pipefail

scp root@oscarator.com:/var/www/oscarator/db.sqlite3 .
