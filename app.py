from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

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
    if "username" in session:
        # user is logged in. so redirect to dashboard
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    username = session["username"]
    return render_template("dashboard.html", username= username)

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
            return redirect(url_for("dashboard"))
        else:
            return "<h1>Password Incorrect</h1>"
    else:
        # user is not present
        return "<h1>Email not present</h1>"

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop("username", None)
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
