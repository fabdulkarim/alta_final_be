from blueprints import db
from flask_restful import fields, inputs

class Points(db.Model):
    __tablename__ = 'point'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    locator_id = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(30), nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    response_fields = {
        'user_id': fields.Integer,
        'locator_id': fields.Integer,
        'content_type': fields.String,
        'deleted': fields.Boolean,
        'created_at': fields.String,
        'updated_at': fields.String
    }

    def __init__(self, user_id, locator_id, content_type):
        self.user_id = user_id
        self.locator_id = locator_id
        self.content_type = content_type
        self.deleted = False

    def __repr__(self):
        return '<Point %r -- %r-%r; deleted: %r>' % (self.user_id, self.content_type, self.locator_id, self.deleted)