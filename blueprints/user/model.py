from blueprints import db
from flask_restful import fields, inputs

class Users(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    response_fields = {
        'user_id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'deleted': fields.Boolean,
        'created_at': fields.String,
        'updated_at': fields.String
    }

    jwt_claims_fields = {
        'user_id': fields.Integer,
    }

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.deleted = False

    def __repr__(self):
        return '<User %r>' % self.user_id