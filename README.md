# Artist-Management-System

## Setup Instructions:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Updates so far:
1. Added a function to connect to mysql db
2. Created schema for user table
3. Created schema for artist table
4. Created schema for music table. Also added foreign key reference to artist table
5. Populated test values for user, artist, and music table
6. Created basic session handling with login and logout
7. Added signup page and created entry in user table upon signup
8. Added pagination while listing users, artists, and music in dashboard
9. Added functionality to add new user from the admin dashboard
10. Added functionality to update existing user from the admin dashboard
11. Added functionality to delete existing user from the admin dashboard
12. Added functionality to add new artist from the admin dashboard
13. Added functionality to update existing artist from the admin dashboard
14. Added functionality to delete existing artist from the admin dashboard
15. Added functionality to add new music from the admin dashboard
16. Added functionality to update existing music from the admin dashboard
17. Added functionality to delete existing music from the admin dashboard
18. CSV import and export added in admin dashboard
19. Added  parameterized queries to prevent sql injection
20. Added password hashing during signup and login
21. TODO: Add validation check while importing data for artist from CSV
22. Added validation for admin signup
23. Added validations to check if fields are empty or exceed their maximum lengths
24. Added other validations: checked if email is correct, checked if gender value is correct,
    checked if first_release_year is correct, and checked if no_of_albums_released is correct.
25. Maintained role based api access. 
* All access (user, artist, music) granted to super_admin
* Limited access (artist, music) granted to artist_manager
26. Refactored scripts and separated configurations to separate file
27. Made UI more user friendly with bootstrap
28. Removed password in /manage_user
29. Deployed a live demo version
30. TODO: Refactor and separate helper functions