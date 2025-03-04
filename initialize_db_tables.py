from app import create_cursor, app, mysql

if __name__ == '__main__':
    with app.app_context():
        cursor = create_cursor()

        # create user table
        cursor.execute('DROP TABLE if exists user')
        cursor.execute('''
                       CREATE TABLE user (
                            id integer primary key auto_increment, 
                            name varchar(255), 
                            last_name varchar(255),
                            email varchar(255),
                            password varchar(500),
                            phone varchar(20),
                            dob datetime,
                            gender ENUM('m', 'f', 'o'),
                            address varchar(255),
                            created_at datetime default CURRENT_TIMESTAMP,
                            updated_at datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            age integer)
                       ''')
        # cursor.execute("INSERT INTO test_table (name, age) values('gluttony', 25)")
        # cursor.execute("INSERT INTO test_table (name, age) values('greed', 26)")
        mysql.connection.commit()
        cursor.execute("SELECT * FROM user")    
        test_values = cursor.fetchall()
        # print(type(test_values))
        # print(test_values)
        print(list(test_values))