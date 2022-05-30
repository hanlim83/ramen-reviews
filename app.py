from flask import Flask, render_template, request, url_for, flash, redirect, abort, jsonify
import sqlite3
import sys

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = 'Wheatley'
app.config['JSON_SORT_KEYS'] = False

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.row_factory = dict_factory
        query = "SELECT * FROM reviews WHERE"
        to_filter = []
        if not request.form.get('Country') is None:
            query += ' Country LIKE ? AND'
            to_filter.append("%{}%".format(request.form.get('Country')))
        if not request.form.get('Brand') is None:
            query += ' Brand LIKE ? AND'
            to_filter.append("%{}%".format(request.form.get('Brand')))
        if not request.form.get('Type') is None:
            query += ' Type LIKE ? AND'
            to_filter.append("%{}%".format(request.form.get('Type')))
        if not request.form.get('Package') is None:
            query += ' Package LIKE ? AND'
            to_filter.append(request.form.get('Package'))
        if not request.form.get('Minimum Rating') is None and request.form.get('Minimum Rating') != "":
            try:
                float(request.form.get('Minimum Rating'))
                query += ' Rating>=? AND'
                to_filter.append(float(request.form.get('Minimum Rating')))
            except ValueError:
                return "Minimum Rating parameter must be an Float", 400
        if not request.form.get('Maxmium Rating') is None and request.form.get('Maxmium Rating') != "":
            try:
                float(request.form.get('Maxmium Rating'))
                query += ' Rating<=? AND'
                to_filter.append(float(request.form.get('Maxmium Rating')))
            except ValueError:
                return "Maxmium Rating parameter must be an Float", 400
        if not request.form.get('Country') is None and not request.form.get('Brand') is None and not request.form.get('Type') is None and not request.form.get('Package') is None and not request.form.get('Minimum Rating') is None and not request.form.get('Maxmium Rating') is None:
            reviews = conn.execute('SELECT * FROM reviews;').fetchall()
            countries = conn.execute('SELECT DISTINCT Country FROM reviews').fetchall()
            brands = conn.execute('SELECT DISTINCT Brand FROM reviews').fetchall()
            packages = conn.execute('SELECT DISTINCT Package FROM reviews').fetchall()
            conn.close()
            return render_template('index.html', reviews = reviews, countries = countries, brands = brands, packages = packages)
        
        query = query[:-4] + ';'
        reviews = conn.execute(query, to_filter).fetchall()
        countries = conn.execute('SELECT DISTINCT Country FROM reviews').fetchall()
        brands = conn.execute('SELECT DISTINCT Brand FROM reviews').fetchall()
        packages = conn.execute('SELECT DISTINCT Package FROM reviews').fetchall()
        conn.close()
        return render_template('index.html', reviews = reviews, countries = countries, brands = brands, packages = packages)
    else:
        conn = get_db_connection()
        reviews = conn.execute('SELECT * FROM reviews').fetchall()
        countries = conn.execute('SELECT DISTINCT Country FROM reviews').fetchall()
        brands = conn.execute('SELECT DISTINCT Brand FROM reviews').fetchall()
        packages = conn.execute('SELECT DISTINCT Package FROM reviews').fetchall()
        conn.close()
        return render_template('index.html', reviews = reviews, countries = countries, brands = brands, packages = packages)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        acceptable_package_values = ['Cup', 'Pack',
                                    'Tray', 'Bowl', 'Box', 'Can', 'Bar']
        if request.form.get('Country') is None:
            return "Country parameter is needed!", 400
        elif request.form.get('Brand') is None:
            return "Brand parameter is needed!", 400
        elif request.form.get('Type') is None:
            return "Type parameter is needed!", 400
        elif request.form.get('Package') is None:
            return "Package parameter is needed!", 400
        elif not request.form.get('Package') in acceptable_package_values:
            return "Package parameter is invaild!", 400
        elif request.form.get('Rating') is None:
            return "Rating parameter is needed!", 400
        else:
            try:
                Country = request.form.get('Country')
                Brand = request.form.get('Brand')
                Type = request.form.get('Type')
                Package = request.form.get('Package')
                Rating_String = request.form.get('Rating')
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
                countries = conn.execute('SELECT DISTINCT Country FROM reviews').fetchall()
                brands = conn.execute('SELECT DISTINCT Brand FROM reviews').fetchall()
                packages = conn.execute('SELECT DISTINCT Package FROM reviews').fetchall()
                conn.close()
                return redirect(url_for('index'))
            except ValueError:
                return "Rating parameter must be an Float", 400
    else:
        conn = get_db_connection()
        countries = conn.execute('SELECT DISTINCT Country FROM reviews').fetchall()
        brands = conn.execute('SELECT DISTINCT Brand FROM reviews').fetchall()
        packages = conn.execute('SELECT DISTINCT Package FROM reviews').fetchall()
        conn.close()
        return render_template('create.html', countries = countries, brands = brands, packages = packages)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        acceptable_package_values = ['Cup', 'Pack',
                                    'Tray', 'Bowl', 'Box', 'Can', 'Bar']
        if not request.form.get('ID'):
            return "ID parameter is required!", 400
        try:
            ID = int(request.form.get('ID'))
            conn = get_db_connection()
            review = conn.execute("SELECT * from reviews WHERE ID = ?", (ID,)).fetchone()
            if review is None:
                return "Review does not exist!", 404
            else:
                query = "UPDATE reviews SET"
                to_filter = []
                query += ' Country=?, '
                to_filter.append(request.form.get('Country'))
                query += ' Brand=?, '
                to_filter.append(request.form.get('Brand'))
                query += ' Type=?, '
                to_filter.append(request.form.get('Type'))
                if request.form.get('Package') and request.form.get('Package') in acceptable_package_values:
                    query += ' Package=?, '
                    to_filter.append(request.form.get('Package'))
                elif request.form.get('Package') and not request.form.get('Package') in acceptable_package_values:
                    return "Package parameter is invaild!", 400
                try:
                    float(request.form.get('Rating'))
                    query += ' Rating=?, '
                    to_filter.append(float(request.form.get('Rating')))
                except ValueError:
                    return "Rating parameter must be an Float", 400
                to_filter.append(ID)
                query = query[:-2] + ' WHERE ID=?;'
                conn.execute(query, to_filter)
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
        except ValueError:
            return "ID parameter must be an Integer", 400
    else:
        if not request.args.get('ID'):
            return "ID parameter is required!", 400
        try:
            ID = int(request.args.get('ID'))
            conn = get_db_connection()
            review = conn.execute("SELECT * from reviews WHERE ID = ?", (ID,)).fetchone()
            countries = conn.execute('SELECT DISTINCT Country FROM reviews').fetchall()
            packages = conn.execute('SELECT DISTINCT Package FROM reviews').fetchall()
            conn.close()
            return render_template('edit.html', review = review, countries = countries, packages = packages)
        except ValueError:
            return "ID parameter must be an Integer", 400

