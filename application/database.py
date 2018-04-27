from typing import List
from flask import g
from application.model import Taxonomy
import sqlite3


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect('DatabaseTSV/PGM.db')
    return g.sqlite_db


def list_taxonomy_ranks() -> List[str]:
    results = get_db().execute('SELECT DISTINCT taxonomicRank FROM taxonomy ORDER BY parentTaxID DESC').fetchall()
    return [r[0] for r in results]


def find_cpds_pathways(cpds) -> List[str]:
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


def find_rxns_pathways(rxns) -> List[str]:
    pathways = []
    for rxn in rxns:
        results = get_db().execute('SELECT DISTINCT(pathwayName) FROM hierarchy '
                                   'INNER JOIN pathway ON hierarchy.pathwayFrameID = pathway.pathwayFrameID '
                                   'INNER JOIN PWYRXN ON pathway.pathwayFrameID = PWYRXN.PWY '
                                   'INNER JOIN RXNName ON PWYRXN.RXN = RXNName.RXN '
                                   'WHERE RXNName.Name LIKE ?;', ['%' + rxn.lower().strip() + '%']).fetchall()
        pathways.extend(results)
    return [r[0] for r in pathways]


def find_enzs_pathways(enzs) -> List[str]:
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


def find_taxonomies(names, ranks) -> List[Taxonomy]:
    if not names:
        return []

    name_criteria = "(name LIKE ?"
    for i in range(len(names) - 1):
        name_criteria += " OR name LIKE ?"
    name_criteria += ")"

    rank_criteria = ''
    if ranks:
        rank_criteria = " AND (taxonomicRank=?"
        for i in range(len(ranks) - 1):
            rank_criteria += " OR taxonomicRank=?"
        rank_criteria += ")"

    query = "SELECT * FROM taxonomy WHERE typeOfName='scientific name' AND " + name_criteria + rank_criteria + ';'
    results = get_db().execute(query, names + ranks).fetchall()
    return [Taxonomy(r[0], r[1], r[2], r[3], r[4], r[5]) for r in results]


def find_pathways_for_taxonomy(lineage_rank, min_score, max_score, funcs):
    if not funcs:
        return [], [], []

    options_criteria = "(hierarchy.pathwayName LIKE ?"
    for i in range(len(funcs) - 1):
        options_criteria += " OR hierarchy.pathwayName LIKE ?"
    options_criteria += ")"

    faprotax_criteria = "(pathwayName LIKE ?"
    for i in range(len(funcs) - 1):
        faprotax_criteria += " OR pathwayName LIKE ?"
    faprotax_criteria += ")"

    pathways_query = "TODO"
    faprotaxs_query = "TODO"

    match_point = []
    pathways = []
    faprotaxs = []
    stop = False

    while not stop:
        if lineage_rank.endswith("NaN."):
            lineage_rank = lineage_rank[:-4]
        elif lineage_rank == '2':
            print("Function doesn't exist or your score is too strict! Skip to next taxonomy")
            stop = True
        else:
            pathways = get_db().execute(pathways_query, funcs).fetchall()
            faprotaxs = get_db().execute(faprotaxs_query, funcs).fetchall()
            if pathways or faprotaxs:
                stop = True
            else:
                lineage_rank = ".".join(lineage_rank.split(".")[0:-1])
                lineage_rank = ".".join(lineage_rank.split(".")[0:-1])+"."

    return pathways, faprotaxs, match_point
