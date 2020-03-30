pipenv shell "\
    set -x FLASK_ENV development; \
and set -x FLASK_APP 'bakalari_homework_tasklist:create_app()'; \
and set -x DATABASE_URL (heroku config:get DATABASE_URL); \
and set -x REDIS_URL (heroku config:get REDIS_URL); \
and set -x SECRET_KEY 'TEST. DO NOT USE IN PRODUCTION'; \
and clear; and clear; and echo Environment successfully created; \
or exit"
echo Environment was destroyed
