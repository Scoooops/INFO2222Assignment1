'''
    This file will handle our typical Bottle requests and responses
    You should not have anything beyond basic page loads, handling forms and
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file, response
import bottle
from beaker.middleware import SessionMiddleware
import json
import time

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)

user_messages = dict()

import model
#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index

        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login

        Serves the login page
    '''
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login

        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    time.sleep(0.5)
    publicKey = None
    session = bottle.request.environ.get('beaker.session')
    session['name'] = username
    session.save()
    return model.login_check(username, password, publicKey)


@route('/validlogin', method='POST')
def valid_login():
    session = bottle.request.environ.get('beaker.session')
    username = session.get('name')
    publicKey = request.json
    time.sleep(0.5)
    return model.valid_login(publicKey, username)


@route('/chat')
def chat():
    session = bottle.request.environ.get('beaker.session')
    username = session.get('name')
    text = ""
    if username is not None:
        if username in user_messages.keys():
            for i in user_messages[username]:
                text += i + ":"
            text = text[:-1]
        return model.chat(username, text, None)
    else:
        return model.not_logged_in()

@post('/chat')
def post_chat():
    session = bottle.request.environ.get('beaker.session')
    username = session.get('name')
    user_to = request.forms.get('userto')
    userTopublicKey = model.chat_get_key(username, user_to)
    time.sleep(0.5)
    return model.chat(username, userTopublicKey, user_to)

@route('/chatsuccessful', method='POST')
def chat_successful():
    session = bottle.request.environ.get('beaker.session')
    username = session.get('name')
    time.sleep(1)
    encoded_message = request.json
    time.sleep(2)
    if encoded_message != None:
        message_details = encoded_message.split(":")
        user_to = message_details[0][1:]
        encoded_message = message_details[1][:-1]
        if user_to not in user_messages.keys():
            user_messages[user_to] = []
        user_messages[user_to].append(encoded_message)
        print(user_messages[user_to])
    return model.chat(username, "", None)

@get('/register')
def get_registration_controller():
    return model.register_form()

@post('/register')
def post_registration():
    username = request.forms.get('username')
    password = request.forms.get('password')
    email = request.forms.get('email')

    return model.register_check(username, password, email)


#-----------------------------------------------------------------------------

@get('/about')
def get_about():
    '''
        get_about

        Serves the about page
    '''
    return model.about()


@get('/contact')
def get_contact():
    return model.contact()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error):
    return model.handle_errors(error)
