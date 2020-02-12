##hardcopy from fadhil's portofolio
import hashlib

from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from datetime import datetime

from .model import Users, UsersDetail, UserTags
from .mini_profile import create_mini_profile
from ..tag.model import Tags
from ..posting.model import TopLevels, SecondLevels
from ..posting.tl_tags import tl_tags_return
from blueprints import db, app

#using separate scripts
from .public_get_u_by_id_posting import PublicWildcardResource

from . import *

bp_user = Blueprint('user', __name__)
api = Api(bp_user)


#CRUD untuk user, hanya bisa diakses admin
#sesuai dengan rancangan final project, Admin hanya get all dan delete
class AdminUserEdit(Resource):
    #changed to put to enable open block/undelete
    @jwt_required
    @admin_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('deleted', location='json', required=True)

        args = parser.parse_args()

        qry = Users.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        qry.deleted = bool(args['deleted'])
        qry.updated_at = db.func.now()
        db.session.commit()

        return marshal(qry, Users.response_fields), 200
    
    @jwt_required
    @admin_required
    def get(self):
        qry = Users.query

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        rows = []
        for que in qry:
            user_row = marshal(que,Users.response_fields)
            qry2 = UsersDetail.query.get(que.user_id)
            # print(user_row)
            user_row['user_detail'] = marshal(qry2, UsersDetail.response_fields) #?
            rows.append(user_row)

        return rows, 200


#signup, terpisah
class UserSignUp(Resource):

    def post(self):

        policy = PasswordPolicy.from_names(
            length=6
        )

        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        
        args = parser.parse_args()

        validation = policy.test(args['password'])

        if validation == []:
            password_digest = hashlib.md5(args['password'].encode()).hexdigest()
            
            user = Users(args['username'], args['email'], password_digest)

            try:
                db.session.add(user)

                ##adding new user detail/info
                #should be inside try, to catch duplicate error and produce 409s
                user_id = Users.query.filter_by(username=args['username']).first().user_id
                user_detail = UsersDetail(user_id,user_id)
                db.session.add(user_detail)
            except:
                return {'status':'failed','message':'conflicting database'}, 409, {'Content-Type':'application/json'}
            app.logger.debug('DEBUG : %s', user)

            db.session.commit()

            return marshal(user, Users.response_fields), 200, {'Content-Type': 'application/json'}
        return {'status': 'failed', 'result': str(validation)}, 400, {'Content-Type': 'application/json'}



    def options(self):
        return {}, 200

