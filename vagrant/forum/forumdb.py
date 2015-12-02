#
# Database access functions for the web forum.
# 

import time
import psycopg2
# bleach is an input sanitization library by Mozilla
import bleach


## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    ## Database connection
    DB = psycopg2.connect("dbname = forum")
    ## Cursor creation
    curs = DB.cursor()
    curs.execute("SELECT content, time FROM posts ORDER BY time DESC")
    # added output sanitization to content since we already have bad data in dbase
    posts = [{'content': str(bleach.clean(row[0])), 'time': str(row[1])} for row in curs.fetchall()]
    DB.close()
    return posts
    

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    ## Database connection
    DB = psycopg2.connect("dbname = forum")
    ## Cursor creation
    curs = DB.cursor()
    # input sanitization
    content = bleach.clean(content)
    ## Very important, values must be passed as a tuple & single item tuple needs comma
    ## Use DB API parameter passing rather than string substitution for security
    curs.execute("INSERT INTO posts (content) VALUES (%s)", (content,))
    DB.commit()
    DB.close()
