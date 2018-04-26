from flask import Flask, g, render_template, request
from application import database

app = Flask(__name__)


@app.route('/')
def index():
    taxonomy_ranks = database.list_taxonomy_ranks()
    return render_template('index.html', taxonomy_ranks=taxonomy_ranks)


@app.route('/search')
def search():
    func = request.args.get("func")
    cpd = request.args.get("cpd")
    rxn = request.args.get("rxn")
    enz = request.args.get("enz")
    taxonomy_rank = request.args.get("taxonomyRank")
    min_score = request.args.get("minScore")
    max_score = request.args.get("maxScore")

    print(str(request.args.to_dict()))

    return render_template('search.html', func=func, cpd=cpd, rxn=rxn, enz=enz, taxonomy_rank=taxonomy_rank,
                           min_score=min_score, max_score=max_score)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
