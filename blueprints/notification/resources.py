from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from .model import MessageGroups, UserGroups, MessageReceipts, Messages
from .group_function import create_group

from blueprints import db

bp_nofity = Blueprint('notify', __name__)
api = Api(bp_nofity)

class UserJoinGroup(Resource):
    def options(self, *args, **kwargs):
        return {}, 200

    #by tl id?
    @jwt_required
    @user_required
    def post(self, tl_id):

        user_id = get_jwt_claims()['user_id']

        qry = Groups.query.filter_by(group_type='question').filter_by(owner_id=tl_id)
        qry = qry.first()

        if qry is None:
            g_id = create_group('question',tl_id)
        else:
            g_id = qry.id
        
        #check existing
        qry2 = UserGroups.query.filter_by(user_id=user_id).filter_by(group_id=g_id)
        if qry2 is None:
            user_group = UserGroups(user_id,g_id)
            db.session.add(user_group)
        else:
            qry2.first().deleted = False

        db.session.commit()

        return {}, 200

# class SendMessage(Resource):
#     def options(self):
#         return {}, 200

#     def 
        
class UserNotification(Resource):
    def options(self, *args, **kwargs):
        return {}, 200

    @jwt_required
    @user_required
    def get(self):
        user_id = get_jwt_claims()['user_id']

        qry = MessageReceipts.query.filter_by(recipient_uid=user_id)

        rows = []
        
        for que in qry:
            notif_row = marshal(que,MessageReceipts.response_fields)
            msg_qry = Messages.query.get(que.message_id).message_content
            notif_row['message_content'] = msg_qry
            rows.append(notif_row)

        return rows, 200

    @jwt_required
    def put(self,id):
        user_id = get_jwt_claims()['user_id']

        qry = MessageReceipts.query.filter_by(recipient_uid=user_id).filter_by(id=id)

        #if 404

        parser =reqparse.RequestParser()
        parser.add_argument("is_read", location="json")
        parser.add_argument('deleted',location='json')
        args = parser.parse_args()

        qry.is_read = args['is_read']
        qry.deleted = args['deleted']

        db.session.commit()

        return marshal(qry, MessageReceipts.response_fields), 200

api.add_resource(UserNotification, '')