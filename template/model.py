'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import sql

# Initialise our views, all arguments are defaults for the template
page_view = view.View()
db = sql.SQLDatabase('test.db')
db.database_setup()
#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index")


def contact():
    return page_view("contact")

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password, publicKey):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    if db.check_credentials(username, password, publicKey):
        return page_view("validlogin", header='validloginheader', name=username)
    else:
        if username != "admin": # Wrong Username
            err_str = "Incorrect Username"
            login = False

        if password != "password": # Wrong password
            err_str = "Invalid password"
            login = False
        return page_view("invalid", reason=err_str)
    """
    # By default assume good creds
    login = True

    if username != "admin": # Wrong Username
        err_str = "Incorrect Username"
        login = False

    if password != "password": # Wrong password
        err_str = "Incorrect Password"
        login = False

    if login:
        return page_view("valid", name=username)

    else:
        return page_view("invalid", reason=err_str)
    """


def valid_login(publicKey, username):
    db.storeKey(username, publicKey)
    return page_view("validlogin", header='validloginheader', name=username)
#-----------------------------------------------------------------------------
def register_form():
    return page_view("register")


def register_check(username, password, email):
    register = True

    if (username and password and email) == "":
        err_str = "Please enter a valid username, password and email"
        register = False

    if username == "":
        err_str = "Please enter a valid username"
        register = False

    if password == "":
        err_str = "Please enter a valid password"
        register = False

    if email == "":
        err_str = "Please enter a valid email"
        register = False

    if db.add_user(username,password,email,None):
        return page_view("valid", name=username)
    else:
        err_str = "Username already exists."
        return page_view("invalid", reason=err_str)

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.",
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass

#-----------------------------------------------------------------------------
# Logged in for chat
#-----------------------------------------------------------------------------
def chat_get_key(username, user_to):
    if user_to != None:
      userTopublicKey = db.checkFriend(username, user_to)
      if userTopublicKey == False or userTopublicKey[0] == 'None':
          return "Error"
      else:
          return userTopublicKey

def chat(username, text, user_to):
    if not(text == "Error" or user_to == None):
        return page_view("chatsuccessful", header="chatencode", text=text, username=username, user_to=user_to)
    elif text == "":
        return page_view("chat", header="chatroom", message=text, username=username, user_to=user_to)
    else:
        return page_view("chat", header="chatroom", message=text, username=username, user_to=user_to)
#-----------------------------------------------------------------------------
# Not logged in
#-----------------------------------------------------------------------------

def not_logged_in():
    return page_view("not_logged_in")

#-----------------------------------------------------------------------------
# User already logged in
#-----------------------------------------------------------------------------

def user_already_logged_in():
    return page_view("already_logged_in")


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
