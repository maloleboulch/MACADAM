from typing import Iterator
from flask import g
from application.model import Taxonomy
import sqlite3


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect('DatabaseTSV/PGM.db')
    return g.sqlite_db


def list_taxonomy_ranks() -> Iterator[str]:
    results = get_db().execute('SELECT DISTINCT taxonomicRank FROM taxonomy ORDER BY parentTaxID DESC').fetchall()
    return [r[0] for r in results]


def find_cpds_pathways(cpds) -> Iterator[str]:
    pathways = []
    for cpd in cpds:
        results = get_db().execute('SELECT DISTINCT(pathwayName) FROM hierarchy '
                                   'INNER JOIN pathway ON hierarchy.pathwayFrameID = pathway.pathwayFrameID '
                                   'INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY '
                                   'INNER JOIN RXNCPD ON PWYRXN.RXN = RXNCPD.RXN '
                                   'INNER JOIN CPDName ON RXNCPD.CPD = CPDName.CPD '
                                   'WHERE CPDName.Name LIKE ?;', ['%' + cpd.lower().strip() + '%']).fetchall()
        pathways.extend(results)
    return [r[0] for r in pathways]


def find_rxns_pathways(rxns) -> Iterator[str]:
    pathways = []
    for rxn in rxns:
        results = get_db().execute('SELECT DISTINCT(pathwayName) FROM hierarchy '
                                   'INNER JOIN pathway ON hierarchy.pathwayFrameID = pathway.pathwayFrameID '
                                   'INNER JOIN PWYRXN ON pathway.pathwayFrameID = PWYRXN.PWY '
                                   'INNER JOIN RXNName ON PWYRXN.RXN = RXNName.RXN '
                                   'WHERE RXNName.Name LIKE ?;', ['%' + rxn.lower().strip() + '%']).fetchall()
        pathways.extend(results)
    return [r[0] for r in pathways]


def find_enzs_pathways(enzs) -> Iterator[str]:
    pathways = []
    for ezn in enzs:
        results = get_db().execute('SELECT DISTINCT(pathwayName) FROM hierarchy '
                                   'INNER JOIN pathway ON hierarchy.pathwayFrameID = pathway.pathwayFrameID '
                                   'INNER JOIN PWYRXN ON pathway.pathwayFrameID = PWYRXN.PWY '
                                   'INNER JOIN RXNENZ ON PWYRXN.RXN = RXNENZ.RXN '
                                   'INNER JOIN ENZName ON RXNENZ.ENZ = ENZName.ENZ '
                                   'WHERE ENZName.Name LIKE ?;', ['%' + ezn.lower().strip() + '%']).fetchall()
        pathways.extend(results)
    return [r[0] for r in pathways]


def find_taxonomies(names, ranks) -> Iterator[Taxonomy]:
    if not names:
        return []

    name_query = "(name LIKE ?"
    for i in range(len(names) - 1):
        name_query += " OR name LIKE ?"
    name_query += ")"

    rank_query = ''
    if ranks:
        rank_query = " AND (taxonomicRank=?"
        for i in range(len(ranks) - 1):
            rank_query += " OR taxonomicRank=?"
        rank_query += ")"

    query = 'SELECT * FROM taxonomy WHERE ' + name_query + rank_query + ';'
    results = get_db().execute(query, names + ranks).fetchall()
    return [Taxonomy(r[0], r[1], r[2], r[3], r[4], r[5]) for r in results]
