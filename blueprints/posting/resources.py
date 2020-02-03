from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from datetime import datetime

from .model import TopLevels
from blueprints import db, app

from . import *

bp_posting = Blueprint('posting', __name__)
api = Api(bp_posting)

#CR features for top-level posting (no param)
class TopLevelCR(Resource):
    #getall, open for all (visitor-level)
    def get(self):
        qry = TopLevels.query.filter_by(content_status=0)
        # qry.all()

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404, {'Content-Type':'application/json'}

        #modify later to add pagination and filtering

        rows = []
        for que in qry:
            rows.append(marshal(que, TopLevels.response_fields))

        return rows, 200, {'Content-Type':'application/json'}

    @jwt_required
    @user_required
    def post(self):

        #get argument from input
        parser = reqparse.RequestParser()
        parser.add_argument('title', location='json', required=True)
        parser.add_argument('content_type', location='json', required=True)
        parser.add_argument('html_content', location='json', required=True)
        parser.add_argument('banner_photo_url', location='json')
        
        args = parser.parse_args()

        #get user_id for posting purposes
        id = get_jwt_claims()['user_id']

        if (args['content_type']=='article') and (args['banner_photo_url']):
            top_level = TopLevels(id,args['title'],args['content_type'],args['html_content'],banner_photo_url=args['banner_photo_url'])
        else:
            top_level = TopLevels(id,args['title'],args['content_type'],args['html_content'])

        db.session.add(top_level)
        db.session.commit()

        return marshal(top_level, TopLevels.response_fields), 200, {'Content-Type':'application/json'}

api.add_resource(TopLevelCR,'/toplevel')