from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import math, csv, os, hashlib

PAGINATION_SIZE = 5
UPLOAD_FILE_PATH = os.path.join(os.getcwd(), 'static/file_uploads')

app = Flask(__name__)

app.secret_key = 'secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'artist_db'

mysql = MySQL(app)

# helper function to create cursor for mysql connection
def create_cursor():
    return mysql.connection.cursor(DictCursor)

def generate_hash_password(password):
    h = hashlib.md5(password.encode())
    return h.hexdigest()

def verify_hash_password(password, db_hashed_password):
    h = hashlib.md5(password.encode())
    return h.hexdigest() == db_hashed_password

@app.route('/')
def home():
    if "username" in session and "userrole" in session:
        # user is logged in. so redirect to dashboard
        return redirect(url_for("dashboard"))
    return render_template("index.html", is_user_logged_in=False)

@app.route('/dashboard')
def dashboard():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        return render_template("dashboard.html", username= username, userrole=userrole, is_user_logged_in=True)
    else:
        # user is not logged in, so redirect to home
        return redirect(url_for('home'))
    
@app.route('/manage_user')
def manage_user():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            # only user with super_admin role should have access to manage users
            page = request.args.get('page', 1)
            page = int(page)
            print("page: ", page)
            cursor = create_cursor()
            offset = PAGINATION_SIZE * (page - 1)
            cursor.execute(f"SELECT * FROM user LIMIT {PAGINATION_SIZE} OFFSET {offset}")
            userlist = cursor.fetchall()
            cursor.execute(f"SELECT count(*) as count FROM user")
            total_user_count = cursor.fetchone()['count']
            print("total_user_count: ", total_user_count)
            total_page = math.ceil(total_user_count / PAGINATION_SIZE)
            print("total_page: ", total_page)
            return render_template("manage_user.html", username= username, userrole=userrole, userlist=userlist, total_page=total_page, current_page=page, is_user_logged_in=True)
        else:
            return "<h1>User doesn't have permission to view this page</h1>"
    else:
        # user is not logged in, so redirect to home
        return redirect(url_for('home'))
    
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            if request.method == "POST":
                # add new user and redirect to manage_users dashboard
                email = request.form["email"]
                password = request.form["password"]
                first_name = request.form["first_name"]
                last_name = request.form["last_name"]
                gender = request.form["gender"]
                phone = request.form["phone"]
                address = request.form["address"]
                dob = request.form["dob"]
                role = request.form["role"]

                # TODO: validate form data is as expected
                user_data = {
                    'email': email,
                    'password': generate_hash_password(password),
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'phone': phone,
                    'address': address,
                    'dob': dob,
                    'role': role
                }

                # after validation is correct, create a new entry of the data in the user table
                cursor = create_cursor()
                # check if email is already present or not, if present redirect back to signup with error message: 'email already present'
                cursor.execute("SELECT * from user where email=%s", (email,))
                user_info = cursor.fetchone()
                if user_info:
                    return "<h1>Email already present</h1>"
                else:
                    # validation completed, and email is new. so can create the new user in user table
                    cursor.execute('''
                            INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, role, created_at, updated_at) 
                                    values(%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(phone)s, %(dob)s, %(gender)s, %(address)s, %(role)s, now(), now())
                            ''', user_data)
                    mysql.connection.commit()
                    return redirect(url_for('manage_user'))
            elif request.method == "GET":
                return render_template("add_user.html", is_user_logged_in=True, username=username, userrole=userrole)
    return redirect(url_for('home'))

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            if request.method == "POST":
                # update existing user and redirect to manage_users dashboard
                # first confirm that user exists in table or not
                email = request.form["email"]
                password = request.form["password"]
                first_name = request.form["first_name"]
                last_name = request.form["last_name"]
                gender = request.form["gender"]
                phone = request.form["phone"]
                address = request.form["address"]
                dob = request.form["dob"]
                role = request.form["role"]

                # TODO: validate form data is as expected
                user_data = {
                    'email': email,
                    'password': generate_hash_password(password),
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'phone': phone,
                    'address': address,
                    'dob': dob,
                    'role': role,
                    'id': id
                }

                cursor = create_cursor()
                cursor.execute("SELECT * from user where id=%s", (id,))
                user_info = cursor.fetchone()
                if not user_info:
                    return "<h1>User ID is not present</h1>"
                else:
                    update_query = '''
                            UPDATE user 
                            SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s, password=%(password)s, phone=%(phone)s, 
                            dob=%(dob)s, gender=%(gender)s, address=%(address)s, role=%(role)s, updated_at=now()
                            WHERE id=%(id)s;
                            '''
                    cursor.execute(update_query, user_data)
                    mysql.connection.commit()
                    return redirect(url_for('manage_user'))
            elif request.method == "GET":
                # get existing data of user and use that as placeholder value in the edit form
                cursor = create_cursor()
                # check if email is already present or not, if present redirect back to signup with error message: 'email already present'
                cursor.execute("SELECT * from user where id=%s", (id,))
                update_user_info = cursor.fetchone()
                if not update_user_info:
                    return "<h1>User ID is not present</h1>"
                else:
                    return render_template("edit_user.html", update_user_info=update_user_info, username=username, userrole=userrole, is_user_logged_in=True)
    return redirect(url_for('home'))

