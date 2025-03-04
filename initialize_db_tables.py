from app import create_cursor, app, mysql

if __name__ == '__main__':
    with app.app_context():
        cursor = create_cursor()

        # Create user table
        cursor.execute('DROP TABLE if exists user')
        cursor.execute('''
                       CREATE TABLE user (
                            id integer primary key auto_increment, 
                            first_name varchar(255), 
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
        
        # load example rows for user table
        cursor.execute('''
                       INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, created_at, updated_at, age) 
                            values('Natsuki', 'Subaru', 'subaru@rezero.com', 'subarupassword', '989979966899', '1995-12-26', 'm', 'Tokyo', now(), now(), 29)
                       ''')
        cursor.execute('''
                       INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, created_at, updated_at, age) 
                            values('Emilia', 'Tan', 'emilia@rezero.com', 'emiliapassword', '38375956190', '1997-09-30', 'f', 'Elior Forest', now(), now(), 27)
                       ''')
        mysql.connection.commit()
        cursor.execute("SELECT * FROM user")    
        test_values = cursor.fetchall()
        # print(type(test_values))
        # print(test_values)
        print(list(test_values))

        # cursor.execute("TRUNCATE TABLE user")