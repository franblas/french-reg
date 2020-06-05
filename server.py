import sqlite3

from data import connect_db, get_regions
from flask import Flask, jsonify, g, request

app = Flask(__name__)

NB_ITEMS = 10

# g is a special object that is unique for each request.
# It is used to store data that might be accessed by multiple functions during
# the request. The connection is stored and reused instead of creating a new
# connection if get_db is called a second time in the same request.
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/regions/')
def regions_api():
    page = request.args.get('page', 0, type=int)
    data = get_regions(get_db(), NB_ITEMS, NB_ITEMS * page)
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
