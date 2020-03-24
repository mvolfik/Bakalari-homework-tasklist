from collections import defaultdict
from datetime import date, datetime, time, timedelta

from flask import flash, get_flashed_messages
from flask.json import JSONEncoder
from flask_login import current_user
from flask_wtf import FlaskForm


class FlashColor:
    ERROR_RED = "#F99"
    CONFIRMATION_GREEN = "#4BB543"
    INFO_YELLOW = "#FCF712"
    WARNING_ORANGE = "#FF6700"


def flash_form_errors(f: FlaskForm):
    for field in f.errors.values():
        for e in field:
            flash(e, FlashColor.ERROR_RED)


def until_midnight():
    dt = datetime.now()
    return datetime.combine(dt + timedelta(days=1), time.min) - dt


# --- templates helpers
def get_grouped_flashes():
    """Returns a dictionary with group names as keys and lists of messages as values"""
    msgs = get_flashed_messages(with_categories=True)
    groups = defaultdict(list)
    for group, msg in msgs:
        groups[group].append(msg)
    return groups


def create_navbar(sender, template, context, **extra):
    if current_user.is_authenticated:
        context["navigation_bar"] = (
            ("home", "Úvod", ""),
            ("core.list_homeworks", "Domácí úkoly", ""),
            ("core.contact", "Kontakt", ""),
            ("auth.logout", "Odhlásit se", ""),
        )
    else:
        context["navigation_bar"] = (
            ("home", "Úvod", ""),
            ("core.contact", "Kontakt", ""),
            ("auth.login", "Přihlásit se", ""),
        )


class BetterJSONEncoder(JSONEncoder):
    def default(self, o):
        if type(o) == datetime:
            return {
                "display": "{}. {}".format(
                    o.day,
                    o.strftime("%b %y" + (" %H:%M" if o.time() != time.min else "")),
                ),
                "timestamp": o.timestamp(),
            }
        elif type(o) == date:
            return {
                "display": "{}. {}".format(o.day, o.strftime("%b %y")),
                "timestamp": o.toordinal(),
            }
        else:
            return super(BetterJSONEncoder, self).default(o)
