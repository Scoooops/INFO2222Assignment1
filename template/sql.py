import sqlite3
import os
import hashlib

salt = os.urandom(32)

# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''
    # Get the database running
    def __init__(self, database_arg=":memory:"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------

    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin', email='admin@admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username TEXT,
            password VARCHAR(255),
            email VARCHAR(30),
            admin INTEGER DEFAULT 0,
            publicKey TEXT
        );""")

        self.commit()

        self.execute("DROP TABLE IF EXISTS Friends")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Friends(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username_one TEXT,
            username_two TEXT
        );""")

        self.commit()

        # Add our admin user
        self.add_user('admin', 'admin', email, publicKey=None, admin=1)
        self.add_user('owen', 'owen', email, publicKey=None, admin=0)
        self.add_user('cooper', 'cooper', email, publicKey=None, admin=0)

        sql_cmd = """
                  INSERT INTO Friends
                  VALUES(NULL, '{username_one}', '{username_two}');
                  """
        sql_cmd = sql_cmd.format(username_one='owen', username_two='cooper')
        self.execute(sql_cmd)
        self.commit()


        #ADD SAMPLE FREINDS HERE
        #USE THE FOLLOWING CODE AND CHANGE THE REQUIRED NAMES:
        
        #sql_cmd = """
        #          INSERT INTO Friends
        #          VALUES(NULL, '{username_one}', '{username_two}');
        #          """
        #sql_cmd = sql_cmd.format(username_one='owen', username_two='cooper')
        #self.execute(sql_cmd)
        #self.commit()



    def checkFriend(self, username, user_to):
        sql_query = """
                SELECT 1
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=user_to)


        self.execute(sql_query)
        if self.cur.fetchone():
            sql_query = """
                    SELECT 1
                    FROM Friends
                    WHERE
                      username_one = '{username_one}' AND username_two = '{username_two}'
                """

            sql_query = sql_query.format(username_one=username, username_two = user_to)
            self.execute(sql_query)

            if self.cur.fetchone():
                sql_query = """
                        SELECT publicKey
                        FROM Users
                        WHERE username = '{username}'
                """
                sql_query = sql_query.format(username=user_to)
                self.execute(sql_query)
                userTopublicKey = self.cur.fetchone()
                return userTopublicKey
            else:
                sql_query = """
                      SELECT 1
                      FROM Friends
                      WHERE
                        username_one = '{username_one}' AND username_two = '{username_two}'
                  """

                sql_query = sql_query.format(username_one=user_to, username_two = username)
                self.execute(sql_query)
                if self.cur.fetchone():
                    sql_query = """
                            SELECT publicKey
                            FROM Users
                            WHERE username = '{username}'
                    """
                    sql_query = sql_query.format(username=user_to)
                    self.execute(sql_query)
                    userTopublicKey = self.cur.fetchone()
                    return userTopublicKey
                else:
                    return False
        else:
          return False

    def storeKey(self, username, publicKey):
        sql_cmd = """
                UPDATE Users
                SET
                    publicKey = '{publicKey}'
                WHERE
                    username = '{username}'
            """
        sql_cmd = sql_cmd.format(publicKey=publicKey, username=username)
        self.execute(sql_cmd)
        self.commit()

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, email, publicKey, admin=0):
        sql_query = """
                SELECT 1
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)


        self.execute(sql_query)
        # If our query returns
        if not self.cur.fetchone():
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            sql_cmd = """
                    INSERT INTO Users
                    VALUES(NULL, '{username}', '{password}', '{email}', {admin}, '{publicKey}');
                """
            sql_cmd = sql_cmd.format(username=username, password=key.hex(), email=email, admin=admin, publicKey=publicKey)

            self.execute(sql_cmd)
            self.commit()
            return True
        else:
            return False

    #-----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password, publicKey):
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        sql_query = """
                SELECT 1
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """

        sql_query = sql_query.format(username=username, password=key.hex())


        self.execute(sql_query)
        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False
