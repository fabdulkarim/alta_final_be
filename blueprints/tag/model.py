from blueprints import db
from flask_restful import fields, inputs

class Tags(db.Model):
    __tablename__ = "tag"
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())
    deleted = db.Column(db.Boolean, nullable=False)

    photo_url = db.Column(db.String(255))
    total_follower = db.Column(db.Integer)

    public_response_fields = {
        'name': fields.String,
        'photo_url': fields.String,
        'total_follower': fields.Integer
    }

    response_fields = {
        'tag_id': fields.Integer
        'name': fields.String,
        'photo_url': fields.String,
        'total_follower': fields.Integer
        'created_at': fields.String
        'updated_at': fields.String
        'deleted': fields.Boolean
    }

    def __init__(self, name, photo_url):
        self.name = name
        self.photo_url = photo_url
        self.total_follower = 0
        self.deleted = False

    def __repr__(self):
        return '<Tag %r>' % self.name