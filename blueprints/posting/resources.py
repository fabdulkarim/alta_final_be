from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from datetime import datetime

from .model import TopLevels
from ..user.model import Users, UsersDetail
from blueprints import db, app

from . import *

bp_posting = Blueprint('posting', __name__)
api = Api(bp_posting)

#CR features for top-level posting (no param)
class TopLevelCR(Resource):
    #getall, open for all (visitor-level)
    def get(self):
        #hanya tampilkan konten 0 -- open, bukan 1 -- closed, atau 2 -- deleted
        qry = TopLevels.query.filter_by(content_status=0)
        # qry.all()

        # add search (by keyword, tags), filter tipe dan pagination
        parser =reqparse.RequestParser()
        parser.add_argument("keyword", location="args")
        parser.add_argument("tags", location="args")
        parser.add_argument("content_type", location="args")
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()


        if qry is None:
            return {'status': 'NOT_FOUND'}, 404, {'Content-Type':'application/json'}

        #modify later to add pagination and filtering

        #pagination

        offset = (args['p']-1)*args['rp']
        qry = qry.limit(args['rp']).offset(offset)

        #added user/author detail for FE request
        rows = []
        for que in qry:
            check_f_name = UsersDetail.query.filter_by(user_id=que.user_id).first_name
            check_l_name = UsersDetail.query.filter_by(user_id=que.user_id).last_name
            check_photo = UsersDetail.query.filter_by(user_id=que.user_id).photo_url
            if (check_f_name == None) & (check_l_name == None):
                username = Users.query.get(que.user_id).username
            elif (check_l_name == None):
                username = check_f_name
            elif (check_f_name == None):
                username = check_l_name
            else:
                username = check_f_name + " " + check_l_name
            
            if check_photo == None:
                photo_url = "null"
            else:
                photo_url = check_photo

            rows.append({'username':username,'photo_url':photo_url,'posting_detail':marshal(que, TopLevels.response_fields)})

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

<<<<<<< Updated upstream
api.add_resource(TopLevelCR,'/toplevel')
=======

class TopLevelRUD(Resource):
    #public get by id
    def get(self, id):
        qry = TopLevels.query.filter(TopLevels.content_status.in_((0,1)))
        qry = qry.filter_by(id=id)

        qry = qry.first()


        if qry is None:
            return {'status': 'NOT_FOUND'}, 404, {'Content-Type': 'application/json'}

        #add to views in posting table -- nanti pakai put saja
        ##after discussion with lead (mas Lian), kita nambah view lewat sini saja
        qry.views += 1
        db.session.commit()

        return marshal(qry, TopLevels.response_fields), 200, {'Content-Type':'application/json'}

    @jwt_required
    def put(self,id):

        qry = TopLevels.query.filter_by(id=id)

        #determine admin or user?
        


api.add_resource(TopLevelCR,'/toplevel')
api.add_resource(TopLevelRUD, '/toplevel/<int:id>')
>>>>>>> Stashed changes
