from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal

from sqlalchemy import desc

from flask_jwt_extended import jwt_required

from blueprints import db, admin_required
from ..user.model import Users, UsersDetail
from ..user.mini_profile import create_mini_profile
from ..posting.model import TopLevels, TopLevelTags, SecondLevels
from ..posting.tl_tags import tl_tags_return
from ..tag.model import Tags
from .chart import prepare_chart

bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)

class AdminUsersGet(Resource):
    #CORS
    def options(self, *args, **kwargs):
        return {},200


    @jwt_required
    @admin_required
    def get(self):
        qry = Users.query

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        # parser =reqparse.RequestParser()
        # parser.add_argument("p", type=int, location="args", default=1)
        # parser.add_argument("rp", type=int, location="args", default=15)
        # args = parser.parse_args()


        #add sort by time
        qry = qry.order_by(desc(Users.created_at))

        #count qry result
        total_result = len(qry.all())
        # if (total_result%args['rp'] != 0) | (total_result == 0):
        #     total_pages = int(total_result/args['rp']) + 1
        # else:
        #     total_pages = int(total_result/args['rp'])


        #pagination

        # offset = (args['p']-1)*args['rp']
        # qry = qry.limit(args['rp']).offset(offset)

        query_info = {
            'total_result': total_result
        }
        # ,
        #     'total_pages': total_pages,
        #     'page_number': args['p'],
        #     'result_per_pages': args['rp']
        # }

        rows = []
        for que in qry:
            user_row = marshal(que,Users.response_fields)
            qry2 = UsersDetail.query.get(que.user_id)
            # print(user_row)
            user_row['user_detail'] = marshal(qry2, UsersDetail.response_fields) #?
            rows.append(user_row)

        return {'query_info':query_info,'query_data':rows}, 200

class AdminTopLevelsGet(Resource):
    #CORS
    def options(self, *args, **kwargs):
        return {},200, {'Content-Type':'application/json'}

    def get(self, content_type):

        qry = TopLevels.query.filter_by(content_type=content_type)

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        #add sort by time
        qry = qry.order_by(desc(TopLevels.created_at))

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

        rows = []
        for que in qry:
            tl_row = marshal(que, TopLevels.response_fields)
            user_data = create_mini_profile(que.user_id)
            tags = tl_tags_return(que.id)
            tl_row['tags'] = tags
            sl_amount = SecondLevels.query.filter_by(parent_id=que.id).count()
            tl_row['sl_amount'] = sl_amount
            rows.append({'user_data': user_data,'posting_detail':tl_row})

        return {'query_info':query_info,'query_data':rows}, 200, {'Content-Type':'application/json'}

class AdminAnswersGet(Resource):
    #CORS
    def options(self, *args, **kwargs):
        return {},200

    @jwt_required
    @admin_required
    def get(self):

        qry = SecondLevels.query.filter_by(content_type='answer')

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        #add sort by time
        qry = qry.order_by(desc(SecondLevels.created_at))

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

        rows = []
        for que in qry:
            answer_row = marshal(que, SecondLevels.response_fields)
            user_data = UsersDetail.query.filter_by(user_id=que.user_id).first()
            user_data = marshal(user_data, UsersDetail.response_fields)
            user_data['username'] = Users.query.get(que.user_id).username
            answer_row['user_data'] = user_data
            rows.append(answer_row)

        return {'query_info': query_info,'query_data':rows}, 200

#NO PAGINATIONS
class AdminTagsGet(Resource):
    #CORS
    def options(self, *args, **kwargs):
        return {},200, {'Content-Type':'application/json'}
    
    @jwt_required
    @admin_required
    def get(self):
        
        qry = Tags.query

        rows = []
        for que in qry:
            tag_row = marshal(que, Tags.response_fields)
            qry2 = TopLevelTags.query
            qry2 = qry2.filter_by(tag_id=que.tag_id)\
                .filter_by(deleted=False)
            tag_row['tl_tag_count'] = qry2.count()
            rows.append(tag_row)

        return {'query_data':rows},200, {'Content-Type':'application/json'}

class AdminChartGet(Resource):
    #CORS
    def options(self, *args, **kwargs):
        return {},200, {'Content-Type':'application/json'}


    @jwt_required
    @admin_required
    def get(self, data):

        input_list = ['user','article','question','answer']
        pair_list = [{'table':Users,'filter':None},{'table':TopLevels,'filter':'article'},{'table':TopLevels,'filter':'question'},{'table':SecondLevels,'filter':'answer'}]

        if data not in input_list:
            return {'status': 'PATH_NOT_FOUND'}, 404

        idx_to_use = input_list.index(data)

        qry = pair_list[idx_to_use]['table'].query

        if pair_list[idx_to_use]['filter'] != None:
            qry = qry.filter_by(content_type=pair_list[idx_to_use]['filter'])

        # qry = Users.query

        trial_return = prepare_chart(qry)

        return trial_return, 200, {'Content-Type':'application/json'}


api.add_resource(AdminUsersGet,'/user')
api.add_resource(AdminAnswersGet,'/answer')
api.add_resource(AdminTagsGet,'/tag')
api.add_resource(AdminChartGet, '/chart/<string:data>')
api.add_resource(AdminTopLevelsGet,'/<string:content_type>')