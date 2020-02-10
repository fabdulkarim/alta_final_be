import hashlib

from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

from ..user.model import Users

#using g-api-python-client
from google.oauth2 import id_token
from google.auth.transport import requests

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
            token = create_access_token(identity=args['username'], user_claims={'isadmin':True})
            return {'token': token, 'is_admin':'true'}, 200

        password_digest = hashlib.md5(args['password'].encode()).hexdigest()

        qry = Users.query.filter_by(username=args['username']).filter_by(password=password_digest)

        clientData = qry.first()

        if clientData is not None:
            clientData = marshal(clientData, Users.jwt_claims_fields) 
            clientData['isadmin'] = False
            
            token = create_access_token(identity=args['username'], user_claims=clientData)
            
            
            ##### fasilitas dari flask
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
        # parser.add_argument('email', location='json', required=True)
        parser.add_argument('id_token', location='json', required=True)
        args = parser.parse_args()
        
        #id_token check
        CLIENT_ID = "164164000203-aeirfg61lk5363cp27fri0odtq32cp7u.apps.googleusercontent.com"

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
            clientData['isadmin'] = False

            token = create_access_token(identity=qry.username, user_claims=clientData)

            return {'token': token}, 200, {'Content-Type': 'application/json'}

        else:
            password_digest_like = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            base_uname = idinfo['email'].split('@')[0]
            qry2 = Users.query.filter_by(username=base_uname)
            if qry2 is None:
                user = Users(base_uname,idinfo['email'],password_digest_like)
                #buat user_detail
                try:
                    db.session.add(user)

                    ##adding new user detail/info
                    #should be inside try, to catch duplicate error and produce 409s
                    qry3 = Users.query.filter_by(username=base_uname).first()
                    user_id = qry3.user_id
                    user_detail = UsersDetail(user_id,user_id)
                    db.session.add(user_detail)
                    
                except:
                    return {'status':'failed','message':'conflicting database'}, 409, {'Content-Type':'application/json'}
                
                clientData = marshal(qry3, Users.jwt_claims_fields)
                clientData['isadmin'] = False

                token = create_access_token(identity=qry.username, user_claims=clientData)

                return {'token': token}, 200, {'Content-Type': 'application/json'}


api.add_resource(CreateTokenResource, '')
api.add_resource(CreateTokenGoogleResource, '/google')
