#!/bin/bash
set -o errexit

case "$1" in
  setup)
    python create_json_data.py
    ;;
  dgraph)
    python dbs/load_dgraph.py
    ;;
  dgraph_live)
    python dbs/load_dgraph_live.py
    dgraph live --files /tmp/live_json.json --alpha $DGRAPH_URL --zero $DGRAPH_ZERO_URL
    ;;
  postgres)
    python dbs/load_sql.py
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_URL -d $POSTGRES_DB -U $POSTGRES_USER -p 5432 -1 -q -f "/tmp/temp.sql"
    bash
    ;;
  *)
    exec "$@"
esac