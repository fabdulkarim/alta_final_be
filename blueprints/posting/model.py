from blueprints import db
from flask_restful import fields, inputs

class TopLevels(db.Model):
    __tablename__ = "top_level"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    #content type -- either article or question
    content_type = db.Column(db.String(30), nullable=False) 
    html_content = db.Column(db.Text, nullable=False)
    banner_photo_url = db.Column(db.String(255))
    views = db.Column(db.Integer, nullable=False)
    #status should merged into one? 0 - normal, 1 - closed, 2 - deleted?
    # deleted = db.Column(db.Boolean, nullable=False)
    # closed = db.Column(db.Boolean, nullable=False)
    content_status = db.Column(db.SmallInteger, nullable=False)
    point = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())


    #sementara, html_content di output dalam bentuk string
    response_fields = {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'title': fields.String,
        'content_type': fields.String,
        'html_content': fields.String,
        'banner_photo_url': fields.String,
        'views': fields.Integer,
        'content_status': fields.Integer,
        'point': fields.Integer,
        'created_at': fields.String,
        'updated_at': fields.String
    }

    def __init__(self, user_id, title, content_type, html_content, **kwargs):
        self.user_id = user_id
        self.title = title
        self.content_type = content_type
        self.html_content = html_content
        self.views = 0
        self.content_status = 0
        self.point = 0
        if 'banner_photo_url' in kwargs:
            self.banner_photo_url = kwargs.get("banner_photo_url")

    def __repr__(self):
        return '<Top Level %r>' % self.title


