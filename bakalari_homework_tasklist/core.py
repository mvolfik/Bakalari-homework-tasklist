from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms.fields import BooleanField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length, Optional

from .db import Homework, HomeworkState, Message, db
from .utils import FlashColor, flash_form_errors

bp = Blueprint("core", __name__)


class ContactForm(FlaskForm):
    is_error = BooleanField("Informuji o chybě v aplikaci")
    email = EmailField(
        "Můj e-mail pro odpověd (volitelný)",
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
    reloader = False
    if "running_jobs" in session:
        job_ids = session["running_jobs"][:]
        for job_id in job_ids:
            job = current_app.task_queue.fetch_job(job_id)
            if job.is_finished:
                session["running_jobs"].remove(job_id)
            elif job.is_failed:
                flash(
                    "Při importu úkolů z Bakalářů nastala chyba, zkuste to prosím znovu",
                    FlashColor.INFO_YELLOW,
                )
                session["running_jobs"].remove(job_id)
            else:
                reloader = True
        session.modified = True
    hws = (
        Homework.query.filter_by(user_id=current_user.id)
        .options(joinedload(Homework.attachments))
        .all()
    )
    hwgroups = {state.name: [] for state in HomeworkState}
    for hw in hws:
        hwgroups[hw.state.name].append(hw)
    return render_template("list_homeworks.html", hwgroups=hwgroups, reloader=reloader,)


@bp.route("/fetch-new")
@login_required
def fetch_new():
    job = current_app.task_queue.enqueue(
        "bakalari_homework_tasklist.worker_tasks.fetch_new_homework", current_user.id
    )
    if "running_jobs" not in session:
        session["running_jobs"] = []
    session["running_jobs"].append(job.get_id())
    session.modified = True
    flash(
        "Import nových úkolů byl zahájen, vyčkejte prosím&hellip;",
        FlashColor.CONFIRMATION_GREEN,
    )
    return redirect(url_for("core.list_homeworks"), 303)
