from flask import Flask, render_template, request, url_for, flash, redirect, abort, jsonify
import sqlite3

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = 'Wheatley'


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    reviews = conn.execute('SELECT * FROM reviews').fetchall()
    conn.close()
    return render_template('index.html', reviews=reviews)


@app.route('/api/get', methods=['GET'])
def get_specific():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    query = "SELECT * FROM reviews WHERE"
    to_filter = []
    if 'ID' in request.args:
        try:
            int(request.args.get('ID'))
            query += ' ID=? AND'
            to_filter.append(request.args.get('ID'))
        except ValueError:
            return "ID parameter must be an Integer", 400
    if 'Country' in request.args:
        query += ' Country LIKE ? AND'
        to_filter.append("%{}%".format(request.args.get('Country')))
    if 'Brand' in request.args:
        query += ' Brand LIKE ? AND'
        to_filter.append("%{}%".format(request.args.get('Brand')))
    if 'Type' in request.args:
        query += ' Type LIKE ? AND'
        to_filter.append("%{}%".format(request.args.get('Type')))
    if 'Package' in request.args:
        query += ' Package LIKE ? AND'
        to_filter.append(request.args.get('Package'))
    if 'Minimum Rating' in request.args:
        try:
            float(request.args.get('Minimum Rating'))
            query += ' Rating>=? AND'
            to_filter.append(request.args.get('Minimum Rating'))
        except ValueError:
            return "Minimum Rating parameter must be an Float", 400
    if 'Maxmium Rating' in request.args:
        try:
            float(request.args.get('Maxmium Rating'))
            query += ' Rating<=? AND'
            to_filter.append(request.args.get('Maxmium Rating'))
        except ValueError:
            return "Maxmium Rating parameter must be an Float", 400
    if not 'ID' in request.args and 'Country' not in request.args and 'Brand' not in request.args and 'Type' not in request.args and 'Package' not in request.args and 'Minimum Rating' not in request.args and 'Maximum Rating' not in request.args:
        return "Error: No Parameters specified. Any paramters listed must be specified: ID, Country, Brand, Type, Packaging, Minimum Rating, Maximum Rating", 400
    query = query[:-4] + ';'
    reviews = conn.execute(query, to_filter).fetchall()
    return jsonify(reviews), 200


@app.route('/api/get/all', methods=['GET'])
def get_all():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    reviews = conn.execute('SELECT * FROM reviews;').fetchall()
    return jsonify(reviews), 200


@app.route('/api/add', methods=['POST'])
def add():
    request_data = request.get_json()
    acceptable_package_values = ['Cup', 'Pack',
                                 'Tray', 'Bowl', 'Box', 'Can', 'Bar']
    if not'Country'in request_data:
        return "Country parameter is needed!", 400
    elif not'Brand' in request_data:
        return "Brand parameter is needed!", 400
    elif not 'Type' in request_data:
        return "Type parameter is needed!", 400
    elif not 'Package' in request_data:
        return "Package parameter is needed!", 400
    elif not request_data['Package'] in acceptable_package_values:
        return "Package parameter is invaild!", 400
    elif not'Rating' in request_data:
        return "Rating parameter is needed!", 400
    else:
        try:
            Country = request_data['Country']
            Brand = request_data['Brand']
            Type = request_data['Type']
            Package = request_data['Package']
            Rating_String = request_data['Rating']
            Rating = float(Rating_String)
            conn = get_db_connection()
            conn.row_factory = dict_factory
            conn.execute("INSERT INTO reviews (Country, Brand, Type, Package, Rating) VALUES (?, ?, ?, ?, ?)",
                         (Country, Brand, Type, Package, Rating))
            conn.commit()
            conn.close()
            conn = get_db_connection()
            conn.row_factory = dict_factory
            review = conn.execute('SELECT * FROM reviews WHERE Country = ? AND Brand = ? AND Type = ? AND Package = ? AND Rating = ?',
                                  (Country, Brand, Type, Package, Rating)).fetchone()
            conn.close()
            return jsonify(review), 200
        except ValueError:
            return "Rating parameter must be an Float", 400


@app.route('/api/update', methods=['POST'])
def update():
    request_data = request.get_json()
    acceptable_package_values = ['Cup', 'Pack',
                                 'Tray', 'Bowl', 'Box', 'Can', 'Bar']
    if not'ID' in request_data:
        return "ID parameter is required!", 400
    try:
        ID = int(request_data['ID'])
        conn = get_db_connection()
        review = conn.execute("SELECT * from reviews WHERE ID = ?", (ID,)).fetchone()
        if review is None:
            return "Review does not exist!", 404
        else:
            query = "UPDATE reviews SET"
            to_filter = []
            if 'Country' in request_data:
                query += ' Country=?, '
                to_filter.append(request_data['Country'])
            if 'Brand' in request_data:
                query += ' Brand=?, '
                to_filter.append(request_data['Brand'])
            if 'Type' in request_data:
                query += ' Type=?, '
                to_filter.append(request_data['Type'])
            if 'Package' in request_data and request_data['Package'] in acceptable_package_values:
                query += ' Package=?, '
                to_filter.append(request_data['Package'])
            elif 'Package' in request_data and not request_data['Package'] in acceptable_package_values:
                return "Package parameter is invaild!", 400
            if 'Rating' in request_data:
                try:
                    float(request_data['Rating'])
                    query += ' Rating=?, '
                    to_filter.append(request_data['Rating'])
                except ValueError:
                    return "Rating parameter must be an Float", 400
            if not 'Country' in request_data and not'Brand' in request_data and not 'Type' in request_data and not 'Package' in request_data and not 'Rating' in request_data:
                return "Error: No Parameters to be updated specified. Any paramters listed must be specified: Country, Brand, Type, Packaging, Rating", 400
            to_filter.append(ID)
            query = query[:-2] + 'WHERE ID=?;'
            conn.execute(query, to_filter)
            conn.commit()
            conn.close()
            conn = get_db_connection()
            conn.row_factory = dict_factory
            review = conn.execute('SELECT * FROM reviews WHERE ID = ?',(ID,)).fetchone()
            conn.close()
            return jsonify(review), 200
    except ValueError:
        return "ID parameter must be an Integer", 400


@app.route('/api/remove', methods=['POST'])
def remove():
    request_data = request.get_json()
    ID_String = request_data['ID']
    conn = get_db_connection()
    query = "DELETE FROM reviews WHERE ID =?"
    if ID_String:
        try:
            ID = int(ID_String)
            review = conn.execute("SELECT * from reviews WHERE ID = ?", (ID,)).fetchone()
            if review is None:
                return "Review does not exist!", 404
            else:
                conn.execute(query, (ID,))
                conn.commit()
                conn.close()
                return "Review Deleted Successfully!", 200
        except ValueError:
            return "ID parameter must be an Integer", 400
    else:
        return "ID parameter must be provided", 400
