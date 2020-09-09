# -*- coding: utf-8 -*-

from app import app
from flask import request, json, jsonify
from app.controllers.BaseController import *
from app.decorators.ValidateInput import *
from app.decorators.HandleSecret import check_secret
from app.models.UserModel import User as model_user
from app.models.RegistryModel import Registry as model_registry
from app.decorators.ProcessResponse import process_response as _
from app.decorators.HandleBan import handle_ban


###
# The signup route which creates an inactive user
#   and returns the key needed for activating it.
#
# @method <post>
# @header string <secret>
# @header string <email>
# @header string <password>
# @return integer <status>
# @return string <key>
###
@app.route('/v1/account/signup/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_signup
def signup():
    response = model_user.signup(request.headers.get('email'),
                                 request.headers.get('password'))
    if response is False:
        _(500, 'Something wrong creating the account', stop=True)
    return jsonify({
        'status': 200,
        'key': response
    })


###
# The user activation route.
# After the activation, the user can generate tokens.
# Note: the user is not authorized to retrieve or update any data,
#   in the order to do so the token must be consumed.
#
# @method <post>
# @header string <secret>
# @header string <key>
# @return integer <status>
###
@app.route('/v1/account/activate/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_activate
def activate():
    response = model_user.activate(request.headers.get('key'))
    if response is None:
        _(400, 'No user associated to the provided email', stop=True)
    if response is False:
        _(401, 'The provided key is invalid', stop=True)
    _(200, 'The email has ben activated', stop=True)


###
# The authenticate route which generates tokens.
# The token has a short life and expires
#   after a precise amount of seconds defined into the configuration file.
#
# @method <post>
# @header string <secret>
# @header string <email>
# @header string <password>
# @return integer <status>
# @return integer <expiration_time>
# @return string <token>
###
@app.route('/v1/account/authenticate/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authenticate
def authenticate():
    response = model_user.authenticate(request.headers.get('email'),
                                       request.headers.get('password'))
    if response is None or response is False:
        _(401, 'Wrong login', stop=True)
    return jsonify({
        'status': 200,
        'expiration_time': response['expiration_time'],
        'token': response['token']
    })


###
# The refresh token route which generates a new tokens invalidating the old one.
#
# @method <post>
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <status>
# @return integer <expiration_time>
# @return string <token>
###
@app.route('/v1/account/token_refresh/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_token_refresh
def token_refresh():
    response = model_user.refresh_token(request.headers.get('email'),
                                        request.headers.get('token'))
    if response is False:
        _(401, 'The provided token is invalid or expired', stop=True)
    if response is None:
        _(500, 'Something wrong refreshing the token', stop=True)
    return jsonify({
        'status': 200,
        'expiration_time': response['expiration_time'],
        'token': response['token']
    })


###
# The route which generates the one-time token containing the user identity.
# This token (or ott-token) requires to be used immediately after the generation
#   because it has a very short life.
# It's supposed to be used from third-party apps
#   to get the ability to generate auth token independently.
#
# @method <post>
# @header string <secret>
# @header string <email>
# @header string <password>
# @return integer <status>
# @return integer <expiration_time>
# @return string <token>
###
@app.route('/v1/account/ott_generate/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authenticate
@validate_input_for_token_refresh
def ott_generate():
    response = model_user.ott_generate(request.headers.get('email'),
                                       request.headers.get('token'))
    if response is None or response is False:
        _(401, 'The provided token is invalid or expired', stop=True)
    return jsonify({
        'status': 200,
        'expiration_time': response['expiration_time'],
        'token': response['token']
    })


###
# Consume a token (or ott-token) for getting the user identity.
# After that the client can start
#   to generate authorisation tokens independently.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <status>
# @return integer <id>
# @return string <email>
# @return string <password>
@app.route('/v1/account/ott_authorize/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
def ott_authorize():
    response = model_user.verify_ott_auth_token(request.headers.get('email'),
                                                request.headers.get('token'))
    if response is False or response is None:
        _(401, 'The provided token is invalid or expired', stop=True)
    return jsonify({
        'status': 200,
        'id': response['id'],
        'email': response['email'],
        'token': response['token'],
        'expiration_time': response['expiration_time'],
    })


###
# Authorize a token returning the user identity.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <status>
# @return integer <id>
# @return string <email>
@app.route('/v1/account/authorize/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
def authorize():
    response = model_user.verify_auth_token(request.headers.get('email'),
                                            request.headers.get('token'))
    if response is False or response is None:
        _(401, 'The provided token is invalid or expired', stop=True)
    return jsonify({
        'status': 200,
        'id': response['id'],
        'email': response['email']
    })


###
# Update the user email keeping trace of the old one as historical data.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <old_email>
# @return integer <new_email>
# @return integer <status>
@app.route('/v1/account/update_email/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
@validate_input_for_update_email
def update_email():
    m_user = json.loads(authorize().data.decode('utf-8'))
    response = model_user.update_email_by_id(m_user['id'],
                                             request.headers.get('new_email'))
    if response is None:
        _(400, 'No user associated to the provided parameters', stop=True)
    if response is False:
        _(500, 'Something wrong saving your data', stop=True)
    _(200, 'The email has been updated and the account needs to be activated again', stop=True)


###
###
# Update the user password and
#   keep trace of the old one as historical data.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <old_password>
# @return integer <new_password>
# @return integer <status>
@app.route('/v1/account/update_password/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
@validate_input_for_update_password
def update_password():
    m_user = json.loads(authorize().data.decode('utf-8'))
    response = model_user.update_password_by_id(m_user['id'],
                                                request.headers.get('old_password'),
                                                request.headers.get('new_password'))
    if response is None:
        _(400, 'No user associated to the provided parameters', stop=True)
    if response is False:
        _(500, 'Something wrong saving your data', stop=True)
    _(200, 'The password has been updated and the account needs to be activated again', stop=True)


###
# As a step of the password lost journey if provided email exists
#   it generates and returns a token, returning token can be used to reset the password.
#
# @method $post
# @header string <secret>
# @header string <email>
# @return integer <status>
# @return string <key>
@app.route('/v1/account/is_valid/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_is_valid
def is_valid():
    response = model_user.is_valid(request.headers.get('email'))
    if response is False:
        _(400, 'No user associated to the provided parameters', stop=True)
    return jsonify({
        'status': 200,
        'key': response
    })


###
# Update the user password with the new one provided and 
#   keep the trace of the old one as historical data.
#
# @method $post
# @header string <secret>
# @header string <token>
# @return integer <old_password>
# @return integer <new_password>
# @return integer <status>
@app.route('/v1/account/reset_password/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_reset_password
def reset_password():
    response = model_user.reset_password(request.headers.get('key'))
    if response is None:
        _(400, 'No user associated with the provided key', stop=True)
    if response is False:
        _(500, 'Something wrong resetting the password', stop=True)
    return jsonify({
        'status': 200,
        'password': response
    })


###
# Retrieve the user registry data.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <status>
# @return array <registry>
@app.route('/v1/account/get_registry/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
def get_registry():
    m_user = json.loads(authorize().data.decode('utf-8'))
    response = {
        'status': 200,
        'registry': model_registry.get_data_by_user__id(m_user['id'])
    }
    return jsonify(response)


###
# Update the user registry data.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @header string <name>
# @header string <bio>
# @header string <url>
# @header string <company>
# @header string <location>
# @header string <opt_in_email>
# @return integer <status>
@app.route('/v1/account/update_registry/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
def update_registry():
    m_user = json.loads(authorize().data.decode('utf-8'))
    if model_registry.update_registry_by_id(m_user['id'], request.headers) is False:
        _(500, 'Something wrong updating the registry', stop=True)
    _(200, 'The registry has been updated', stop=True)


###
# Return the user Stripe ID, if it exists.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return string <stripe_id>
@app.route('/v1/account/get_stripe_id/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
def get_stripe_id():
    response = model_user.verify_auth_token(request.headers.get('email'),
                                            request.headers.get('token'))
    if response is False or response is None:
        _(401, 'The provided token is invalid or expired', stop=True)
    return jsonify({
        'status': 200,
        'stripe_id': response['stripe_id']
    })
    
    
###
# Return the user Stripe ID, if it exists.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @header string <stripe_id>
# @return boolean
@app.route('/v1/account/set_stripe_id/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
@validate_input_for_set_stripe_id
def set_stripe_id():
    response = model_user.set_stripe_id(request.headers.get('email'),
                                        request.headers.get('token'),
                                        request.headers.get('stripe_id'))
    if response is None:
        _(401, 'The provided token is invalid or expired', stop=True)
    if response is False:
        _(401, 'stripe_id cannot be updated', stop=True)
    _(200, 'Stripe ID has been updated', stop=True)


###
# Logout user destroying the nonce and so invalidating any previously actived token.
#
# @method $post
# @header string <secret>
# @header string <email>
# @header string <token>
# @return integer <status>
@app.route('/v1/account/logout/', methods=['POST'])
@check_secret
@handle_ban
@validate_input_for_authorize
def logout():
    m_user = json.loads(authorize().data.decode('utf-8'))
    if m_user is None:
        _(401, 'No user associated to the provided parameters', stop=True)
    response = model_user.logout(m_user['id'])
    if response is False:
        _(500, 'Something wrong logging out the user', stop=True)
    _(200, 'The user has been logged out', stop=True)
