import logging
from datetime import date, datetime, time

from flask import Blueprint, current_app, jsonify, request, session
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from .auth import FirstImportForm
from .db import Homework, db

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/load")
@login_required
def load_data():
    hws = (
        Homework.query.filter_by(user_id=current_user.id)
        .options(joinedload(Homework.attachments))
        .all()
    )
    return jsonify(hws)


@bp.route("/start-import", methods=("POST",))
@login_required
def start_import():
    try:
        if current_app.config["PAUSE_REQUESTS"]:
            return jsonify(ok=False, reason=5)
        job = current_app.task_queue.enqueue(
            "bakalari_homework_tasklist.worker_tasks.fetch_new_homework",
            current_user.id,
        )
        return jsonify(ok=True, job_id=job.get_id())
    except Exception:
        return jsonify(ok=False), 500


@bp.route("/first-import", methods=("POST",))
def first_import():
    try:
        if current_app.config["PAUSE_REQUESTS"]:
            return jsonify(ok=False, reason=5)

        f = FirstImportForm()
        if f.validate():
            job = current_app.task_queue.enqueue(
                "bakalari_homework_tasklist.worker_tasks.first_import",
                datetime.combine(f.date.data, time.min),
                username=session.pop("username"),
                url=session.pop("url"),
                token=session.pop("token"),
                token_date=date.fromordinal(session.pop("token_date")),
                name=session.pop("name"),
                account_type=session.pop("account_type"),
            )
            job_id = job.get_id()
            session["login_job_id"] = job_id
            return jsonify(ok=True, job_id=job_id)
        else:
            return jsonify(ok=False, reason=1, error=f.date.errors[0]), 400
    except Exception as e:
        logging.exception(e)
        return jsonify(ok=False, reason=-1), 500


@bp.route("/get-job-result", methods=("POST",))
def get_job_result():
    try:
        job = current_app.task_queue.fetch_job(request.form["job_id"])
        return jsonify(
            ok=True, finished=job.is_finished, error=job.is_failed, result=job.result
        )
    except Exception as e:
        logging.exception(e)
        return jsonify(ok=False, reason=-1), 500


@bp.route("/change-status", methods=("POST",))
def change_status():
    try:
        hw = Homework.query.get(request.form["hw_id"])
        if hw is None:
            return jsonify(ok=False)
        if not current_user.is_authenticated or hw.user_id != current_user.id:
            return jsonify(ok=False), 401

        if request.form["action"] == "mark-done":
            hw.is_done = True
            db.session.commit()
            return jsonify(ok=True)

        elif request.form["action"] == "mark-undone":
            hw.is_done = False
            db.session.commit()
            return jsonify(ok=True)

        elif request.form["action"] == "unpostpone":
            hw.postponed_until = None
            db.session.commit()
            return jsonify(ok=True)

        elif request.form["action"] == "postpone":
            d = datetime.strptime(request.form["until"], "%Y-%m-%d").date()
            hw.postponed_until = d
            db.session.commit()
            return jsonify(ok=True, new_data=d)
        else:
            return jsonify(ok=False)

    except Exception as e:
        logging.exception(e)
        return jsonify(ok=False, reason=-1)