##New separated class for different endpoint, kita geser juga edit ke /me karena cuma user
## yang bisa ngedit data sendiri
class UserSelf(Resource):

    #fitur perbarui data
    @jwt_required
    @user_required
    def put(self):
        policy = PasswordPolicy.from_names(
            length=6
        )

        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json')
        parser.add_argument('password_new', location='json')
        
        #added input for user_detail, all nullable
        parser.add_argument('first_name', location='json')
        parser.add_argument('last_name', location='json')
        parser.add_argument('job_title', location='json')
        parser.add_argument('photo_url', location='json')
        #parsing json for array/list?
        ##changed to required. putting [] means (soft) deleting all tags for user
        ###FINAL: have to be inputed always. but cant be made required
        ### [] returned None still counted as none
        parser.add_argument('tags', location='json', action='append')

        args = parser.parse_args()

        id = get_jwt_claims()['user_id']

        qry = Users.query.get(id)
        #add query for user_detail
        qry2 = UsersDetail.query.get(id)

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404, {'Content-Type': 'application/json'}
        
        if qry2 is None:
            return {'status': 'DETAIL_NOT_FOUND'}, 404, {'Content-Type': 'application/json'}

        #became conditional, if inputed password
        if args['password']:
            #added hashing to check old_password
            old_password_digest = hashlib.md5(args['password'].encode()).hexdigest()
            validation = policy.test(args['password_new'])

            #safeguard against different old password dan method ganti password (base user general)
            if old_password_digest != qry.password:
                return {'status': 'failed', 'result': 'wrong password'}, 401, {'Content-Type': 'application/json'}

            if validation != []:
                return {'status': 'failed', 'result': str(validation)}, 401, {'Content-Type': 'application/json'}

            password_digest = hashlib.md5(args['password_new'].encode()).hexdigest()
            qry.password = password_digest

        qry.username = args['username']
        qry.email = args['email']
        
        qry.updated_at = db.func.now()

        ##adding user detail edit, if not empty, change record

        if args['first_name']:
            qry2.first_name = args['first_name']
      
        if args['last_name']:
            qry2.last_name = args['last_name']

        if args['job_title']:
            qry2.job_title = args['job_title']

        if args['photo_url']:
            qry2.photo_url = args['photo_url']

        #processing input user-tags and UT.query
        qry3_all = UserTags.query.filter_by(user_id=id)
        qry3 = qry3_all.filter_by(deleted=False)
        
        ##harus dalam bentuk tag list
        ##butuh all() atau ngga

        #list of dbs tag, in their names, have to be constructed first
        #redundancy for rewriting existing to undelete
        db_tag_list = []
        db_tag_list_all = []
        for que in qry3_all:
            qry5 = Tags.query.get(que.tag_id)
            if que in qry3:
                db_tag_list.append(qry5.name)
            db_tag_list_all.append(qry5.name)

        #operation to determine input_only tag list and db only tag list
        #both will be used to append and delete usertag table

        ##error, safeguard against empty list
        ###reqparse if keyword doesnt exist
        ####[mas Kobar] urusin aja di FEnya. ntar bingung sendiri
        # if 'tags' in args:
        #     print("Masuk boskuh")
        if args['tags'] is None:
            input_set = set()
        else:
            input_set = set(args['tags'])

        input_only = input_set - set(db_tag_list)
        db_only = set(db_tag_list) - input_set

        #two times iteration, both by names
        for input_iter in input_only:
            #add safeguard for re-adding deleted tags
            #get tag_id first
            qry4 = Tags.query.filter_by(name=input_iter)
            qry4 = qry4.first()
            tag_id = qry4.tag_id


            #rewrite deleted to false if existing
            if input_iter in db_tag_list_all:
                #get from qry all, reactivate
                qry_reactivate = qry3_all.filter_by(tag_id=tag_id).first()
                qry_reactivate.deleted = False
            #kondisi mint
            else:
            #qry4 used for search for tag_id first
                user_tag = UserTags(id, tag_id)

                db.session.add(user_tag)
        
        for db_iter in db_only:
            qry4 = Tags.query.filter_by(name=db_iter)
            qry4 = qry4.first()
            tag_id = qry4.tag_id
            #qry3 is a user-filtered usertag
            #do a second filter for tag_id
            qry6 = qry3.filter_by(tag_id=tag_id).first()
            #set delete to true
            qry6.deleted = True
            qry6.updated_at = db.func.now()

        qry2.updated_at = db.func.now()      

        #all commit
        db.session.commit()

        #get list of user tags, turn into list of names
        qry7 = UserTags.query.filter_by(user_id=id).filter_by(deleted=False)
        db_tag_list_final = []
        for que in qry7:
            qry5 = Tags.query.get(que.tag_id)
            db_tag_list_final.append(qry5.name)

        user_data = marshal(qry, Users.response_fields)
        user_detail_data = marshal(qry2, UsersDetail.response_fields)
        user_tag_data = db_tag_list_final

        return {'user_data':user_data, 'user_detail_data':user_detail_data, 'user_tag_data':user_tag_data}, 200, {'Content-Type': 'application/json'}
        

    @jwt_required
    @user_required
    def get(self):
        id = get_jwt_claims()['user_id']

        qry = Users.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        #add get detail and tag data

        qry2 = UsersDetail.query.get(id)
        #no none: show filter field empty
        
        #get list of user tags, turn into list of names
        qry3 = UserTags.query.filter_by(user_id=id).filter_by(deleted=False)
        db_tag_list_final = []
        for que in qry3:
            qry4 = Tags.query.get(que.tag_id)
            db_tag_list_final.append(qry4.name)

        user_data = marshal(qry, Users.response_fields)
        user_detail_data = marshal(qry2, UsersDetail.response_fields)
        user_tag_data = db_tag_list_final

        return {'user_data':user_data, 'user_detail_data':user_detail_data, 'user_tag_data':user_tag_data}, 200, {'Content-Type': 'application/json'}

    def options(self):
        return {}, 200

class UserSelfPostingArticle(Resource):
    #CORS
    def options(self):
        return {}, 200
    
    @jwt_required
    @user_required
    def get(self):
        id = get_jwt_claims()['user_id']

        parser =reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        qry = TopLevels.query.filter_by(user_id=id).filter_by(content_type='article')

        qry = qry.order_by(desc(TopLevels.created_at))

        #prepare query info so similar to home GET
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

            row_posting_detail = marshal(que, TopLevels.response_fields)
            #adding tags
            row_posting_detail['tags'] = tl_tags_return(que.id)

            sl_amount = SecondLevels.query.filter_by(parent_id=que.id).count()

            row_posting_detail['sl_amount'] = sl_amount

            user_data = create_mini_profile(id)

            rows.append({'user_data':user_data,'posting_detail':row_posting_detail})

        return {'query_info': query_info,'query_data':rows}, 200, {'Content-Type': 'application/json'}

#HARD COPY FROM ABOVE
class UserSelfPostingQuestion(Resource):
    #CORS
    def options(self):
        return {}, 200
    
    @jwt_required
    @user_required
    def get(self):
        id = get_jwt_claims()['user_id']

        parser =reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        qry = TopLevels.query.filter_by(user_id=id).filter_by(content_type='question')

        qry = qry.order_by(desc(TopLevels.created_at))

        #prepare query info so similar to home GET
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
            
            row_posting_detail = marshal(que, TopLevels.response_fields)
            #adding tags
            row_posting_detail['tags'] = tl_tags_return(que.id)

            sl_amount = SecondLevels.query.filter_by(parent_id=que.id).count()

            row_posting_detail['sl_amount'] = sl_amount

            user_data = create_mini_profile(id)

            rows.append({'user_data':user_data,'posting_detail':row_posting_detail})

        return {'query_info': query_info,'query_data':rows}, 200, {'Content-Type': 'application/json'}

