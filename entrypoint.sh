#!/bin/sh

python --version
echo "Current working directory: `pwd`"
echo "App run command args: $@"

run_service() {
  echo "Generated config, starting ytube app..."
  env $(cat /code/config/.env | xargs) /usr/local/bin/uvicorn server.app:app --host=0.0.0.0 --port=6006 --workers=4
}

run_worker() {
  echo "Generated config, starting ytube workers..."
  env $(cat /code/config/.env | xargs)  /usr/local/bin/celery -A worker.scheduler beat
}

run_scheduler() {
  echo "Generated config, starting ytube scheduler..."
  env $(cat /code/config/.env | xargs)  /usr/local/bin/celery -A worker.task_worker worker
}

CMD_TO_EXECUTE="$1"

case "$CMD_TO_EXECUTE" in
  "run_app")
    run_service
    exit $?
  ;;
  "run_worker")
    run_worker
    exit $?
  ;;
  "run_scheduler")
    run_scheduler
    exit $?
esac

exec "$@"