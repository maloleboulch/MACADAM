from typing import Iterator
from flask import g
import sqlite3


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect('DatabaseTSV/PGM.db')
    return g.sqlite_db


def list_taxonomy_ranks() -> Iterator[str]:
    results = get_db().execute('SELECT DISTINCT taxonomicRank FROM taxonomy ORDER BY parentTaxID DESC').fetchall()
    return map(lambda t: t[0], results)

