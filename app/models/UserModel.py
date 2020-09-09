from app import app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import base64, hashlib, random, string
from random import *
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.config.Config import Config as config_app
from app.services.TimestampService import get_or_ko as service_timestamp_get
from app.models.TokenBanlistModel import TokenBanlist as model_token_banlist
from app.models.HistoryModel import History as model_history
from app.decorators.ProcessResponse import process_response as _


class User(db.Model):


    __bind_key__ = 'mysql'
    __tablename__ = 'users'


    id = db.Column(db.Integer, primary_key=True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    nonce = db.Column(db.String(64))
    stripe_id = db.Column(db.String(24))
    is_active = db.Column(db.Boolean)


    def __init__(self, insert_date, last_update_date, email, password, nonce, stripe_id, is_active = 0):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.email = email
        self.password = password
        self.nonce = nonce
        self.stripe_id = stripe_id
        self.is_active = is_active


    @property
    def __repr__(self):
        return '<ID %r>' % self.id

    def user_exists_by_email(email):
        response = False
        if User.query.filter_by(email=email).first() is not None:
            response = True
        return response


    @staticmethod
    def password_hash(password):
        return pwd_context.encrypt(password)


    ###
    # @param string <password>
    # @param string <password_hash>
    # @return boolean
    ###
    def verify_password(password, password_hash):
        return pwd_context.verify(password, password_hash)


    ###
    # This user is not active yet, the flag is_active is set on false.
    #
    # @param string <email>
    # @param string <password>
    # @return mixed
    ###
    @staticmethod
    def signup(email, password):
        now = service_timestamp_get()
        password_hash = User.password_hash(password)
        try:
            m = User(now, now, email, password_hash)
            db.session.add(m)
            db.session.commit()
            db.session.close()
            response = base64.b64encode(bytes(str(now) + email, "utf-8"))
            return str(response)[2:-1]
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # After that this user is active and it means that the token can be generated.
    #
    # @param string <key>
    # @return mixed
    ###
    @staticmethod
    def activate(key):
        now = service_timestamp_get()
        try:
            params = base64.b64decode(str.encode(key)).decode('utf-8', 'ignore')
        except BaseException as e:
            _(500, str(e))
            _(406, 'The provided key has an invalid format', stop=True)
        insert_date = params[:10]
        email = params[10:]
        m = User.query.filter_by(insert_date=insert_date, email=email).first()
        if m is None:
            return m
        else:
            if m.is_active:
                _(412, 'This user cannot be activated', stop=True)
            else:
                try:
                    m.last_update_date = now
                    m.is_active = True
                    db.session.commit()
                    db.session.close()
                    return True
                except BaseException as e:
                    _(500, str(e))
                    return False
        return False


    ###
    # Token generation by email and password.
    # This is supposed to be used only once per session because the password shouldn't stored.
    #
    # @param string <email>
    # @param string <password>
    # @return mixed
    ###
    @staticmethod
    def authenticate(email, password):
        now = service_timestamp_get()
        m = User.query.filter_by(email=email).first()
        if not isinstance(m, User):
            return None
        if User.verify_password(password, m.password) is not True:
            return False
        if m.is_active == 0:
            return False
        if User.refresh_nonce(m.id) is not True:
            return False
        expires_in = config_app().data['token_expires_after_seconds']
        s = Serializer(m.nonce, expires_in=expires_in)
        token = s.dumps({'id': m.id})
        expiration_time = now + expires_in
        return {
            'token': token.decode('ascii'),
            'expiration_time': expiration_time
        }


    ### 
    # Refresh the user nonce, a user based key
    #
    # @param string <email>
    # @param string <token>
    # @return mixed
    @staticmethod
    def refresh_nonce(id):
        m = User.find_by_id(id)
        if m is None:
            return False
        try:
            m.nonce = User.generate_password(letters=True, punctuation=True, digits=True, _range=[64, 64])
            db.session.commit()
            return True
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # Token generation by email and token.
    # Furthermore, it invalidates the passed token.
    #
    # @param string <email>
    # @param string <token>
    # @return mixed
    ###
    @staticmethod
    def refresh_token(email, token):
        if model_token_banlist.is_banned(token) is True:
            return False
        attrs = User.verify_auth_token(email, token)
        if attrs is False or attrs is None or attrs['email'] != email:
            return False
        now = service_timestamp_get()
        m = User.query.filter_by(email=email).first()
        if not isinstance(m, User):
            return None
        if m.is_active == 0:
            return False
        expires_in = config_app().data['token_expires_after_seconds']
        expiration_time = now + expires_in
        s = Serializer(m.nonce, expires_in=expires_in)
        new_token = s.dumps({'id': m.id})
        return {
            'token': new_token.decode('ascii'),
            'expiration_time': expiration_time
        }


    ###
    # Return token containing user identity.
    # This token has a short life so it needs to be consumed immediately
    #   after the generation.
    #
    # @param string $email
    # @param string $password
    # @return string $token
    # @return integer $expiration_time
    ###
    @staticmethod
    def ott_generate(email, token):
        if model_token_banlist.is_banned(token) is True:
            return False
        attrs = User.verify_auth_token(email, token)
        if attrs is False or attrs is None or attrs['email'] != email:
            return False
        now = service_timestamp_get()
        m = User.query.filter_by(email=email).first()
        if m is None:
            return m
        if m.is_active == 0:
            return False
        expires_in = config_app().data['ott_token_expires_after_seconds']
        expiration_time = now + expires_in
        s = Serializer(m.nonce, expires_in=expires_in)
        new_token = s.dumps({'id': m.id})
        return {
            'token': new_token.decode('ascii'),
            'expiration_time': expiration_time
        }


    ###
    # It authorizes the token which contains the user identity.
    # This token (or ott-token) has a very short life and
    #   it has to be used immediately after the generation.
    # It's supposed to be used from third-party apps
    #   to get the ability to generate auth token independently.
    #
    # @param string $token
    # @return mixed
    ###
    @staticmethod
    def verify_ott_auth_token(email, token):
        if model_token_banlist.is_banned(token) is True:
            return False
        m = User.find_by_email(email)
        if m is None or m.nonce is None:
            return None
        s = Serializer(m.nonce)
        try:
            data = s.loads(token)
            m = db.session.query(User).get(data['id'])
            m_refresh_token = User.refresh_token(email, token)
            m.__dict__['token'] = m_refresh_token['token']
            m.__dict__['expiration_time'] = m_refresh_token['expiration_time']
            model_token_banlist.add(service_timestamp_get(), token)
            return m.__dict__
        except SignatureExpired:
            return False
        except BadSignature:
            return False


    ###
    # @param integer $id
    # @return object
    ###
    @staticmethod
    def find_by_id(id):
        return db.session.query(User).get(id)


    ###
    # @param string $email
    # @return object
    ###
    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()


    ###
    # @param string $email
    # @param string $token
    # @return mixed
    ###
    @staticmethod
    def verify_auth_token(email, token):
        if model_token_banlist.is_banned(token) is True:
            return False
        m = User.find_by_email(email)
        if m is None or m.nonce is None:
            return None
        s = Serializer(m.nonce)
        try:
            data = s.loads(token)
            m = db.session.query(User).get(data['id'])
            return m.__dict__
        except SignatureExpired:
            return False
        except BadSignature:
            return False


    ###
    # @param integer $id
    # @param string $email
    # @return boolean
    ###
    @staticmethod
    def update_email_by_id(id, email):
        now = service_timestamp_get()
        m = User.find_by_id(id)
        if m is None:
            return m
        try:
            model_history.add_by_user_id(id, 'email', m.email)
            m.last_update_date = now
            m.email = email
            m.is_active = False
            db.session.commit()
            db.session.close()
            return True
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # @param integer $id
    # @param string $old_password
    # @param string $new_password
    # @return boolean
    ###
    @staticmethod
    def update_password_by_id(id, old_password, new_password):
        now = service_timestamp_get()
        m = User.find_by_id(id)
        if m is None:
           return m
        if User.verify_password(old_password, m.password) is False:
            _(406, 'The old_password is invalid', stop=True)
        try:
            model_history.add_by_user_id(id, 'password', m.password)
            m.last_update_date = now
            m.password = User.password_hash(new_password)
            #m.is_active = False
            db.session.commit()
            db.session.close()
            return True
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # As a step of the password lost journey if the provided email exists
    #   it generates and returns a token.
    # The returning token can be used to reset the password.
    #
    # @param string $email
    # @return string
    @staticmethod
    def is_valid(email):
        m = User.find_by_email(email)
        if m is None:
            return False
        else:
            expires_in = config_app().data['token_expires_after_seconds']
            s = Serializer(config_app().data['secret_key'], expires_in=expires_in)
            token = s.dumps({'id': m.id})
            return token.decode('ascii')


    ###
    # A simple password generator with a predefined entropy.
    #
    # @param boolean $letters default True
    # @param boolean $punctuation default True
    # @param boolean $digits default True
    # @param array $_range default [12, 16]
    # @return string
    ###
    @staticmethod
    def generate_password(letters=True, punctuation=True, digits=True, _range=[12, 16]):
        chars = ''
        if letters:
            chars += string.ascii_letters
        if punctuation:
            chars += string.punctuation
        if digits:
            chars += string.digits
        return "" . join(choice(chars) for x in range(randint(_range[0], _range[1])))


    ###
    # As last step of the password lost journey if the user exists
    #   it adds to the user history the current password
    #   and updates it with a new predefined one,
    #   then it encodes and returns the new password.
    #
    # @param string $token
    # @return mixed
    ###
    @staticmethod
    def reset_password(token):
        now = service_timestamp_get()
        s = Serializer(config_app().data['secret_key'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        m = db.session.query(User).get(data['id'])
        if m is None:
            return m
        try:
            model_history.add_by_user_id(m.id, 'password', m.password)
            m.last_update_date = now
            new_password = User.generate_password()
            print('New password has been generated', new_password)
            m.password = User.password_hash(new_password)
            db.session.commit()
            db.session.close()
            return str(base64.b64encode(bytes(new_password, "utf-8")))[1:]
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # @param string $email
    # @param string $token
    # @param string $stripe_id
    # @return boolean
    ###
    @staticmethod
    def set_stripe_id(email, token, stripe_id):
        attrs = User.verify_auth_token(email, token)
        if attrs is False or attrs is None or attrs['email'] != email:
            return None
        m = User.find_by_email(email)
        if m is None:
            return m
        if m.stripe_id is not None:
            return False
        try:
            m.stripe_id = stripe_id
            db.session.commit()
            db.session.close()
            return True
        except BaseException as e:
            _(500, str(e))
            return False


    ###
    # Logout the user destroying the nonce and
    #   invalidating any active token.
    #
    # @param integer $id
    # @return boolean
    ###
    @staticmethod
    def logout(id):
        m = User.find_by_id(id)
        if m is None:
            return False
        try:
            m.nonce = None
            db.session.commit()
            return True
        except BaseException as e:
            _(500, str(e))
            return False
