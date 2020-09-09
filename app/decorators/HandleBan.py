from app import app
from functools import wraps
from flask import g, request, json, jsonify, abort
from app.models.BanModel import Ban as model_ban
from app.decorators.ProcessResponse import process_response as _


###
# Ban manager decorator based on client signature and activity.
###
def handle_ban(f):
    @wraps(f)
    def default(*args, **kwargs):
        m = model_ban.get()
        if isinstance(m, model_ban):
            if model_ban.grant(m) is False:
                return _(423, 'Your signature is banned, try again later', stop=True)
            #print(m.id, m.counter)
        #else:
            #return _(500, 'Something wrong managing your signature', stop=True)
        
        #if m is None:
            #if model_ban.add() is not True:
                #return _(500, 'Something wrong adding your signature', stop=True)
        #else:
            #if m.is_banned is True:
                #return _(423, 'Your signature is banned, try again later', stop=True)
            #if model_ban.update(m) is not True:
                #return _(500, 'Something wrong managing your signature', stop=True)
        return f(*args, **kwargs)
    return default
