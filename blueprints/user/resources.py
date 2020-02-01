##hardcopy from fadhil's portofolio
import hashlib

from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from datetime import datetime

from .model import Users, UsersDetail
from ..tag.model import Tags
from blueprints import db, app

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
        qry = Users.query.all()

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        return marshal(qry, Users.response_fields), 200


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
            except:
                return {'status':'failed','message':'conflicting database'}, 409, {'Content-Type':'application/json'}
            app.logger.debug('DEBUG : %s', user)

            ##adding new user detail/info
            user_id = Users.query.filter_by(username=args['username']).first().user_id
            user_detail = UsersDetail(user_id,user_id)
            db.session.add(user_detail)

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
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('password_new', location='json', required=True)
        
        #added input for user_detail, all nullable
        parser.add_argument('first_name', location='json')
        parser.add_argument('last_name', location='json')
        parser.add_argument('job_title', location='json')
        parser.add_argument('photo_url', location='json')
        #parsing json for array/list?
        parser.add_argument('tags', location='json')

        args = parser.parse_args()

        id = get_jwt_claims()['user_id']

        qry = Users.query.get(id)
        #add query for user_detail
        qry2 = UsersDetail.query.get(id)

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        #added hashing to check old_password
        old_password_digest = hashlib.md5(args['password'].encode()).hexdigest()
        validation = policy.test(args['password_new'])

        #safeguard against different old password dan method ganti password (base user general)
        if old_password_digest != qry.password:
            return {'status': 'failed', 'result': 'wrong password'}, 400, {'Content-Type': 'application/json'}

        if validation != []:
            return {'status': 'failed', 'result': str(validation)}, 400, {'Content-Type': 'application/json'}

        password_digest = hashlib.md5(args['password_new'].encode()).hexdigest()

        qry.username = args['username']
        qry.email = args['email']
        qry.password = password_digest
        qry.updated_at = db.func.now()

        ##adding user detail edit

        

        db.session.commit()

        return marshal(qry, Users.response_fields), 200
        

    @jwt_required
    @user_required
    def get(self):
        id = get_jwt_claims()['user_id']

        qry = Users.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        return marshal(qry, Users.response_fields), 200

    def options(self):
        return {}, 200

#separated into different class because different purpose (public access to user)
class PublicResources(Resource):
    
    def get(self, id):
        #public, not by get
        #qry = Users.query.get(id)
        
        qry = Users.query.filter_by(deleted=False).filter_by(user_id=id)

        qry = qry.first()

        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        return marshal(qry, Users.response_fields), 200

    # def options(self):
    #     return {}, 200

api.add_resource(UserSignUp, '')
api.add_resource(UserSelf, '/me')
#all wildcards should be in lower section
#apparently jwt in higher places can cause 401 w/o prompt
api.add_resource(PublicResources, '/<int:id>')
api.add_resource(AdminUserEdit, '', '/<int:id>')
