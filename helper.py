import hashlib, re
from datetime import datetime

def generate_hash_password(password):
    h = hashlib.md5(password.encode())
    return h.hexdigest()

def verify_hash_password(password, db_hashed_password):
    h = hashlib.md5(password.encode())
    return h.hexdigest() == db_hashed_password

def is_field_more_than_max_length(field, max_length):
    if len(str(field)) > max_length:
        return True
    return False

def validate_user_data(user_data):
    # check if any empty value is passed or not
    for field in user_data.keys():
        field_data = user_data[field]
        if len(str(field_data)) == 0:
            return False, {field: f'{field} is empty'}
    
    if 'email' in user_data:
        # validate email
        email = user_data['email']
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$', email):
            return False, {'email': 'Email is invalid. Should be of the format test@email.com'}
    
    if 'first_name' in user_data:
        if is_field_more_than_max_length(user_data['first_name'], 255):
            return False, {'first_name': 'exceeds max length 255'}
    if 'last_name' in user_data:
        if is_field_more_than_max_length(user_data['last_name'], 255):
            return False, {'last_name': 'exceeds max length 255'}
    if 'email' in user_data:
        if is_field_more_than_max_length(user_data['email'], 255):
            return False, {'email': 'exceeds max length 255'}
    if 'phone' in user_data:
        if is_field_more_than_max_length(user_data['phone'], 20):
            return False, {'phone': 'exceeds max length 20'}
    if 'address' in user_data:
        if is_field_more_than_max_length(user_data['address'], 255):
            return False, {'address': 'exceeds max length 255'}
    if 'gender' in user_data:
        gender = user_data['gender']
        if gender not in ('m', 'f', 'o'):
            return False, {'gender': 'Allowed values m, f, o'}
    return True, {}

def validate_artist_data(artist_data):
    # check if any empty value is passed or not
    for field in artist_data.keys():
        field_data = artist_data[field]
        if len(str(field_data)) == 0:
            return False, {field: f'{field} is empty'}
    
    if 'first_release_year' in artist_data:
        first_release_year = str(artist_data['first_release_year'])
        if not re.match(r'^[0-9]+$', first_release_year):
            return False, {'first_release_year': 'Non-numeric characters present'}
    if 'no_of_albums_released' in artist_data:
        no_of_albums_released = str(artist_data['no_of_albums_released'])
        if not re.match(r'^[0-9]+$', no_of_albums_released):
            return False, {'no_of_albums_released': 'Non-numeric characters present'}
    if 'first_release_year' in artist_data:
        first_release_year = str(artist_data['first_release_year'])
        # check for 4 digit number starting with either 1 or 2
        if not re.match(r'[12]\d{3}', first_release_year):
            return False, {'first_release_year': 'Should be between 1000 and 2999'}
        current_year = datetime.now().year
        if int(first_release_year) > current_year:
            return False, {'first_release_year': f'Should not exceed current year {current_year}'}
    
    if 'name' in artist_data:
        if is_field_more_than_max_length(artist_data['name'], 255):
            return False, {'name': 'exceeds max length 255'}
    if 'address' in artist_data:
        if is_field_more_than_max_length(artist_data['address'], 255):
            return False, {'address': 'exceeds max length 255'}
    if 'gender' in artist_data:
        gender = artist_data['gender']
        if gender not in ('m', 'f', 'o'):
            return False, {'gender': 'Allowed values m, f, o'}
    return True, {}

def validate_music_data(music_data):
    # check if any empty value is passed or not
    for field in music_data.keys():
        field_data = music_data[field]
        if len(str(field_data)) == 0:
            return False, {field: f'{field} is empty'}
    if 'title' in music_data:
        if is_field_more_than_max_length(music_data['title'], 255):
            return False, {'title': 'exceeds max length 255'}
    if 'album_name' in music_data:
        if is_field_more_than_max_length(music_data['album_name'], 255):
            return False, {'album_name': 'exceeds max length 255'}
    if 'genre' in music_data:
        genre = music_data['genre']
        if genre not in ('rnb', 'country', 'classic', 'rock', 'jazz'):
            return False, {'genre': "Allowed values 'rnb', 'country', 'classic', 'rock', 'jazz'"}
    return True, {}
