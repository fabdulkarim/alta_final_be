from blueprints import db
from flask_restful import fields, inputs

class TopLevels(db.Model):
    __tablename__ = "top_level"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    title = db.Column(db.String(255))
    #content type -- either article or question
    content_type = db.Column(db.String(30)) 
    html_content = db.Column(db.Text)
    banner_photo_url = db.Column(db.String(255))
    views = db.Column(db.Integer)
    #status should merged into one? 0 - normal 1 - closed 2 - deleted?
    # deleted = db.Column(db.Boolean, nullable=False)
    # closed = db.Column(db.Boolean, nullable=False)
    content_status = db.Column(db.Integer(1))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())