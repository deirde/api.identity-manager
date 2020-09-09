# -*- coding: utf-8 -*-

from app import app
from flask import g
from app.config.Config import Config as config_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.decorators.HandleSecret import increase_usage
from app.models.TokenBanlistModel import TokenBanlist as model_token_banlist
from app.models.BanModel import Ban as model_ban
from app.decorators.HandleBan import handle_ban


###
# To accept the request there're requirements:
#   the client signature, it mustn't be banned
#   the param secret is provided and recognized
#   the usage limit for the secret provided is not over quota
###
@app.before_request
def before_request():
    pass


###
# Increases the usage limit and
#   enable cross-origin resource sharing.
###
@app.after_request
@increase_usage
def after_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    f.headers.add('Access-Control-Allow-Origin', '*')
    f.headers.add('Access-Control-Allow-Headers', '*')
    f.headers.add('Access-Control-Allow-Methods', '*')
    return f


###
# Clean up banned tokens as scheduled job.
###
def transport():
    model_token_banlist.clean()
    model_ban.clean()


schedule = BackgroundScheduler(
    timezone=config_app().data['timezone'],
    daemon=True
)
schedule.add_job(
    transport,
    'interval',
    seconds=config_app().data['transport_interval_seconds']
)
schedule.start()
