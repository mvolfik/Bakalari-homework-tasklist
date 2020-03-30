# Contributing guidelines

**Use common sense**. That _might_ be all you need.

## Development environment

This app uses Pipenv for dependency management. To open new console in the context of
the virtual environment with dependencies installed, run `pipenv install --dev` and
`pipenv shell`.

However, to run the app locally, you need to setup a few environment variables –
`DATABASE_URL` (PostgreSQL), `REDIS_URL` and
[`SECRET_KEY`](https://flask.palletsprojects.com/config/#SECRET_KEY). You might also
want to set `FLASK_ENV=development`.
 
To simplify this, there is the script `devenv.fish`, which does all of this for you.
All you need for it to work is to have the Heroku CLI installed, have your own instance
of the app on Heroku (it's completely free) and have this app in git remote (see
[Heroku tutorial](https://devcenter.heroku.com/articles/git#for-an-existing-heroku-app)).

Run the script simply as `fish devenv.fish`.

Inside this environment you can run the app with `flask run`, which uses the Werkzeug
development server for simpler debugging.

## Code style

Use the Black formatter (with default configuration) for Python code. As for templates
and other files, I use PyCharm's code formatting (get it for free as a student!). If
you use other editor, please see the existing code and try to do it similarly.

If you know any good HTML+Jinja formatter, please tell me.

## Dev chats

If you need any help, join our dev chat connected to the Telegram channel
[@bakatasklist](https://t.me/bakatasklist) or contact me directly
[@mvolfik](https://t.me/mvolfik)
