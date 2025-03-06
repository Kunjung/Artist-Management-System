from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import math

PAGINATION_SIZE = 10

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


@app.route('/')
def home():
    if "username" in session and "userrole" in session:
        # user is logged in. so redirect to dashboard
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        return render_template("dashboard.html", username= username, userrole=userrole)
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
            return render_template("manage_user.html", username= username, userrole=userrole, userlist=userlist, total_page=total_page, current_page=page)
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
                data = {
                    'email': email,
                    'password': password,
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
                cursor.execute(f"SELECT * from user where email='{email}'")
                user_info = cursor.fetchone()
                if user_info:
                    return "<h1>Email already present</h1>"
                else:
                    # validation completed, and email is new. so can create the new user in user table
                    cursor.execute(f'''
                            INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, role, created_at, updated_at) 
                                    values('{first_name}', '{last_name}', '{email}', '{password}', '{phone}', '{dob}', '{gender}', '{address}', '{role}', now(), now())
                            ''')
                    mysql.connection.commit()
                    return redirect(url_for('manage_user'))
            elif request.method == "GET":
                return render_template("add_user.html")
    return redirect(url_for('home'))

@app.route('/edit_user/<id>', methods=['GET', 'POST'])
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
                data = {
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'phone': phone,
                    'address': address,
                    'dob': dob,
                    'role': role
                }

                cursor = create_cursor()
                cursor.execute(f"SELECT * from user where id='{id}'")
                user_info = cursor.fetchone()
                if not user_info:
                    return "<h1>User ID is not present</h1>"
                else:
                    update_query = f'''
                            UPDATE user 
                            SET first_name='{first_name}', last_name='{last_name}', email='{email}', password='{password}', phone='{phone}', 
                            dob='{dob}', gender='{gender}', address='{address}', role='{role}', updated_at=now()
                            WHERE id={id};
                            '''
                    print("update_query: ")
                    print(update_query)
                    cursor.execute(update_query)
                    mysql.connection.commit()
                    return redirect(url_for('manage_user'))
            elif request.method == "GET":
                # get existing data of user and use that as placeholder value in the edit form
                cursor = create_cursor()
                # check if email is already present or not, if present redirect back to signup with error message: 'email already present'
                cursor.execute(f"SELECT * from user where id='{id}'")
                update_user_info = cursor.fetchone()
                if not update_user_info:
                    return "<h1>User ID is not present</h1>"
                else:
                    return render_template("edit_user.html", update_user_info=update_user_info)
    return redirect(url_for('home'))

@app.route('/delete_user/<id>')
def delete_user(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            cursor = create_cursor()
            cursor.execute(f"SELECT * from user where id='{id}'")
            user_info = cursor.fetchone()
            if not user_info:
                return "<h1>User ID is not present</h1>"
            else:
                delete_query = f"DELETE FROM user WHERE id={id}"
                print("delete_query: ")
                print(delete_query)
                cursor.execute(delete_query)
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
            return render_template("manage_artist.html", username= username, userrole=userrole, artistlist=artistlist, total_page=total_page, current_page=page)
        else:
            return "<h1>User doesn't have permission to view this page</h1>"
    else:
        # user is not logged in, so redirect to home
        return redirect(url_for('home'))

@app.route('/edit_artist/<id>')
def edit_artist(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            return f"Artist Id: {id}"
    return redirect(url_for('home'))

@app.route('/delete_artist/<id>')
def delete_artist(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            return f"Artist Id: {id}"
    return redirect(url_for('home'))

@app.route('/list_artist_songs/<artist_id>')
def list_artist_songs(artist_id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole in ("super_admin", "artist_manager"):
            page = request.args.get('page', 1)
            page = int(page)
            print("page: ", page)
            cursor = create_cursor()
            cursor.execute(f"SELECT * FROM artist WHERE id={artist_id}")
            artist_info = cursor.fetchone()
            if artist_info:
                offset = PAGINATION_SIZE * (page - 1)
                print("offset: ", offset)
                artist_name = artist_info['name']
                cursor.execute(f"SELECT * FROM music WHERE artist_id={artist_id} LIMIT {PAGINATION_SIZE} OFFSET {offset}")
                songlist = cursor.fetchall()
                cursor.execute(f"SELECT count(*) as count FROM music WHERE artist_id={artist_id}")
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
                    current_page=page
                )
            else:
                return f"Artist not found: {artist_id}"
    return redirect(url_for('home'))
    
@app.route('/edit_music/<id>')
def edit_music(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            return f"Music Id: {id}"
    return redirect(url_for('home'))

@app.route('/delete_music/<id>')
def delete_music(id):
    if "username" in session and "userrole" in session:
        username = session["username"]
        userrole = session["userrole"]
        if userrole == "super_admin":
            return f"Music Id: {id}"
    return redirect(url_for('home'))

@app.route('/login', methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    # check if username and password is present in database
    cursor = create_cursor()
    cursor.execute(f"SELECT * FROM user WHERE email ='{email}' LIMIT 1")
    user_info = cursor.fetchone()
    if user_info:
        # user is present
        # check if password matches
        db_password = user_info["password"]
        if password == db_password:
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
        return render_template("signup.html")
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
            'password': password,
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
        cursor.execute(f"SELECT * from user where email='{email}'")
        user_info = cursor.fetchone()
        if user_info:
            return "<h1>Email already present</h1>"
            return render_template("signup.html") # TODO: include error that email is already present
        else:
            # validation completed, and email is new. so can create the new user in user table
            cursor.execute(f'''
                       INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, role, created_at, updated_at) 
                            values('{first_name}', '{last_name}', '{email}', '{password}', '{phone}', '{dob}', '{gender}', '{address}', '{role}', now(), now())
                       ''')
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
