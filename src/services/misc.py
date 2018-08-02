import json

import requests
from numpy import unique
from random import choices
from services.db import DB


db = DB()


def read_users_from_alice(self, params):
    req = {
        "selector": {
            "$and": [
                {"profileType": "human"},
                {"isAlive": True}
            ]
        },
        "fields": ["_id", "firstName", "lastName"],
        "limit": 200,
    }
    r = requests.post("https://couchdb.alice.magellan2018.ru/models/_find", data=json.dumps(req),
                      headers={"Content-Type": "application/json"})
    users = json.loads(r.text)
    if 'docs' in users:
        ins_data = [
            {
                "id": user['_id'],
                "name": (user['firstName'] + " " + user['lastName']).strip(),
                "is_active": 1
            }
            for user in users['docs']
        ]
    db.query('update users set is_active=0')
    db.insert('users', ins_data, on_duplicate_key_update="is_active=1")
    return {"status": "ok", "affected": db.affected_rows()}


def modernize_date(date):
    return date.replace("2018", "2435")


def api_fail(msg):
    return {"status": "fail", "errors": msg}


def api_ok(**kwargs):
    res = {"status": "ok"}
    if kwargs:
        res.update(kwargs)
    return res


def gen_array_by_weight(array, cnt=1):
    sumvals = sum(array.values())
    generated =choices(list(array.keys()), k=cnt, weights=[i/sumvals for i in array.values()])
    ret = dict(zip(*unique(generated, return_counts=True)))
    return ret if cnt > 1 else list(ret.keys())[0]