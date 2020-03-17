echo This script is intended for sourcing!
pipenv shell "set -x FLASK_DEBUG 1; and set -x FLASK_APP \"bakalari_homework_tasklist:create_app()\"; and set -x DATABASE_URL (heroku config:get DATABASE_URL); and set -x SECRET_KEY "TEST. DO NOT USE IN PRODUCTION"; and clear; and clear; and echo Environment successfully created"
echo Environment was destroyed
