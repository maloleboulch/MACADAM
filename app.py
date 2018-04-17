from flask import Flask, g, render_template
from app.database import list_taxonomy_ranks

app = Flask(__name__)


@app.route('/')
def index():
    ranks = list_taxonomy_ranks()
    return render_template('index.html', ranks=ranks)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
