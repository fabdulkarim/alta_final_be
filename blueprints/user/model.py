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

class UsersDetail(db.Model):
    __tablename__ = "user_detail"
    user_detail_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship("Users", backref=db.backref("user", uselist=False))
    
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    job_title = db.Column(db.String(255))
    photo_url = db.Column(db.String(255))
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    response_fields = {
        'first_name': fields.String,
        'last_name': fields.String,
        'job_title': fields.String,
        'photo_url': fields.String,
        'deleted': fields.Boolean,
        'created_at': fields.String,
        'updated_at': fields.String
    }

    complete_response_fields = {
        'username': fields.String,
        'email': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
        'job_title': fields.String,
        'photo_url': fields.String
    }

    def __init__(self, user_detail_id, user_id):
        self.deleted = False
        self.user_detail_id = user_detail_id
        self.user_id = user_id

    def __repr__(self):
        return '<Detail %r>' % self.user_detail_id

class UserTags(db.Model):
    __tablename__ = "user_tag"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'), nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __init__(self,user_id,tag_id):
        self.user_id = user_id
        self.tag_id = tag_id
        self.deleted = False

    def __repr__(self):
        return '<User Tags %r>' % self.id
