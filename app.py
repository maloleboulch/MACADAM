from flask import Flask, g, render_template
from application import database

app = Flask(__name__)


@app.route('/')
def index():
    taxonomy_ranks = database.list_taxonomy_ranks()
    return render_template('index.html', taxonomy_ranks=taxonomy_ranks)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
