web:    gunicorn "bakalari_homework_tasklist:create_app()"
worker: rq worker homework-fetcher -u $REDIS_URL -c bakalari_homework_tasklist.rq_sentry
