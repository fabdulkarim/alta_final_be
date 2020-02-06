from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc, or_

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
        parser.add_argument("content_type", location="args", choices=('article','question'))
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()


        #modify later to add pagination and filtering
        #content_type filtering
        if args['content_type']:
            qry = qry.filter_by(content_type=args['content_type'])

        #search feature
        #exact search in HTML content first
        #combo wildcard search also in title
        if args['keyword']:
            qry = qry.filter(or_(
                        TopLevels.title.like("%"+args['keyword']+"%"),\
                        TopLevels.html_content.like("%"+args['keyword']+"%")
                    )
                )

        #count qry result
        total_result = len(qry.all())
        if (total_result%args['rp'] != 0) | (total_result == 0):
            total_pages = int(total_result/args['rp']) + 1
        else:
            total_pages = int(total_result/args['rp'])


        #pagination

        offset = (args['p']-1)*args['rp']
        qry = qry.limit(args['rp']).offset(offset)

        query_info = {
            'total_result': total_result,
            'total_pages': total_pages,
            'page_number': args['p'],
            'result_per_pages': args['rp']
        }

        #get ready to move NONE to lower part
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404, {'Content-Type':'application/json'}

        #added user/author detail for FE request
        rows = []
        for que in qry:
            check_f_name = UsersDetail.query.filter_by(user_id=que.user_id).first().first_name
            check_l_name = UsersDetail.query.filter_by(user_id=que.user_id).first().last_name
            check_photo = UsersDetail.query.filter_by(user_id=que.user_id).first().photo_url
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

            user_data = {
                'username': username,
                'photo_url': photo_url
            }

            rows.append({'user_data':user_data,'posting_detail':marshal(que, TopLevels.response_fields)})

        return {'query_info':query_info,'query_data':rows}, 200, {'Content-Type':'application/json'}

    @jwt_required
    @user_required
    def post(self):

        #get argument from input
        parser = reqparse.RequestParser()
        parser.add_argument('title', location='json', required=True)
        parser.add_argument('content_type', location='json', required=True, choices=('article','question'))
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

    def options(self):
        return {}, 200


class TopLevelRUD(Resource):

    def options(self):
        return {}, 200
        
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

        ##adding detail so format stays the same with GET all
        check_f_name = UsersDetail.query.filter_by(user_id=qry.user_id).first().first_name
        check_l_name = UsersDetail.query.filter_by(user_id=qry.user_id).first().last_name
        check_photo = UsersDetail.query.filter_by(user_id=qry.user_id).first().photo_url
        if (check_f_name == None) & (check_l_name == None):
            username = Users.query.get(qry.user_id).username
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

        user_data = {
            'username': username,
            'photo_url': photo_url
        }

        posting_data = {
            'user_data': user_data,
            'posting_detail': marshal(qry, TopLevels.response_fields)
        }

        #second data dikosongin, buat slot komen dan jawaban
        return {'posting_data':posting_data, 'second_data':[]}, 200, {'Content-Type':'application/json'}
        # return marshal(qry, TopLevels.response_fields), 200, {'Content-Type':'application/json'}

    @jwt_required
    def put(self,id):

        qry = TopLevels.query.filter_by(id=id)


        return {'status':'NOT_FOUND','message':'Layanan belum tersedia, mohon maaf'}, 404, {'Content-Type':'application/json'}

        #determine admin or user?
        


api.add_resource(TopLevelCR,'/toplevel')
api.add_resource(TopLevelRUD, '/toplevel/<int:id>')
