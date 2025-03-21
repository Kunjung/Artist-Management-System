from app import create_cursor, app, mysql

from helper import generate_hash_password

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
                            role ENUM('super_admin', 'artist_manager', 'artist') default 'artist',
                            created_at datetime default CURRENT_TIMESTAMP,
                            updated_at datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        )
                       ''')
        
        # load example rows for user table
        cursor.execute('''
                       INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, created_at, updated_at) 
                            values('Natsuki', 'Subaru', 'subaru@rezero.com', %s, '989979966899', '1995-12-25', 'm', 'Tokyo', now(), now())
                       ''', (generate_hash_password('subaru')))
        cursor.execute('''
                       INSERT INTO user (first_name, last_name, email, password, phone, dob, gender, address, created_at, updated_at) 
                            values('Mr.', 'admin', 'admin@artist.com', %s, '38375956190', '1997-09-30', 'm', 'The Grid', now(), now())
                       ''', (generate_hash_password('admin')))
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
                            values('Michael Jackson', '1980-09-12', 'm', 'USA', 2014, 43, now(), now())
                       ''')
        cursor.execute('''
                       INSERT INTO artist (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at) 
                            values('Taylor Swift', '1990-01-01', 'f', 'USA', 2016, 10, now(), now())
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
                            values(1, 'Billie jean', 'Michael', 'rock', now(), now())
                       ''')
        cursor.execute('''
                       INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at) 
                            values(1, 'Remember the time', 'Michael', 'country', now(), now())
                       ''')
        mysql.connection.commit()
        cursor.execute("SELECT * FROM music")
        music_values = cursor.fetchall()
        display_table_values('Music', list(music_values))