@app.route('/delete', methods=['GET'])
def delete():
    ID_String = request.args.get('ID')
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
                return redirect(url_for('index'))
        except ValueError:
            return "ID parameter must be an Integer", 400
    else:
        return "ID parameter must be provided", 400

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
            to_filter.append(float(request.args.get('Minimum Rating')))
        except ValueError:
            return "Minimum Rating parameter must be an Float", 400
    if 'Maxmium Rating' in request.args:
        try:
            float(request.args.get('Maxmium Rating'))
            query += ' Rating<=? AND'
            to_filter.append(float(request.args.get('Maxmium Rating')))
        except ValueError:
            return "Maxmium Rating parameter must be an Float", 400
    if not 'ID' in request.args and 'Country' not in request.args and 'Brand' not in request.args and 'Type' not in request.args and 'Package' not in request.args and 'Minimum Rating' not in request.args and 'Maximum Rating' not in request.args:
        return "Error: No Parameters specified. Any one of paramters listed must be specified: ID, Country, Brand, Type, Packaging, Minimum Rating, Maximum Rating", 400
    query = query[:-4] + ';'
    reviews = conn.execute(query, to_filter).fetchall()
    return jsonify(reviews), 200


@app.route('/api/get/all', methods=['GET'])
def get_all():
    acceptable_sort_by_values = ['Country', 'Brand', 'Type', 'Package', 'Rating']
    acceptable_sort_type_values = ['Ascending', 'Decending']
    conn = get_db_connection()
    conn.row_factory = dict_factory
    query = "SELECT * FROM reviews"
    sort_filter = []
    if 'SortBy' in request.args and request.args.get("SortBy") in acceptable_sort_by_values:
        query += ' ORDER BY ?'
        sort_filter.append(request.args.get('SortBy'))
    if 'SortType' in request.args and request.args.get("SortType") in acceptable_sort_type_values:
        if request.args.get("SortType")  == 'Ascending':
            query += ' ASC'
        elif request.args.get("SortType")  == 'Decending':
            query += ' DESC'
    if 'SortBy' in request.args and not request.args.get("SortBy") in acceptable_sort_by_values:
        return "Invaild SortBy Parameter. SortBy Parameter must be one of the following: Country, Brand, Type, Package, Rating"
    if 'SortType' in request.args and not request.args.get("SortType") in acceptable_sort_type_values:
        return "Invaild SortType Paramter. Sorting Paramter must be one of the following: Ascending, Decending"
    query = query + ';'
    print(sort_filter)
    reviews = conn.execute(query, sort_filter).fetchall()
    return jsonify(reviews), 200

@app.route('/api/get/average_rating', methods=['GET'])
def get_average_rating():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    query = "SELECT Country, Brand, Type, Package, AVG(Rating) as Average_Rating FROM reviews WHERE"
    to_filter = []
    if 'Country' in request.args:
        query += ' Country = ? AND'
        to_filter.append(request.args.get('Country'))
    if 'Brand' in request.args:
        query += ' Brand = ? AND'
        to_filter.append(request.args.get('Brand'))
    if 'Type' in request.args:
        query += ' Type = ? AND'
        to_filter.append(request.args.get('Type'))
    if 'Package' in request.args:
        query += ' Package = ? AND'
        to_filter.append(request.args.get('Package'))
    if 'Country' not in request.args or 'Brand' not in request.args or 'Type' not in request.args or 'Package' not in request.args:
        return "Error: One or more Parameters are not specified. All paramters listed must be specified: Country, Brand, Type, Packaging", 400
    query = query[:-4] + ';'
    reviews = conn.execute(query, to_filter).fetchall()
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
                    to_filter.append(float(request_data['Rating']))
                except ValueError:
                    return "Rating parameter must be an Float", 400
            if not 'Country' in request_data and not'Brand' in request_data and not 'Type' in request_data and not 'Package' in request_data and not 'Rating' in request_data:
                return "Error: No Parameters to be updated specified. Any paramters listed must be specified: Country, Brand, Type, Packaging, Rating", 400
            to_filter.append(ID)
            query = query[:-2] + ' WHERE ID=?;'
            conn.execute(query, to_filter)
            conn.commit()
            conn.close()
            return "Review Updated Successfully!", 200
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
