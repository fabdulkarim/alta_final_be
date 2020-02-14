from blueprints import db
from flask_restful import fields, inputs

class MessageGroups(db.Model):
    __tablename__ = "msg_group"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_type = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __init__(self, group_type, owner_id):
        self.group_type = group_type
        self.owner_id = owner_id
        self.deleted = False

class UserGroups(db.Model):
    __tablename__ = "user_group"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('msg_group.id'), nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id
        self.deleted = False

class Messages(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_uid = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    # message_type = db.Column(db.String(30))
    tl_id = db.Column(db.Integer, db.ForeignKey('top_level.id'))
    sl_id = db.Column(db.Integer, db.ForeignKey('second_level.id'))
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __init__(self, author_uid, message_content, **kwargs):
        self.author_uid = author_uid
        self.message_content = message_content
        self.deleted = False
        if set(['tl_id','sl_id']).issubset(kwargs):
            # self.message_type = kwargs.get('message_type')
            self.tl_id = kwargs.get('tl_id')
            self.sl_id = kwargs.get('sl_id')

class MessageReceipts(db.Model):
    __tablename__ = "message_receipt"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipient_uid = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_gid = db.Column(db.Integer, db.ForeignKey('msg_group.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __init__(self, recepient_uid, recepient_gid, message_id):
        self.recipient_uid = recepient_uid
        self.recipient_gid = recepient_gid
        self.message_id = message_id
        self.is_read = False
        self.deleted = False

    response_fields = {
        'id': fields.Integer,
        'recipient_uid': fields.Integer,
        'recipient_gid': fields.Integer,
        'message_id': fields.Integer,
        'is_read': fields.Boolean,
        'deleted': fields.Boolean,
        'created_at': fields.String,
        'updated_at': fields.String
    }