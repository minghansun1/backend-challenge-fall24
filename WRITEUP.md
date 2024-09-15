# Open-Ended Questions

## 1. 
I already implemented a login feature using JWT. This was done by writing an API endpoint (POST /api/login) that takes in a username and password and checking if it's valid. If the combination is valid, the program would return a JWT token. I also implemented a python function decorator that allows an API endpoint to take in a jwt token and confirm that it's valid before executing functions. This enables the protection of certain routes by limiting its use to authenticated users.

If I had more time I would've implemented a signup and logout feature. Signup by adding an API endpoint (POST /api/signup) that allows a person to create a user along with a password (and other info). Logout (POST /api/logout) is harder with JWT since it's stateless do tokens can't be destroyed on the serverside. However, when a user logs out, I could use a token blacklist to keep track of all tokens of users that have logged out, and treat them as unauthenticated.

I've addressed security vulnerabilities by hashing all passwords before they're stored on the server, and making it so that tokens are invalidated very frequently (every 30 minutes). 

Additional security measures I could use are blacklisting tokens with suspicious activity. Also, it's important to make my site reistant to SQL injection and CSRF attacks. SQLAlchemy automatically sanitizes user inputs and prevents SQL injection. I should also use libraries like Flask-WTF to CSRF tokens for each form, and validate tokens when recieving requests.

Some packages I've used to implement authentication are PyJWT to create and authenticate tokens, and Werkzeug to hash passwords. I'd also use FLask-WTF to implement CSRF tokens.

## 2.

I already implemented comments in this technical challenge. I chose to represent comments with a comment model, a single table. It contains the following fields: a unique `id` as the primary key, the `user_id` of the user who made the comment, `club_id` of the club that the comment is about, `parent_comment_id` which is the id of the parent comment, `text` which is the text part of the comment, and a `timestamp` of when the comment was written.

I've added foreign keys for the `user_id`, `club_id`, and `parent_comment_id`, since I want a comment to be able to point to a user, club, or parent comment that it's associated with.

I chose to model reply chains using parents for each comment. This is because comments have a treelike structure. A comment may have multiple replies to it, but can only have 1 parent. Modeling it in this way means that I only need constant space additional space per comment. Also, no additional relationship tables are required since there are no many-to-many relationships.

`POST /api/users/<int:user_id>/clubs/<string:code>/comments` creates a comment. The URL defines the user_id and club_id, the text is defined by the JSON payload, and the timestamp is automatically generated.

`POST /api/users/<int:user_id>/clubs/<string:code>/comments/<int:comment_id>` creates a comment reply. The URL defines the user_id, club_id, and parent_comment_id, the text is defined by the JSON payload, and the timestamp is automatically generated.

`GET /api/clubs/<string:code>/comments` gets all comments for a certain club. The database could be filtered using club_id, which can be found using the URL.

`GET /api/users/<int:user_id>/comments` gets all comments by a certain user. The database could be filtered using user_id, which is in the URL.

Some additional routes I'd implement are to edit and delete a comment, which would be `PUT /api/users/<int:user_id>/comments/<int:id>` and `DELETE /api/users/<int:user_id>/comments/<int:id>`

## 3.

There are a few things to consider when determining whether caching should be used: read-to-write ratio, the importance of data consistency, data access cost, and latency requirements. If a resource is read much more than it's written, or if data consistency/freshness isn't extremely important, or if a system demands low latency, caching may be worth it.

In my API, the following routes are worth being cached:

`GET /api/users/< int:user_id>`, because user data is never updated, outside of the favorite list. The favorite list of each user is also not that time sensitive, since the exact list of clubs that a user favorited isn’t important.

`GET /api/tags`, since tag data is unlikely to change very often, and it doesn't matter too much if tags are out of date.

`GET /api/clubs/<string:code>/comments`, since the set of all comments for all clubs is likely to be extremely large, so filtering a table for a certain club's comments is time intensive. Additionally, most people only read comments, so the read-write ratio will be high.

`GET /api/users/<int:user_id>/comments`, since the set of all comments for all users is likely to be extremely large, so filtering a table for a certain club's comments is time intensive. Additionally, most people only read comments, so the read-write ratio will be high.

Cache invalidation is a difficult problem that requires knowledge of a lot of different factors and a lot of fine tuning. However, one simple (but not optimal) solution would be to store a timestamp for all cached data, and invalidate certain types of data after a predetermined time. I could also implement a more complex caching system that takes into account the ammount of cached data and the frequency of access for each data to determine when to invalidate it.

Some possibly useful packages I'd look at are `lru-cache` for its ease of use and `Beaker` for its support of caching web applications and support of SQLAlchemy.