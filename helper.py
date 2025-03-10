import hashlib, re, os, csv
from datetime import datetime
from config import MAX_FILE_SIZE_IN_KB

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
        
    if 'unhashed_password' in user_data:
        if len(user_data['unhashed_password']) < 5:
            return False, {'password': 'Password must be at least 5 characters long'}
    
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

def validate_csv_file_data(file_path):
    file_size_in_kb = round(os.stat(file_path).st_size / 1024, 2)
    print(f"Size of {file_path}: ", file_size_in_kb, " KB")
    if file_size_in_kb > MAX_FILE_SIZE_IN_KB:
        return False, {'file': f'File size of {file_size_in_kb} KB exceeds max file size of {MAX_FILE_SIZE_IN_KB} KB'}
    
    # validate file data row by row
    with open(file_path) as file:
        csv_file = csv.reader(file)
        file_header = next(csv_file)
        print("file_header: ")
        print(file_header)

        required_headers = ['id', 'name', 'dob', 'gender', 'address', 'first_release_year', 'no_of_albums_released', 'created_at', 'updated_at']
        num_of_headers = len(required_headers)

        common_headers = set(required_headers).intersection(set(file_header))
        print("common_headers: ", common_headers)

        is_all_header_present = common_headers == set(required_headers)
        print("is_all_header_present: ", is_all_header_present)

        if is_all_header_present == False:
            return False, {'file': f'Headers missing. Headers should be: ({', '.join(required_headers)})'}
        
        # check if header is in correct order or not
        for i, (header_1, header_2) in enumerate(zip(required_headers, file_header[:num_of_headers]), start=1):
            if str(header_1).lower() != str(header_2).lower():
                if i == 1:
                    position_string = '1st'
                elif i == 2:
                    position_string = '2nd'
                elif i == 3:
                    position_string = '3rd'
                else:
                    position_string = f'{i}th'
                return False, {'file': f"'{header_1}' should be in {position_string} column, not '{header_2}'"}

        # all ids are present and in correct order
        # now can verify each data row by row
        row_index = 2
        for row in csv_file:
            print(row)
            id, name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at = \
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
            
            required_data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'first_release_year': first_release_year,
                'no_of_albums_released': no_of_albums_released,
            }
            # check if empty data is present in required_data values
            for field in required_data.keys():
                if len(required_data[field]) == 0:
                    return False, {'file': f"Empty {field} in row number {row_index}"}

            # check if id is correct
            if not re.match(r'^\d+$', str(id)):
                return False, {'file': f"Found wrong id '{id}' in row number {row_index}"}
            
            # check if name or address exceed max length 255
            if len(name) > 255:
                return False, {'file': f"Name exceeds max length 255 in row number {row_index}"}
            
            if len(address) > 255:
                return False, {'file': f"Address exceeds max length 255 in row number {row_index}"}

            # verify if datetime fields are correct - dob (skip check for created_at and updated_at)
            correct_date_format = "9/30/1997 0:00"
            if not re.match(r'^(\d){1,2}/(\d){1,2}/(\d){4}\s(\d){1,2}:(\d){1,2}$', dob):
                return False, {'file': f"Found wrong dob '{dob}' in row number {row_index}. Correct example format: {correct_date_format}"}
            
            # check if gender is within accepted values 'm', 'f' or 'o'
            if gender not in ('m', 'f', 'o'):
                return False, {'file': f"Found wrong gender '{gender}' in row number {row_index}"}
            
            if not re.match(r'^[0-9]+$', no_of_albums_released):
                return False, {'file': f"Found wrong no_of_albums_released '{no_of_albums_released}' in row number {row_index}"}

            # check for 4 digit number starting with either 1 or 2
            if not re.match(r'[12]\d{3}', first_release_year):
                return False, {'file': f"Found wrong first_release_year '{first_release_year}' in row number {row_index}. Should be between 1000 and 2999"}
            current_year = datetime.now().year
            if int(first_release_year) > current_year:
                return False, {'file': f"first_release_year value '{first_release_year}' exceeds current year {current_year} in row number {row_index}"}

            row_index += 1

        return False, {'file': 'test test'}
    # all data validated and ready for insert
    return True, {}