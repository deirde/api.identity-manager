from app import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.services.TimestampService import get_or_ko as service_timestamp_get


class Registry(db.Model):


    __bind_key__ = 'mysql'
    __tablename__ = 'registry'


    id = db.Column(db.Integer, primary_key=True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    user__id = db.Column(db.Integer)
    name = db.Column(db.String(155))
    bio = db.Column(db.Text)
    url = db.Column(db.String(128))
    company = db.Column(db.String(128))
    location = db.Column(db.String(256))
    email = db.Column(db.String(128))
    opt_in_email = db.Column(db.Boolean)


    def __init__(self, insert_date, last_update_date, user__id, name='', bio='',
                 url='', company='', location='', email='', opt_in_email=False):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.user__id = user__id
        self.name = name
        self.bio = bio
        self.url = url
        self.company = company
        self.location = location
        self.email = email
        self.opt_in_email = opt_in_email


    @property
    def __repr__(self):
        return '<ID %r>' % self.id


    @staticmethod
    def public_attrs():
        return ['insert_date', 'last_update_date', 'name', 'bio', 'url',
                'company', 'location', 'email', 'opt_in_email']


    ###
    # Only these attributes can be updated externally.
    ###
    @staticmethod
    def safe_attrs():
        return ['name', 'bio', 'url', 'company', 'location', 'email', 'opt_in_email']


    @staticmethod
    def get_data_by_user__id(user__id):
        m = Registry.query.filter_by(user__id=user__id).first()
        response = {}
        for attr in Registry.public_attrs():
            response[attr] = ''
            if m is not None and m.__dict__[attr] is not None:
                response[attr] = m.__dict__[attr]
        return response


    @staticmethod
    def update_registry_by_id(user__id, attrs={}):
        now = service_timestamp_get()
        m = Registry.query.filter_by(user__id=user__id).first()
        if m is None:
            m = Registry(now, now, user__id)
            db.session.add(m)
        try:
            m.last_update_date = now
            for attr, value in attrs:
                attr = attr.lower()
                attr = attr.replace('-', '_')
                if attr in Registry.safe_attrs():
                    if value == "true" or value == "on":
                        value = 1
                    elif value == "false" or value == "off":
                        value = 0
                    setattr(m, attr, value)
            db.session.commit()
            db.session.close()
            return True
        except:
            return False
