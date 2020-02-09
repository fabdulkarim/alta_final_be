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



# class PostingTags(db.Model):
class SecondLevels(db.Model):
    __tablename__ = "second_level"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('top_level.id'), nullable=False)
    #no title
    #content type -- either comment or answer
    content_type = db.Column(db.String(30), nullable=False) 
    html_content = db.Column(db.Text, nullable=False)
    #no banner
    #no views
    # status should merged into one? 0 - normal, 2 - deleted? should c/a be deletable?
    # deleted = db.Column(db.Boolean, nullable=False)
    # closed = db.Column(db.Boolean, nullable=False)
    content_status = db.Column(db.SmallInteger, nullable=False)
    point = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    #editable?
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())



    #sementara, html_content di output dalam bentuk string
    response_fields = {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'parent_id': fields.Integer,
        'content_type': fields.String,
        'html_content': fields.String,
        'content_status': fields.Integer,
        'point': fields.Integer,
        'created_at': fields.String,
        'updated_at': fields.String
    }

    def __init__(self, user_id, parent_id, content_type, html_content):
        self.user_id = user_id
        self.parent_id = parent_id
        self.content_type = content_type
        self.html_content = html_content
        self.content_status = 0
        self.point = 0
        #no kwargs for banner

    def __repr__(self):
        return '<Second Level %r>' % self.title

class TopLevelTags(db.Model):
    __tablename__ = "tl_tag"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tl_id = db.Column(db.Integer, db.ForeignKey('top_level.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'), nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __init__(self, tl_id, tag_id):
        self.tl_id = tl_id
        self.tag_id = tag_id
        self.deleted = False

    def __repr__(self):
        return '<TL Tags %r>' % self.id