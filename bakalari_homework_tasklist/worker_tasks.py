from datetime import datetime
from xml.etree import ElementTree

import requests

from . import create_app
from .db import Attachment, Homework, HomeworkState, User, db

a = create_app()
a.app_context().push()


# --- Helpers
def parse_hw(ukol: ElementTree, state: HomeworkState, hw_id=None):
    hw_id = hw_id if hw_id is not None else ukol.find("id").text
    return Homework(
        baka_id=hw_id,
        assigned=datetime.strptime(ukol.find("zadano").text, "%y%m%d%H%M"),
        due=datetime.strptime(ukol.find("nakdy").text, "%y%m%d%H%M"),
        subject=ukol.find("predmet").text,
        description=ukol.find("popis").text,
        state=state,
    )


def find_attachments(ukol: ElementTree, base_url: str):
    for attachment in ukol.find("attachments").findall("attachment"):
        url = "{}?hx={}&pm=priloha&fileId={}".format(
            base_url, "{}", attachment.find("id").text.replace(" ", "%20%20%20")
        )  # we keep {} instead of token so that it can be filled later
        yield Attachment(filename=attachment.find("name").text, dl_link=url)


# --- Actual tasks
def fetch_new_homework(user_id):
    u: User = User.query.get(user_id)
    if u is None:
        return
    known = [hw.baka_id for hw in Homework.query.filter_by(user_id=user_id).all()]
    req = requests.get(u.url, params={"hx": u.token, "pm": "ukoly"})
    root = ElementTree.fromstring(req.content.decode())[0]

    for ukol in root.findall("ukol"):
        hw_id = ukol.find("id").text
        if hw_id not in known:
            hw: Homework = parse_hw(ukol, HomeworkState.TODO, hw_id)
            u.homeworks.append(hw)
            for attachment in find_attachments(ukol, u.url):
                hw.attachments.append(attachment)

    db.session.commit()  # changes are picked up automatically as we're adding to User


def first_update(user_id, undone_since):
    u = User.query.get(user_id)
    if u is None:
        return
    req = requests.get(u.url, params={"hx": u.token, "pm": "ukoly"})
    root = ElementTree.fromstring(req.content.decode())[0]

    for ukol in root.findall("ukol"):
        hw: Homework = parse_hw(ukol, HomeworkState.TODO)
        if hw.assigned < undone_since:
            hw.state = HomeworkState.DONE
        u.homeworks.append(hw)
        for attachment in find_attachments(ukol, u.url):
            hw.attachments.append(attachment)

    db.session.commit()


# TODO: Add a midnight task to shift all "postponed until [the next day]" homework to "TODO"
#  will probably use ATrigger scheduling