@app.route('/delete_user/<id>')
def delete_user(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            cursor = create_cursor()
            cursor.execute("SELECT * from user where id=%s", (id,))
            user_info = cursor.fetchone()
            if not user_info:
                return "<h1>User ID is not present</h1>"
            else:
                delete_query = "DELETE FROM user WHERE id=%s"
                print("delete_query: ")
                print(delete_query)
                cursor.execute(delete_query, (id,))
                mysql.connection.commit()
                return redirect(url_for('manage_user'))
    return redirect(url_for('home'))

@app.route('/manage_artist')
def manage_artist():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            # only user with super_admin or artist_manager role should have access to manage artist
            page = request.args.get('page', 1)
            page = int(page)
            print("page: ", page)
            cursor = create_cursor()
            offset = PAGINATION_SIZE * (page - 1)
            cursor.execute(f"SELECT * FROM artist LIMIT {PAGINATION_SIZE} OFFSET {offset}")
            artistlist = cursor.fetchall()
            cursor.execute(f"SELECT count(*) as count FROM artist")
            total_artist_count = cursor.fetchone()['count']
            print("total_artist_count: ", total_artist_count)
            total_page = math.ceil(total_artist_count / PAGINATION_SIZE)
            print("total_page: ", total_page)
            return render_template("manage_artist.html", username= username, userrole=userrole, artistlist=artistlist, total_page=total_page, current_page=page, is_user_logged_in=True)
        else:
            return "<h1>User doesn't have permission to view this page</h1>"
    else:
        # user is not logged in, so redirect to home
        return redirect(url_for('home'))

@app.route('/add_artist', methods=['GET', 'POST'])
def add_artist():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            if request.method == "POST":
                # add new user and redirect to manage_users dashboard
                name = request.form["name"]
                dob = request.form["dob"]
                gender = request.form["gender"]
                address = request.form["address"]
                first_release_year = request.form["first_release_year"]
                no_of_albums_released = request.form["no_of_albums_released"]

                # TODO: validate form data is as expected
                artist_data = {
                    'name': name,
                    'dob': dob,
                    'gender': gender,
                    'address': address,
                    'first_release_year': first_release_year,
                    'no_of_albums_released': no_of_albums_released
                }

                # after validation is correct, create a new entry of the data in the user table
                cursor = create_cursor()
                # validation completed, and email is new. so can create the new user in user table
                cursor.execute('''
                        INSERT INTO artist (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at) 
                            values(%(name)s, %(dob)s, %(gender)s, %(address)s, %(first_release_year)s, %(no_of_albums_released)s, now(), now())
                        ''', artist_data)
                mysql.connection.commit()
                return redirect(url_for('manage_artist'))
            elif request.method == "GET":
                return render_template("add_artist.html", username=username, userrole=userrole, is_user_logged_in=True)
    return redirect(url_for('home'))

@app.route('/edit_artist/<int:id>', methods=['GET', 'POST'])
def edit_artist(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            if request.method == "POST":
                name = request.form["name"]
                dob = request.form["dob"]
                gender = request.form["gender"]
                address = request.form["address"]
                first_release_year = request.form["first_release_year"]
                no_of_albums_released = request.form["no_of_albums_released"]

                # TODO: validate form data is as expected
                artist_data = {
                    'name': name,
                    'dob': dob,
                    'gender': gender,
                    'address': address,
                    'first_release_year': first_release_year,
                    'no_of_albums_released': no_of_albums_released,
                    'id': id
                }

                cursor = create_cursor()
                cursor.execute("SELECT * from artist where id=%s", (id,))
                user_info = cursor.fetchone()
                if not user_info:
                    return "<h1>Artist ID is not present</h1>"
                else:
                    update_query = '''
                            UPDATE artist 
                            SET name=%(name)s, first_release_year=%(first_release_year)s, no_of_albums_released=%(no_of_albums_released)s, 
                            dob=%(dob)s, gender=%(gender)s, address=%(address)s, updated_at=now()
                            WHERE id=%(id)s;
                            '''
                    cursor.execute(update_query, artist_data)
                    mysql.connection.commit()
                    return redirect(url_for('manage_artist'))
            elif request.method == "GET":
                # get existing data of user and use that as placeholder value in the edit form
                cursor = create_cursor()
                # check if email is already present or not, if present redirect back to signup with error message: 'email already present'
                cursor.execute("SELECT * from artist where id=%s", (id,))
                artist_info = cursor.fetchone()
                if not artist_info:
                    return "<h1>Artist ID is not present</h1>"
                else:
                    return render_template("edit_artist.html", artist_info=artist_info, username=username, userrole=userrole, is_user_logged_in=True)
    return redirect(url_for('home'))

@app.route('/delete_artist/<int:id>')
def delete_artist(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            cursor = create_cursor()
            cursor.execute("SELECT * from artist where id=%s", (id,))
            artist_info = cursor.fetchone()
            if not artist_info:
                return "<h1>Artist ID is not present</h1>"
            else:
                delete_query = "DELETE FROM artist WHERE id=%s"
                print("delete_query: ")
                print(delete_query)
                cursor.execute(delete_query, (id,))
                mysql.connection.commit()
                return redirect(url_for('manage_artist'))
    return redirect(url_for('home'))

@app.route('/import_artist', methods=['GET', 'POST'])
def import_artist():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            if request.method == 'GET':
                # display CSV upload page
                return render_template("import_artist.html", username=username, userrole=userrole, is_user_logged_in=True)
            elif request.method == 'POST':
                # use the file and populate artist table with insert queries
                print("request.files: ", request.files)
                if 'artist_file' not in request.files:
                    return '<h1>File not uploaded</h1>'
                uploaded_file = request.files['artist_file']
                file_path = os.path.join(UPLOAD_FILE_PATH, uploaded_file.filename)
                uploaded_file.save(file_path)
                with open(file_path) as file:
                    csv_file = csv.reader(file)
                    print("csv imported data:")
                    print("***" * 30)
                    header = next(csv_file)
                    print("header: ")
                    print(header)
                    cursor = create_cursor()
                    # TODO: verify that the required headers are present in the file
                    # e.g. header must include name, dob, gender, address, first_release_year, no_of_albums_released
                    # header can optionally exclude id, created_at, updated_at
                    # TODO: also verify that the data is valid before inserting to table
                    for row in csv_file:
                        print(row)
                        id, name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at = \
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                        params = {
                            'name': name,
                            'dob': dob,
                            'gender': gender,
                            'address': address,
                            'first_release_year': first_release_year,
                            'no_of_albums_released': no_of_albums_released
                        }
                        cursor.execute('''
                                    INSERT INTO artist (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at) 
                                            values(%(name)s, %(dob)s, %(gender)s, %(address)s, %(first_release_year)s, %(no_of_albums_released)s, now(), now())
                                    ''', params)
                        mysql.connection.commit()
                return redirect(url_for('manage_artist'))
            

    return redirect(url_for('home'))

@app.route('/export_artist')
def export_artist():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            cursor = create_cursor()
            cursor.execute('SELECT * FROM artist')
            artists = cursor.fetchall()
            if artists:
                artist_keys = artists[0].keys()
                print("artist_keys: ", artist_keys)
                with open("artists.csv", "w", newline="") as output_file:
                    dict_writer = csv.DictWriter(output_file, artist_keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(artists)
                return send_file("artists.csv", as_attachment=True, download_name="artists.csv")

    return redirect(url_for('home'))

@app.route('/list_artist_songs/<int:artist_id>')
def list_artist_songs(artist_id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            page = request.args.get('page', 1)
            page = int(page)
            print("page: ", page)
            cursor = create_cursor()
            cursor.execute("SELECT * FROM artist WHERE id=%s", (artist_id,))
            artist_info = cursor.fetchone()
            if artist_info:
                offset = PAGINATION_SIZE * (page - 1)
                print("offset: ", offset)
                artist_name = artist_info['name']
                cursor.execute("SELECT * FROM music WHERE artist_id=%s LIMIT %s OFFSET %s",
                               (artist_id, PAGINATION_SIZE, offset))
                songlist = cursor.fetchall()
                cursor.execute("SELECT count(*) as count FROM music WHERE artist_id=%s", (artist_id,))
                total_music_count = cursor.fetchone()['count']
                print("total_music_count: ", total_music_count)
                total_page = math.ceil(total_music_count / PAGINATION_SIZE)
                print("total_page: ", total_page)
                return render_template(
                    "list_artist_songs.html", 
                    username=username,
                    userrole=userrole,
                    artist_id=artist_id, 
                    artist_name=artist_name, 
                    songlist=songlist, 
                    total_page=total_page, 
                    current_page=page,
                    is_user_logged_in=True
                )
            else:
                return f"Artist not found: {artist_id}"
    return redirect(url_for('home'))

@app.route('/add_music/<int:artist_id>', methods=['GET', 'POST'])
def add_music(artist_id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager", "artist"):
            if request.method == "POST":
                # add new user and redirect to manage_users dashboard
                title = request.form["title"]
                album_name = request.form["album_name"]
                genre = request.form["genre"]
                
                music_data = {
                    'artist_id': artist_id,
                    'title': title,
                    'album_name': album_name,
                    'genre': genre
                }

                # after validation is correct, create a new entry of the data in the user table
                cursor = create_cursor()
                # validation completed, and email is new. so can create the new user in user table
                cursor.execute('''
                        INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at) 
                            values(%(artist_id)s, %(title)s, %(album_name)s, %(genre)s, now(), now())
                        ''', music_data)
                mysql.connection.commit()
                return redirect(url_for('list_artist_songs', artist_id=artist_id))
            elif request.method == "GET":
                cursor = create_cursor()
                cursor.execute("SELECT * FROM artist where id=%s LIMIT 1", (artist_id,))
                artist_info = cursor.fetchone()
                artist_name = artist_info['name']
                return render_template("add_music.html", username=username, userrole=userrole, artist_id=artist_id, artist_name=artist_name, is_user_logged_in=True)
    return redirect(url_for('home'))

@app.route('/edit_music/<int:id>', methods=['GET', 'POST'])
def edit_music(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager", "artist"):
            if request.method == "POST":
                cursor = create_cursor()
                cursor.execute("SELECT artist_id from music where id=%s", (id,))
                artist_id = cursor.fetchone()['artist_id']
                title = request.form["title"]
                album_name = request.form["album_name"]
                genre = request.form["genre"]
                
                music_data = {
                    'artist_id': artist_id,
                    'title': title,
                    'album_name': album_name,
                    'genre': genre
                }

                cursor = create_cursor()
                cursor.execute("SELECT * from music where id=%s", (id,))
                music_info = cursor.fetchone()
                if not music_info:
                    return "<h1>Music ID is not present</h1>"
                else:
                    parameters = {
                        'title': title,
                        'album_name': album_name,
                        'genre': genre,
                        'id': id
                    }
                    parameterized_update_query = '''
                            UPDATE music 
                            SET title=%(title)s, album_name=%(album_name)s,
                            genre=%(genre)s, updated_at=now()
                            WHERE id=%(id)s;
                            '''
                    cursor.execute(parameterized_update_query, parameters)
                    mysql.connection.commit()
                    return redirect(url_for('list_artist_songs', artist_id=artist_id))
            elif request.method == "GET":
                cursor = create_cursor()
                cursor.execute("SELECT * from music where id=%s", (id,))
                music_info = cursor.fetchone()
                if not music_info:
                    return "<h1>Music ID is not present</h1>"
                else:
                    return render_template("edit_music.html", music_info=music_info, username=username, userrole=userrole, is_user_logged_in=True)
    return redirect(url_for('home'))

@app.route('/delete_music/<id>')
def delete_music(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager", "artist"):
            cursor = create_cursor()
            cursor.execute("SELECT * from music where id=%s", (id,))
            music_info = cursor.fetchone()
            if not music_info:
                return "<h1>Music ID is not present</h1>"
            else:
                delete_query = "DELETE FROM music WHERE id=%s"
                cursor.execute(delete_query, (id,))
                mysql.connection.commit()
                return redirect(url_for('list_artist_songs',artist_id=music_info['artist_id']))
    return redirect(url_for('home'))

@app.route('/login', methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    # check if username and password is present in database
    cursor = create_cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s LIMIT 1", (email,))
    user_info = cursor.fetchone()
    if user_info:
        # user is present
        # check if password matches
        db_password = user_info["password"]
        if verify_hash_password(password, db_password) == True:
            # return "<h1>Password Matched</h1>"
            session["username"] = user_info["first_name"] + " " + user_info["last_name"]
            session["userrole"] = user_info["role"]
            return redirect(url_for("dashboard"))
        else:
            return "<h1>Password Incorrect</h1>"
    else:
        # user is not present
        return "<h1>Email not present</h1>"

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html", is_user_logged_in=False)
    else:
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        dob = request.form["dob"]
        role = request.form["role"]

        # TODO: validate form data is as expected
        data = {
            'email': email,
            'password': generate_hash_password(password),
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'phone': phone,
            'address': address,
            'dob': dob,
            'role': role
        }

        # after validation is correct, create a new entry of the data in the user table
        cursor = create_cursor()
        # check if email is already present or not, if present redirect back to signup with error message: 'email already present'
        cursor.execute("SELECT * FROM user WHERE email = %s LIMIT 1", (email,))
        user_info = cursor.fetchone()
        if user_info:
            return "<h1>Email already present</h1>"
            return render_template("signup.html") # TODO: include error that email is already present
        else:
            # validation completed, and email is new. so can create the new user in user table
            # cursor.execute(f'''
            #            INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, role, created_at, updated_at) 
            #                 values('{first_name}', '{last_name}', '{email}', '{password}', '{phone}', '{dob}', '{gender}', '{address}', '{role}', now(), now())
            #            ''')
            cursor.execute('''
                       INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, role, created_at, updated_at) 
                            values(%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(phone)s, %(dob)s, %(gender)s, %(address)s, %(role)s, now(), now())
                       ''', data)
            mysql.connection.commit()
            return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop("username", None)
    session.pop("userrole", None)
    return redirect(url_for("home"))

@app.route('/test_db_connection')
def test_db_connection():
    cursor = create_cursor()
    cursor.execute('DROP TABLE if exists test_table')
    cursor.execute('CREATE TABLE test_table (id integer primary key auto_increment, name varchar(255), age integer)')
    cursor.execute("INSERT INTO test_table (name, age) values('rem', 25)")
    cursor.execute("INSERT INTO test_table (name, age) values('subaru', 26)")
    mysql.connection.commit()
    cursor.execute("SELECT * FROM test_table")    
    test_values = cursor.fetchall()
    # print(type(test_values))
    # print(test_values)
    return list(test_values)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
