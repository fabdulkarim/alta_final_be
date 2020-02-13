import hashlib

from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

from ..user.model import Users, UsersDetail
from blueprints import db

#using g-api-python-client
from google.oauth2 import id_token
from google.auth.transport import requests

#separating google client id from codebase
import os

#for generating database-placeholder password
import random, string

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class CreateTokenResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        if args['username'] == 'admin' and args['password'] == 'admin':
            #gave admin user_id = 0
            token = create_access_token(identity=args['username'], user_claims={'isadmin':True,'user_id':0})
            return {'token': token, 'is_admin':'true'}, 200

        password_digest = hashlib.md5(args['password'].encode()).hexdigest()

        qry = Users.query.filter_by(username=args['username']).filter_by(password=password_digest)

        clientData = qry.first()

        if clientData is not None:
            clientData = marshal(clientData, Users.jwt_claims_fields) 
            clientData['isadmin'] = False
            
            token = create_access_token(identity=args['username'], user_claims=clientData)
            
            return {'token': token}, 200, {'Content-Type': 'application/json'}
        return {'status': 'UNAUTHORIZED', 'message': 'invalid key or secret'}, 401, {'Content-Type': 'application/json'}
    
    ## adding options to facilitate flask-cors
    def options(self):
        return {}, 200, {'Content-Type': 'application/json'}

    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        return claims, 200, {'Content-Type': 'application/json'}

class CreateTokenGoogleResource(Resource):
    def options(self):
        return {}, 200, {'Content-Type': 'application/json'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_token', location='json', required=True)
        args = parser.parse_args()
        
        #id_token check
        CLIENT_ID = os.getenv('G_API_CLIENT_ID')

        try:
            idinfo = id_token.verify_oauth2_token(args['id_token'], requests.Request(), CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError:
            return {'status': 'UNAUTHORIZED', 'message': 'invalid key or secret'}, 401, {'Content-Type': 'application/json'}


        qry = Users.query.filter_by(email=idinfo['email']).first()

        #kondisi hanya jika sudah terdaftar
        if qry is not None:
            clientData = marshal(qry, Users.jwt_claims_fields)
            uname_out = qry.username

        else:
            #prepare placeholder user object
            password_digest_like = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            base_uname = idinfo['email'].split('@')[0]
            qry2 = Users.query.filter_by(username=base_uname)
            if qry2 is None:
                user = Users(base_uname,idinfo['email'],password_digest_like)
                #buat user_detail
            else:
                #using sub-info per google documentation
                base_uname = 'guser-' + idinfo['sub']
                user = Users(base_uname,idinfo['email'],password_digest_like)
            try:
                print(user)
                print(base_uname)
                db.session.add(user)

                ##adding new user detail/info
                #should be inside try, to catch duplicate error and produce 409s
                qry3 = Users.query.filter_by(username=base_uname).first()
                user_id = qry3.user_id
                user_detail = UsersDetail(user_id,user_id)
                db.session.add(user_detail)
                
            except:
                return {'status':'failed','message':'conflicting database'}, 409, {'Content-Type':'application/json'}
            
            #add user_detail from idinfo
            qry4 = UsersDetail.query.filter_by(user_id=user_id).first()

            qry4.first_name = idinfo['given_name']
            qry4.last_name = idinfo['family_name']
            qry4.photo_url = idinfo['picture']

            db.session.commit()

            clientData = marshal(qry3, Users.jwt_claims_fields)
            uname_out = qry3.username

        #returnable to user
        clientData['isadmin'] = False

        token = create_access_token(identity=uname_out, user_claims=clientData)

        return {'token': token, 'username':uname_out, 'email':idinfo['email']}, 200, {'Content-Type': 'application/json'}


api.add_resource(CreateTokenResource, '')
api.add_resource(CreateTokenGoogleResource, '/google')
