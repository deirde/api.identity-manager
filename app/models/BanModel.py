from app import app
from flask import request
from phpserialize import *
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.config.Config import Config as config_app
from app.services.TimestampService import get_or_ko as service_timestamp_get


class Ban(db.Model):


    __bind_key__ = 'sqlite'
    __tablename__ = 'ban'


    id = db.Column(db.Integer, primary_key = True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    signature = db.Column(db.Text)
    counter = db.Column(db.Integer)
    is_banned = db.Column(db.Boolean)


    def __init__(self, insert_date, last_update_date, signature, counter=0, is_banned=False):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.signature = signature
        self.counter = counter
        self.is_banned = is_banned


    @property
    def __repr__(self):
        return '<Request %r>' % self.signature


    ###
    # Generate a basic client signature.
    ###
    @staticmethod
    def generate_signature():
        return dumps(str({
            request.environ['HTTP_USER_AGENT'],
            request.environ['HTTP_ACCEPT'],
            request.environ['REMOTE_ADDR'],
        }))


    @staticmethod
    def get():
        m = Ban.query.filter_by(signature = Ban.generate_signature()).first()
        if not isinstance(m, Ban):
            m = Ban.add()
        return m


    @staticmethod
    def add():
        now = service_timestamp_get()
        try:
            m = Ban(now, now, Ban.generate_signature(), 1, False)
            db.session.add(m)
            db.session.commit()
            return True
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # Grant or deny the access to the client.
    # If the client requests, for the period predefined,
    #   is major then the allowed requests,he wins the ban.
    # When the timeout is over the ban is released.
    ###
    @staticmethod
    def grant(m):
        if isinstance(m, Ban):
            now = service_timestamp_get()
            if (now - m.last_update_date) > config_app().data['ban_timeout_millis'] / 1000:
                m.is_banned = False
                m.counter = 0
                m.last_update_date = now
            if m.last_update_date < (now - config_app().data['ban_trap_range_millis'] / 1000):
                m.counter = 0
                m.last_update_date = now
            else:
                m.counter += 1
                if m.counter > config_app().data['ban_trap_max_attempts_in_range']:
                    return False
            if m.is_banned is True:
                return False
            db.session.commit()
            db.session.close()
        return True


    ###
    # Clean up the database table from garbage.
    ###
    @staticmethod
    def clean():
        now = service_timestamp_get()
        diff = now - config_app().data['ban_trap_range_millis'] / 1000
        try:
            Ban.query.filter(Ban.last_update_date < diff).delete()
            db.session.commit()
            db.session.close()
            return True
        except BaseException as e:
            _(500, str(e))
            return False
