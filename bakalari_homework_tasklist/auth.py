from datetime import date
from urllib.error import URLError
from xml.etree import ElementTree

from bakalari_token import InvalidResponse, InvalidUsername, generate_token, process_url
from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf import FlaskForm
from requests import get
from wtforms.fields import PasswordField, StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, ValidationError

from .db import Message, User, db
from .utils import FlashColor, flash_form_errors, until_midnight

bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_message_category = FlashColor.WARNING_ORANGE
login_manager.login_message = "Pro zobrazení této stránky se musíte přihlásit"
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(user_id)
    if u is not None and u.token_date == date.today():
        return u
    else:
        return None


class LoginForm(FlaskForm):
    url = StringField(
        "Adresa bakalářů vaší školy", validators=[InputRequired("Musíte zadat url")]
    )
    username = StringField(
        "Uživatelské jméno",
        validators=[InputRequired("Musíte zadat uživatelské jméno")],
    )
    password = PasswordField("Heslo", validators=[InputRequired("Musíte zadat heslo")])


@bp.route("/login", methods=("GET", "POST"))
def login():
    today = date.today()
    if current_user.is_authenticated and current_user.token_date == today:
        return redirect(url_for("core.list_homeworks"))

    f = LoginForm()
    if f.validate_on_submit():

        # --- validate url
        url = process_url(f.url.data)
        try:
            token = generate_token(url, f.username.data, f.password.data)

        except InvalidUsername as e:
            flash(e, FlashColor.ERROR_RED)
        except InvalidResponse as e:
            db.session.add(
                Message(is_error=True, text="InvalidResponse: " + f.url.data)
            )
            db.session.commit()
            flash(e, FlashColor.ERROR_RED)
        except URLError as e:
            db.session.add(
                Message(
                    is_error=True, text="URLError {}: {}".format(e.reason, f.url.data)
                )
            )
            db.session.commit()
            flash(
                "Na dané adrese neexistuje server systému Bakaláři",
                FlashColor.ERROR_RED,
            )

        else:
            # --- validate token --> password
            req = get(url, params={"hx": token, "pm": "login"}, verify=False)
            print(req.content.decode())
            root = ElementTree.fromstring(req.content.decode())
            result = root.find("result").text
            if result == "-1":
                flash("Špatné heslo", FlashColor.ERROR_RED)
            elif result != "01":
                flash(
                    "Přihlášení se nezdařilo, server vrátil tuto chybu: "
                    + root.find("message").text,
                    FlashColor.ERROR_RED,
                )

            else:
                # --- check if new user
                ifuser = User.query.get({"url": url, "username": f.username.data})
                if ifuser is None:
                    session["username"] = f.username.data
                    session["name"] = root.find("jmeno").text
                    session["url"] = url
                    session["token"] = token
                    session["token_date"] = today.toordinal()
                    session["account_type"] = root.find("strtyp").text
                    return redirect(url_for("auth.first_import"), 303)
                else:
                    # --- update token?
                    if ifuser.token_date != today:
                        ifuser.token = token
                        ifuser.token_date = today
                        db.session.commit()

                    login_user(ifuser, remember=True, duration=until_midnight())
                    flash("Vítejte zpět!", FlashColor.CONFIRMATION_GREEN)
                    return redirect(url_for("core.list_homeworks"), 303)

    flash_form_errors(f)
    return render_template("login.html", form=f)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Byli jste odhlášeni", FlashColor.CONFIRMATION_GREEN)
    return redirect(url_for("home"))


class FirstImportForm(FlaskForm):
    date = DateField(
        "Označit jako hotové všechny úkoly zadané před",
        validators=[InputRequired("Musíte zadat datum")],
        default=date(2020, 2, 1),
    )

    @staticmethod
    def validate_date(_, field):
        if field.data > date.today():
            raise ValidationError("Nelze zadat datum v budoucnosti")


@bp.route("/first-import", methods=("GET", "POST"))
def first_import():
    today = date.today()
    if "token_date" not in session or date.fromordinal(session["token_date"]) != today:
        return redirect(url_for("auth.login"), 303)

    f = FirstImportForm()
    if f.validate_on_submit():
        # noinspection PyArgumentList
        u = User(
            username=session.pop("username"),
            url=session.pop("url"),
            token=session.pop("token"),
            token_date=today,
            name=session.pop("name"),
            account_type=session.pop("account_type"),
        )
        del session["token_date"]
        db.session.add(u)
        db.session.commit()
        login_user(u, remember=True, duration=until_midnight())
        flash(
            "Domácí úkoly nebyly naimportovány, tato aplikace ještě není dokončena",
            FlashColor.CONFIRMATION_GREEN,
        )
        return redirect(url_for("core.list_homeworks"), 303)

    flash_form_errors(f)
    return render_template("first_import.html", form=f)
