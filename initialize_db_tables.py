from app import create_cursor, app, mysql

def display_table_values(table_name, values):
    print(' ' * 100)
    print('Table Name: ' + table_name)
    print('-' * 100)
    for value in values:
        print(value)
    print('-' * 100)
    print(' ' * 100)

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
                            age integer
                        )
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
        user_values = cursor.fetchall()
        display_table_values('User', list(user_values))

        # Create artist table
        cursor.execute('DROP TABLE if exists music')
        cursor.execute('DROP TABLE if exists artist')
        cursor.execute('''
                       CREATE TABLE artist (
                            id integer primary key auto_increment, 
                            name varchar(255), 
                            dob datetime,
                            gender ENUM('m', 'f', 'o'),
                            address varchar(255),
                            first_release_year year,
                            no_of_albums_released integer,
                            created_at datetime default CURRENT_TIMESTAMP,
                            updated_at datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        )
                       ''')
        
        # load example rows for user table
        cursor.execute('''
                       INSERT INTO artist (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at) 
                            values('Hiroyuki Sawano', '1980-09-12', 'f', 'Tokyo', 2014, 43, now(), now())
                       ''')
        cursor.execute('''
                       INSERT INTO artist (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at) 
                            values('Artist MYTH & ROID', '1990-01-01', 'f', 'Tokyo', 2016, 10, now(), now())
                       ''')
        mysql.connection.commit()
        cursor.execute("SELECT * FROM artist")    
        artist_values = cursor.fetchall()
        display_table_values('Artist', list(artist_values))

        # Create music table
        cursor.execute('DROP TABLE if exists music')
        cursor.execute('''
                       CREATE TABLE music (
                            id integer primary key auto_increment, 
                            artist_id integer,
                            title varchar(255), 
                            album_name varchar(255),
                            genre ENUM('rnb', 'country', 'classic', 'rock', 'jazz'),
                            created_at datetime default CURRENT_TIMESTAMP,
                            updated_at datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            foreign key(artist_id) references artist(id) on delete cascade
                        )
                       ''')
        # load example rows for music table
        cursor.execute('''
                       INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at) 
                            values(1, 'Avid', 'eighty six', 'rock', now(), now())
                       ''')
        cursor.execute('''
                       INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at) 
                            values(2, 'Hydra', 'overlord', 'country', now(), now())
                       ''')
        mysql.connection.commit()
        cursor.execute("SELECT * FROM music")    
        music_values = cursor.fetchall()
        display_table_values('Music', list(music_values))