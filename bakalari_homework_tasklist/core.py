from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length, Optional

from .db import Homework, Message, db
from .utils import FlashColor, flash_form_errors

bp = Blueprint("core", __name__)


class ContactForm(FlaskForm):
    is_error = BooleanField("Informuji o chybě v aplikaci")
    email = EmailField(
        "Tvůj e-mail pro odpověd (volitelný)",
        validators=[
            Optional(),
            Email("Do pole e-mail nezadávejte nic, nebo zadejte platný e-mail"),
        ],
    )
    text = TextAreaField(
        "Text zprávy",
        validators=[
            InputRequired("Zpráva bez textu nemá smysl..."),
            Length(min=10, message="Zpráva by měla být alespoň 10 znaků, ne?"),
        ],
    )


@bp.route("/contact", methods=("GET", "POST"))
def contact():
    is_error = request.args.get("error", "no") == "yes"
    f = ContactForm(is_error=is_error)
    if f.validate_on_submit():
        db.session.add(
            Message(is_error=f.is_error.data, email=f.email.data, text=f.text.data)
        )
        db.session.commit()
        flash("Zpráva byla odeslána, děkuji", FlashColor.CONFIRMATION_GREEN)
        return redirect(url_for("core.contact"), 303)

    flash_form_errors(f)
    return render_template("contact.html", form=f)


@bp.route("/list-homeworks")
@login_required
def list_homeworks():
    subjects = (
        db.session.query(Homework.subject, Homework.subject_short)
        .group_by(Homework.subject, Homework.subject_short)
        .filter_by(user_id=current_user.id)
        .all()
    )
    return render_template("list_homeworks.html", subjects=subjects)


@bp.route("/fetch-new")
@login_required
def fetch_new():
    flash(
        "Import nových úkolů byl zahájen, vyčkejte prosím&hellip;",
        FlashColor.CONFIRMATION_GREEN,
    )
    return redirect(url_for("core.list_homeworks"), 303)
