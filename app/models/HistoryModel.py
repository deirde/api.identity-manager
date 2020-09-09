from app import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.services.TimestampService import get_or_ko as service_timestamp_get


class History(db.Model):

    __bind_key__ = 'mysql'
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    insert_date = db.Column(db.Integer)
    user__id = db.Column(db.Integer)
    meta = db.Column(db.String(64))
    value = db.Column(db.String(155))

    def __init__(self, insert_date, user__id, meta, value):
        self.insert_date = insert_date
        self.user__id = user__id
        self.meta = meta
        self.value = value

    @property
    def __repr__(self):
        return '<ID %r>' % self.id

    @staticmethod
    def add_by_user_id(id, meta, value):
        now = service_timestamp_get()
        try:
            m = History(now, id, meta, value)
            db.session.add(m)
            db.session.commit()
            db.session.close()
            return True
        except:
            return False
