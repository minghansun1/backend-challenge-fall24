# Penn Labs Backend Challenge

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipx`
   - `brew install pipx` (macOS)
   - See instructions here https://github.com/pypa/pipx for other operating systems
4. Install `poetry`
   - `pipx install poetry`
5. Install packages using `poetry install --no-root` (Python files didn't have an init).

## Running API

1. Enter poetry virtual environment with `poetry shell`
2. Run `bootstrap.py`, which creates 2 users.
3. Run `app.py`

   If this isn't working, make sure the python interpreter is that of the poetry virtual environment.
4. Go to Postman or another API tester to test the API calls.
5. For API endpoints that require authentication, sign in by passing a `{"username": 'actual username', "password": 'actual password'}` request body while calling `/api/login/`. An example is: `{"username" : "minghan","password" : "password"}`.

   Then, go to the **Authorization** section, switch the **Auth Type** to **Bearer Token**, and paste the returned JWT token into the text field named **Token**.
   
   The login expires in 30 minutes.
6. Call each API endpoint. Try edge cases such as trying to comment under another user's name, favoriting and unfavoriting clubs etc.

## File Structure

- `app.py`: Main file. Includes API endpoints and code for initializing a Flask web application instance and connecting SQLAlchemy to the SQLite database.
- `models.py`: Model definitions for SQLAlchemy database models. Contains models for clubs, tags, users, and comments. Also includes 2 relationship tables for the club-tag, user-favorites many-to-many relationships.
- `bootstrap.py`: Code for creating and populating your local database. Contains 2 functions: one to load the data from clubs.json into the database and one to initialize 2 users.
- `db.py`: Code for initializing a database. Done separately from app.py to avoid circular imports.
- `auth_middleware.py`: Code for validating authentication and protecting private endpoints.
- `.env`: Contains the secret key for authentication. Technically should be in the gitignore but you guys need to run my code.

## Database Schema:
### Models:
- **Club**
   - **Attributes**
      - **`id`**: Unique integer identifier for the club (Primary Key).
      - **`code`**: Unique code representing the club.
      - **`name`**: Name of the club.
      - **`description`**: Description of the club.
      - **`favorites`**: Integer count of how many users have favorited the club. 
   - **Relationships**
      - **`tags`**: Many-to-Many relationship with Tag. Chosen since a club can have multiple tags, and multiple clubs can have one tag.
      - **`users`**: Many-to-Many relationship with User. Chosen since a club can have multiple users, and a user can be in multiple clubs.
      - **`comments`**: One-to-Many relationship with Comments. Chosen since a comment is only about one club, and there can be multiple comments for each club.
   - **Methods**
      - **`to_dict`**: Returns a dictionary representation of the club.

- **User**
   - **Attributes**
      - **`id`**: Unique integer identifier for the user (Primary Key).
      - **`username`**: Username of the user.
      - **`email`**: Email of the user.
      - **`hashed_password`**: Password of the user. Hashed to keep it private in case someone gets access to the database.
      - **`first_name`**: First name of the user.
      - **`last_name`**: Last name of the user.
      - **`school`**: School of the user.
      - **`major`**: Major of the user.
      - **`grad_year`**: Graduation year of the user.
   - **Relationships**
      - **`fav_clubs`**: Many-to-Many relationship with Club. Chosen since a user can have multiple favorite clubs, and a club can be favorited by multiple users.
      - **`comments`**: One-to-Many relationship with ClubComments. Chosen since a user can have multiple comments, but a comment can't be made by more than one user.
   - **Methods**
      - **`set_password`**: Sets `hashed_password` to a hashed version of the password input from the user.
      - **`check_password`**: Checks if an inputted password matches the hashed password after hashing.
      - **`to_private_dict`**: Returns a dictionary representation of the user, excluding the hashed password and favorite clubs. Used internally in Penn Club Review since it contains all user info.
      - **`to_public_dict`**: Returns a dictionary representation of the user, including all fields. Used for other PennLabs apps since passwords shouldn't be shared, and other apps won't care about a user's favorite clubs.

- **Tag**
   - **Attributes**
      - **`id`**: Unique integer identifier for the tag (Primary Key).
      - **`name`**: Name of the tag.
   - **Relationships**
      - **`clubs`**: Many-to-Many relationship with Club. Chosen since a club can have multiple tags, and multiple clubs can have one tag.
   - **Methods**
      - **`to_dict`**: Returns a dictionary representation of the tag.

- **ClubComments**
   - **Attributes**
      - **`id`**: Unique integer identifier for the comment (Primary Key).
      - **`text`**: Text content of the comment.
      - **`timestamp`**: Time the comment was made.
   - **Relationships**
      - **`club`**: Many-to-One relationship with Clubs. Chosen since a comment is only about one club, and there can be multiple comments for each club.
      - **`user`**: Many-to-One relationship with Users. Chosen since a user can have multiple comments, but a comment can't be made by more than one user.
      - **`parent_comment`**: One-to-One relationship with another comment. Chosen since a comment can only have one parent. Didn't use children since a comment can have multiple children, so tracking parents is easier and more space-efficient.
   - **Methods**
      - **`to_dict`**: Returns a dictionary representation of the comment.

### Association Tables:
- **club_to_tags**: Association table for the many-to-many relationship between Club and Tag.
   - **Columns**
      - **`club_id`**: Foreign Key to Club.
      - **`tag_id`**: Foreign Key to Tag.

- **user_to_favorite_club**: Association table for the many-to-many relationship between User and Club.
   - **Columns**
      - **`user_id`**: Foreign Key to User.
      - **`club_id`**: Foreign Key to Club.

## API Endpoints:
- **General Endpoints**
   - **Welcome Endpoints**
      - GET: `/`
         - **Description**: Displays a welcome message.
         - **Response**: "Welcome to the Penn Club Review!"
      - GET: `/api`
         - **Description**: Displays a welcome message for the API.
         - **Response**: "Welcome to the Penn Club Review API!"
   - **Login Endpoint**
      - POST: `/api/login`
         - **Description**: Returns a valid JSON Web Token if user provides valid login information for a user.
         - **Parameters**: `username`, `password`
         - **Response**: 200 OK with JWT token or 400 Bad Request if login info is formatted incorrectly or 401 Unauthorized if login info is incorrect.

- **Club Endpoints**
   - GET: `/api/clubs`
      - **Description**: Returns all clubs in the database as a JSON list. If there are no clubs, returns an empty list.
      - **Response**: 200 OK with JSON list of clubs.
   - GET: `/api/clubs/<string:name>`
      - **Description**: Returns all clubs in the database that contain the given string in their name. If the given string is empty or `None`, returns a 400 Bad Request error. If there are no clubs in the database, returns an empty list.
      - **Parameters**: `name` - Name of the club.
      - **Response**: 200 OK with JSON list of matching clubs or 400 Bad Request if no name is provided.
   - POST: `/api/clubs`
      - **Description**: Creates a new club in the database with a code, name, description, and tags. Returns a 400 Bad Request error if the request is not JSON, or if required fields are missing, or if the club code already exists.
      - **Request Body**: JSON dictionary with `code`, `name`, `description`, and `tags` keys.
      - **Response**: 200 OK with a message indicating success, or 400 Bad Request for errors.
   - PUT: `/api/clubs/<int:club_id>`
      - **Description**: Modifies a club's name, description, and tags. The club code cannot be modified. Returns a 400 Bad Request error if the request is not JSON or a 404 Not Found error if the club is not found.
      - **Parameters**: `code` - a unique identifier for each club.
      - **Request Body**: JSON dictionary with `name`, `description`, and `tags` keys.
      - **Response**: 200 OK with a message indicating success, or 400 Bad Request/404 Not Found for errors.

- **User Endpoints**
   - GET: `/api/users/<int:user_id>`
      - **Description**: Returns all information of a user (except password) with the given user ID. If no user ID is given or the user is not found, returns a 400 Bad Request error.
      - **Parameters**: `user_id` (URL parameter) - a unique identifier for the user.
      - **Response**: 200 OK with JSON object containing user information, or 400 Bad Request/404 Not Found for errors.
   - PUT: `/api/users/<int:user_id>/clubs/<string:code>/favorite`
      - **Description**: Lets a student favorite a club, incrementing the number of favorites a club has. If the user or club is not found, returns a 404 Not Found error. Requires the user to be logged in.
      - **Parameters**: `user_id` - a unique identifier for each user, `code` - a unique identifier for each club.
      - **Response**: 200 OK with a message indicating success, or 200 with a message indicating that the club has already been favorited by the user, or a 404 Not Found error if the user or club aren't in the database.

   - PUT: `/api/users/<int:user_id>/clubs/<string:code>/unfavorite`
      - **Description**: Lets a student unfavorite a club, decrementing the number of favorites a club has. If the user or club is not found, returns a 404 Not Found error. Requires the user to be logged in.
      - **Parameters**: `user_id` - a unique identifier for each user, `code` - a unique identifier for each club.
      - **Response**: 200 OK with a message indicating success, or 200 with a message indicating that the club hasn't been favorited by the user, or a 404 Not Found error if the user or club aren't in the database.

- **Tag Endpoints**
   - GET: `/api/tags/clubcount`
      - **Description**: Returns all tag names and the number of clubs associated with each tag as a list of dictionaries. If there are no tags in the database, returns an empty list.
      - **Response**: 200 OK with JSON list of tag names and club counts.

- **Comment Endpoints**
   - GET: `/api/clubs/<string:code>/comments`
      - **Description**: Returns all comments for a club with the given code as a JSON list.
      - **Response**: 200 OK with JSON list comments, or 404 Not Found error if the club with the given code isn't in the database.

   - GET: `/api/clubs/<int:user_id>/comments`
      - **Description**: Returns all comments made by a given user as a JSON list.
      - **Response**: 200 OK with JSON list comments, or 404 Not Found error if the user with the given ID isn't in the database.

   - POST: `/api/users/<int:user_id>/clubs/<string:code>/comments`
      - **Description**: Allows a user to comment on a specific club. Requires the user to be logged in.
      - **Parameters**: `text` - a message that constitutes the body of the comment.
      - **Response**: 200 OK with a message indicating success, 403 Forbidden if attempting to comment for another user, 400 Bad Request if data is formatted incorrectly, 404 Not Found if club with the given code doesn't exist in the database.

   - POST: `/api/users/<int:user_id>/clubs/<string:code>/comments/<int:comment_id>`
      - **Description**: Allows a user to reply to a specific comment. The club that this comment is about is determined by the parent comment. Requires the user to be logged in.
      - **Parameters**: `text` - a message that constitutes the body of the comment.
      - **Response**: 200 OK with a message indicating success, 403 Forbidden if attempting to comment for another user, 400 Bad Request if data is formatted incorrectly, 404 Not Found if club with the given code or comment with the given ID doesn't exist in the database.
