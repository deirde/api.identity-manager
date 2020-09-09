from functools import wraps
from flask import request
from app.decorators.ProcessResponse import process_response as _
from app.models.UserModel import User as model_user
from app.services.EmailService import validate as service_email_validate


###
# Validate headers in user signing up context.
###
def validate_input_for_signup(f):
    @wraps(f)
    def default():
        if request.headers.get('email') is None or not request.headers.get('email'):
            _(412, 'The parameter email is required', stop=True)
        if request.headers.get('password') is None or not request.headers.get('password'):
            _(412, 'The parameter password is required', stop=True)
        if model_user.user_exists_by_email(request.headers.get('email')):
            _(409, 'The provided email is invalid or unavailable', stop=True)
        if service_email_validate(request.headers.get('email')) is None:
            _(403, 'The required service email is unreachable', stop=True)
        if service_email_validate(request.headers.get('email')) is False:
            _(412, 'The provided email is invalid', stop=True)
        return f()
    return default


###
# Validate headers in user activation context.
###
def validate_input_for_activate(f):
    @wraps(f)
    def default():
        if request.headers.get('key') is None or not request.headers.get('key'):
            _(412, 'The parameter key is required', stop=True)
        return f()
    return default


###
# Validate headers in user authentication context.
###
def validate_input_for_authenticate(f):
    @wraps(f)
    def default():
        if request.headers.get('email') is None or not request.headers.get('email'):
            _(412, 'The parameter email is required', stop=True)
        if request.headers.get('password') is None or not request.headers.get('password'):
            _(412, 'The parameter password is required', stop=True)
        return f()
    return default


###
# Validate headers in user token refresh context.
###
def validate_input_for_token_refresh(f):
    @wraps(f)
    def default():
        if request.headers.get('email') is None or not request.headers.get('email'):
            _(412, 'The parameter email is required', stop=True)
        if request.headers.get('token') is None or not request.headers.get('token'):
            _(412, 'The parameter token is required', stop=True)
        return f()
    return default


###
# Validate headers in user authorization context.
###
def validate_input_for_authorize(f):
    @wraps(f)
    def default():
        if request.headers.get('email') is None or not request.headers.get('email'):
            _(412, 'The parameter email is required', stop=True)
        if request.headers.get('token') is None or not request.headers.get('token'):
            _(412, 'The parameter token is required', stop=True)
        return f()
    return default


###
# Validate headers in user email update context.
###
def validate_input_for_update_email(f):
    @wraps(f)
    def default():
        if request.headers.get('old_email') is None or not request.headers.get('old_email'):
            _(412, 'The parameter old_email is required', stop=True)
        if service_email_validate(request.headers.get('old_email')) is None:
            _(403, 'The required service old_email is unreachable', stop=True)
        if service_email_validate(request.headers.get('old_email')) is False:
            _(412, 'The provided old_email is invalid', stop=True)
        if request.headers.get('new_email') is None or not request.headers.get('new_email'):
            _(412, 'The parameter new_email is required', stop=True)
        if service_email_validate(request.headers.get('new_email')) is None:
            _(403, 'The required service new_email is unreachable', stop=True)
        if service_email_validate(request.headers.get('new_email')) is False:
            _(412, 'The provided new_email is invalid', stop=True)
        if model_user.find_by_email(request.headers.get('old_email')) is None:
            _(412, 'The provided new_email cannot be used', stop=True)
        return f()
    return default


###
# Validate headers in user password update context.
###
def validate_input_for_update_password(f):
    @wraps(f)
    def default():
        if request.headers.get('old_password') is None or not request.headers.get('old_password'):
            _(412, 'The parameter old_password is required', stop=True)
        if request.headers.get('new_password') is None or not request.headers.get('new_password'):
            _(412, 'The parameter new_password is required', stop=True)
        return f()
    return default


###
# Validate headers in user existence check context.
###
def validate_input_for_is_valid(f):
    @wraps(f)
    def default():
        if request.headers.get('email') is None or not request.headers.get('email'):
            _(412, 'The parameter email is required', stop=True)
        if service_email_validate(request.headers.get('email')) is None:
            _(403, 'The required service email is unreachable', stop=True)
        if service_email_validate(request.headers.get('email')) is False:
            _(412, 'The provided email is invalid', stop=True)
        return f()
    return default


###
# Validate headers in user existence check context.
###
def validate_input_for_set_stripe_id(f):
    @wraps(f)
    def default():
        if request.headers.get('stripe_id') is None:
            _(412, 'The parameter stripe_id is required', stop=True)
        return f()
    return default


###
# Validate headers in user password reset context. @TODO
###
def validate_input_for_reset_password(f):
    @wraps(f)
    def default():
        return f()
    return default