class UserSelfPostingAnswer(Resource):
    #CORS
    def options(self):
        return {}, 200
    
    @jwt_required
    @user_required
    def get(self):
        id = get_jwt_claims()['user_id']

        parser =reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        qry = SecondLevels.query.filter_by(user_id=id).filter_by(content_type='answer')

        qry = qry.order_by(desc(SecondLevels.created_at))

        #prepare query info so similar to home GET
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
            qry2 = TopLevels.query.get(que.parent_id)

            user_data = create_mini_profile(id)

            marshal_parent = marshal(qry2, TopLevels.response_fields)

            marshal_parent['user_data'] = create_mini_profile(qry2.user_id)

            sl_amount = SecondLevels.query.filter_by(parent_id=qry2.id).count()

            marshal_parent['sl_amount'] = sl_amount
            
            tags = tl_tags_return(qry2.id)
            
            marshal_parent['tags'] = tags
            rows.append({'user_data':user_data,'posting_detail':marshal(que, SecondLevels.response_fields),'parent_detail':marshal_parent})

        second_data = {
            'second_info': {
                'sl_amount': len(rows)
            },
            'second_detail_list': rows
        }

        return {'query_info': query_info,'second_data':second_data}, 200, {'Content-Type': 'application/json'}

class UserSelfPostingComment(Resource):
    #CORS
    def options(self):
        return {}, 200
    
    @jwt_required
    @user_required
    def get(self):
        id = get_jwt_claims()['user_id']

        parser =reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        qry = SecondLevels.query.filter_by(user_id=id).filter_by(content_type='comment')

        qry = qry.order_by(desc(SecondLevels.created_at))

        #prepare query info so similar to home GET
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
            qry2 = TopLevels.query.get(que.parent_id)

            user_data = create_mini_profile(id)

            marshal_parent = marshal(qry2, TopLevels.response_fields)

            marshal_parent['user_data'] = create_mini_profile(qry2.user_id)

            sl_amount = SecondLevels.query.filter_by(parent_id=qry2.id).count()

            marshal_parent['sl_amount'] = sl_amount
            
            tags = tl_tags_return(qry2.id)
            
            marshal_parent['tags'] = tags
            rows.append({'user_data':user_data,'posting_detail':marshal(que, SecondLevels.response_fields),'parent_detail':marshal_parent})

        second_data = {
            'second_info': {
                'sl_amount': len(rows)
            },
            'second_detail_list': rows
        }

        return {'query_info': query_info,'second_data':second_data}, 200, {'Content-Type': 'application/json'}

#separated into different class because different purpose (public access to user)
class PublicResources(Resource):
    
    def get(self, id):
        #public, not by get
        #qry = Users.query.get(id)
        
        qry = Users.query.filter_by(deleted=False).filter_by(user_id=id)

        qry = qry.first()

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        qry2 = UsersDetail.query.get(id)
        #no none: show filter field empty
        
        #get list of user tags, turn into list of names
        qry3 = UserTags.query.filter_by(user_id=id).filter_by(deleted=False)
        db_tag_list_final = []
        for que in qry3:
            qry4 = Tags.query.get(que.tag_id)
            db_tag_list_final.append(qry4.name)

        user_data = marshal(qry, Users.response_fields)
        user_detail_data = marshal(qry2, UsersDetail.response_fields)
        user_tag_data = db_tag_list_final

        return {'user_data':user_data, 'user_detail_data':user_detail_data, 'user_tag_data':user_tag_data}, 200, {'Content-Type': 'application/json'}

        # return marshal(qry, Users.response_fields), 200

    def options(self, **kwargs):
        return {}, 200


class PublicResourcesPosting(Resource):
    def options(self, **kwargs):
        return {}, 200

    def get(self, id, content_type):

        parser = reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=15)
        args = parser.parse_args()

        if content_type not in ['article','question','answer', 'comment']:
            return {'status':'URL not found'}, 404, {'Content-Type': 'application/json'}

        user_id = id
        c_type = content_type

        result = PublicWildcardResource(user_id,c_type, args['p'],args['rp'])

        if result == []:
            return {'status':'query not found'}, 404, {'Content-Type': 'application/json'}

        return result, 200, {'Content-Type': 'application/json'}

api.add_resource(UserSignUp, '')
api.add_resource(UserSelf, '/me')

#adding postingan group
api.add_resource(UserSelfPostingArticle,'/me/article')
api.add_resource(UserSelfPostingQuestion,'/me/question')
api.add_resource(UserSelfPostingAnswer,'/me/answer')
api.add_resource(UserSelfPostingComment,'/me/comment')

#all wildcards should be in lower section
#apparently jwt in higher places can cause 401 w/o prompt
api.add_resource(PublicResources, '/<int:id>')
api.add_resource(PublicResourcesPosting, '/<int:id>/<string:content_type>')

##adding public resources (one class pls)
api.add_resource(AdminUserEdit, '', '/<int:id>')
