from app import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.services.TimestampService import get_or_ko as service_timestamp_get
from app.decorators.ProcessResponse import process_response as _


class TokenBanlist(db.Model):

    __bind_key__ = 'mysql'
    __tablename__ = 'token_banlist'

    id = db.Column(db.Integer, primary_key=True)
    insert_date = db.Column(db.Integer)
    expiration_time = db.Column(db.Integer)
    token = db.Column(db.String(64))

    def __init__(self, insert_date, expiration_time, token):
        self.insert_date = insert_date
        self.expiration_time = expiration_time
        self.token = token

    @property
    def __repr__(self):
        return '<ID %r>' % self.id

    ###
    # Add a token to the banlist
    #
    # @param integer $expiration_time
    # @param string $token
    # @return boolean
    ###
    @staticmethod
    def add(expiration_time, token):
        now = service_timestamp_get()
        try:
            m = TokenBanlist(now, expiration_time, token)
            db.session.add(m)
            db.session.commit()
            db.session.close()
            return True
        except BaseException as e:
            _(500, str(e))
            return False

    ###
    # Check if the token is banned
    #
    # @param string $token
    # @return boolean
    # ###
    @staticmethod
    def is_banned(token):
        m = TokenBanlist.query.filter_by(token=token).first()
        if m is not None:
            return True
        return False

    ###
    # Clean up the table deleting all the expired token
    #
    # @return boolean
    ###
    @staticmethod
    def clean():
        now = service_timestamp_get()
        try:
            TokenBanlist.query.filter(TokenBanlist.expiration_time < now).delete()
            db.session.commit()
            db.session.close()
            return True
        except BaseException as e:
            _(500, str(e))
            return False
