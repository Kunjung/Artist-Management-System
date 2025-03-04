from flask import Flask
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'artist_db'

mysql = MySQL(app)

# helper function to create cursor for mysql connection
def create_cursor():
    return mysql.connection.cursor(DictCursor)


@app.route('/')
def hello():
    return '<h1>Hello</h1>'

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
