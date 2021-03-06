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
    name_criteria = '(1=1)'
    if names:
        name_criteria = "(name LIKE ?"
        for i in range(len(names) - 1):
            name_criteria += " OR name LIKE ?"
        name_criteria += ")"

    rank_criteria = '(1=1)'
    if ranks:
        rank_criteria = "(taxonomicRank=?"
        for i in range(len(ranks) - 1):
            rank_criteria += " OR taxonomicRank=?"
        rank_criteria += ")"

    query = "SELECT * FROM taxonomy WHERE typeOfName='scientific name' AND " + name_criteria + " AND " +rank_criteria + ';'
    results = get_db().execute(query, names + ranks).fetchall()
    return [Taxonomy(r[0], r[1], r[2], r[3], r[4], r[5]) for r in results]


def find_pathways_for_taxonomy(lineage_rank, min_score, max_score, funcs):
    options_criteria = "(1=1)"
    if funcs:
        options_criteria = "(hierarchy.pathwayName LIKE ?"
        for i in range(len(funcs) - 1):
            options_criteria += " OR hierarchy.pathwayName LIKE ?"
        options_criteria += ")"

    faprotax_criteria = "(1=1)"
    if funcs:
        faprotax_criteria = "(pathwayName LIKE ?"
        for i in range(len(funcs) - 1):
            faprotax_criteria += " OR pathwayName LIKE ?"
        faprotax_criteria += ")"

    pathways_query = 'SELECT pathway.taxonomy, pathway.ID, pathway.strainName, pathway.numberOfPGDBInSpecies, pathway.numberOfPathway, pathway.pathwayScore, pathway.pathwayFrequencyScore, pathway.reasonToKeep, hierarchy.pathwayName FROM pathway '
    pathways_query += 'INNER JOIN hierarchy ON (pathway.pathwayFrameID = hierarchy.pathwayFrameID) '
    pathways_query += 'WHERE pathwayScore BETWEEN ? AND ? '
    pathways_query += 'AND taxonomy LIKE ? '
    pathways_query += 'AND ' + options_criteria + ';'

    faprotaxs_query = 'SELECT * FROM faprotax '
    faprotaxs_query += 'WHERE taxonomy LIKE ? '
    faprotaxs_query += 'AND ' + faprotax_criteria + ';'

    match_point = []
    pathways = []
    faprotaxs = []
    stop = False

    print(pathways_query)
    print(faprotaxs_query)

    while not stop:
        if lineage_rank.endswith("NaN."):
            lineage_rank = lineage_rank[:-4]
        elif lineage_rank == '2' or lineage_rank == '2.' or lineage_rank == '.':
            print("Function doesn't exist or your score is too strict! Skip to next taxonomy")
            stop = True
        else:
            pathways_args = [min_score, max_score, lineage_rank]
            pathways_args.extend(funcs)
            print(pathways_args)

            pathways = get_db().execute(pathways_query, pathways_args).fetchall()

            faprotaxs_args = [lineage_rank]
            faprotaxs_args.extend(funcs)
            print(faprotaxs_args)

            faprotaxs = get_db().execute(faprotaxs_query, faprotaxs_args).fetchall()

            if pathways or faprotaxs:
                stop = True
            else:
                lineage_rank = ".".join(lineage_rank.split(".")[0:-1])
                lineage_rank = ".".join(lineage_rank.split(".")[0:-1])+"."

    return pathways, faprotaxs, match_point
