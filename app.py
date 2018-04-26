from flask import Flask, g, render_template, request
from application import database

app = Flask(__name__)


@app.route('/')
def index():
    taxonomy_ranks = database.list_taxonomy_ranks()
    return render_template('index.html', taxonomy_ranks=taxonomy_ranks)


@app.route('/search')
def search():
    funcs = request.args.getlist("func")
    cpds = request.args.getlist("cpd")
    rxns = request.args.getlist("rxn")
    enzs = request.args.getlist("enz")
    taxonomy_ranks = request.args.getlist("taxonomyRank")
    min_score = request.args.get("minScore")
    max_score = request.args.get("maxScore")

    return render_template('search.html', funcs=funcs, cpds=cpds, rxns=rxns, enzs=enzs, taxonomy_ranks=taxonomy_ranks,
                           min_score=min_score, max_score=max_score)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
