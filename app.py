from flask import Flask, g, render_template, request
from application import database, utils

app = Flask(__name__)


@app.route('/')
def index():
    taxonomy_ranks = database.list_taxonomy_ranks()
    return render_template('index.html', taxonomy_ranks=taxonomy_ranks)


@app.route('/search')
def search():
    taxs = request.args.getlist("tax")
    funcs = request.args.getlist("func")
    cpds = request.args.getlist("cpd")
    rxns = request.args.getlist("rxn")
    enzs = request.args.getlist("enz")
    taxonomy_ranks = request.args.getlist("taxonomyRank")
    min_score = request.args.get("minScore")
    max_score = request.args.get("maxScore")

    cpds_pathways = database.find_cpds_pathways(cpds)
    rxns_pathways = database.find_rxns_pathways(rxns)
    enzs_pathways = database.find_enzs_pathways(enzs)

    all_funcs = funcs + cpds_pathways + rxns_pathways + enzs_pathways
    taxonomies = database.find_taxonomies(taxs, taxonomy_ranks)

    lineages = set([taxonomy.taxonomy for taxonomy in taxonomies])
    lineages_by_taxonomy_id = utils.lineages_by_taxonomy_id(taxonomies)

    pathway_by_lineage = {}
    faprotax_by_lineage = {}
    matching_point_by_lineage = {}
    for lineage in lineages:
        res = database.find_pathways_for_taxonomy(lineage, min_score, max_score, all_funcs)
        pathway_by_lineage[lineage] = res[0] or ["None"]
        faprotax_by_lineage[lineage] = res[1] or ["None"]
        matching_point_by_lineage[lineage] = res[2] or ["None"]

    return render_template('search.html', taxs=taxs, funcs=funcs, cpds=cpds, rxns=rxns, enzs=enzs, taxonomy_ranks=taxonomy_ranks, min_score=min_score, max_score=max_score,
                           all_funcs=all_funcs, lineages=lineages, taxonomies=taxonomies, pathway_by_lineage=pathway_by_lineage, faprotax_by_lineage=faprotax_by_lineage,
                           matching_point_by_lineage=matching_point_by_lineage)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
