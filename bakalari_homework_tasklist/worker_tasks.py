from datetime import datetime
from xml.etree import ElementTree

import requests

from . import create_app
from .db import Attachment, Homework, User, db

a = create_app()
a.app_context().push()


# --- Helpers
def parse_hw(ukol: ElementTree, hw_id=None):
    hw_id = hw_id if hw_id is not None else ukol.find("id").text
    return Homework(
        baka_id=hw_id,
        assigned=datetime.strptime(ukol.find("zadano").text, "%y%m%d%H%M"),
        due=datetime.strptime(ukol.find("nakdy").text, "%y%m%d%H%M"),
        subject=ukol.find("predmet").text,
        subject_short=ukol.find("zkratka").text,
        description=ukol.find("popis").text,
    )


def find_attachments(ukol: ElementTree, base_url: str):
    for attachment in ukol.find("attachments").findall("attachment"):
        url = "{}?hx={}&pm=priloha&fileId={}".format(
            base_url, "{}", attachment.find("id").text.replace(" ", "%20")
        )  # we keep {} instead of token so that it can be filled later
        yield Attachment(filename=attachment.find("name").text, url_placeholder=url)


# --- Actual tasks
def fetch_new_homework(user_id):
    if a.config["PAUSE_REQUESTS"]:
        return 0

    u: User = User.query.get(user_id)
    known = [hw.baka_id for hw in Homework.query.filter_by(user_id=u.id).all()]
    req = requests.get(u.url, params={"hx": u.token, "pm": "ukoly"})
    root = ElementTree.fromstring(req.content.decode("utf-8"))[0]
    c = 0

    for ukol in root.findall("ukol"):
        hw_id = ukol.find("id").text
        if hw_id not in known:
            c += 1
            hw: Homework = parse_hw(ukol, hw_id)
            u.homeworks.append(hw)
            for attachment in find_attachments(ukol, u.url):
                hw.attachments.append(attachment)

    db.session.commit()  # changes are picked up automatically as we're adding to User
    return c


def first_import(undone_since, url, token, **user_kwargs):
    if a.config["PAUSE_REQUESTS"]:
        return None

    req = requests.get(url, params={"hx": token, "pm": "ukoly"})
    root = ElementTree.fromstring(req.content.decode("utf-8"))[0]

    # noinspection PyArgumentList
    u = User(url=url, token=token, **user_kwargs)
    db.session.add(u)
    for ukol in root.findall("ukol"):
        hw: Homework = parse_hw(ukol)
        if hw.assigned < undone_since:
            hw.is_done = True
        u.homeworks.append(hw)
        for attachment in find_attachments(ukol, u.url):
            hw.attachments.append(attachment)

    db.session.commit()
    return u.id


# TODO: Add a midnight task to shift all "postponed until [the next day]" homework to "TODO"
#  will probably use ATrigger scheduling
