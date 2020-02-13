from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from .model import Points
from ..posting.model import TopLevels, SecondLevels
from ..user.model import Users
from blueprints import db, app

bp_point = Blueprint('point', __name__)
api = Api(bp_point)

class PointCRU(Resource):
    #CORS
    def options(self, *args, **kwargs):
        return {}, 200

    @jwt_required
    @user_required
    def get(self):
        
        user_id = get_jwt_claims()['user_id']

        # parser =reqparse.RequestParser()
        # parser.add_argument("content_type", location="args", choices=('article','question','answer','comment'))
        # parser.add_argument('locator_id',location='args')
        # args = parser.parse_args()

        # if args['content_type'] in ['article','question']:
        # qry = Points.query.filter_by(locator_id=args['locator_id'])
        qry = qry.filter_by(user_id=user_id)
        # .filter_by(content_type=args['content_type']).first()
        rows = []
        for que in qry:
            rows.append(marshal(que,Points.response_fields))

        # if qry.deleted == False:
        # return all, if None returns empty?
        return marshal(rows), 200, {'Content-Type':'application/json'}
        
        # return mar
        #yang direturn apa?

    # @jwt_required
    # @user_required
    # def post(self):

    #     users_id = get_jwt_claims()['user_id']

    #     parser =reqparse.RequestParser()
    #     parser.add_argument("content_type", location="json", choices=('article','question','answer','comment'))
    #     parser.add_argument('locator_id',location='args')
    #     args = parser.parse_args()

        
    #     point = Points(user_id, args['content_type'], args['locator_id'])

    #     db.session.add(point)
    #     db.session.commit()

    @jwt_required
    @user_required
    def put(self):

        user_id = get_jwt_claims()['user_id']

        parser =reqparse.RequestParser()
        parser.add_argument("content_type", location="json", choices=('article','question','answer','comment'), required=True)
        parser.add_argument('locator_id',location='json', type=int, required=True)
        parser.add_argument('value',location='json', type=int, choices=(0,1), required=True)
        args = parser.parse_args()

        #filter first
        qry = Points.query
        qry = qry.filter_by(content_type=args['content_type']).filter_by(locator_id=args['locator_id'])

        ###check content

        # qry_me = qry.filter_by(user_id=user_id)
        qry_me = qry.first()
        
        #delete/unvote
        if args['value'] == 0:
            ### kondisi kalau mint dan 0
            qry_me.deleted = True
            qry_me.updated_at = db.func.now()
            point = qry_me
        #renew or mint
        else:
            #mint
            if qry_me is None:
                point = Points(user_id, args['locator_id'], args['content_type'])

                db.session.add(point)
            #renew
            else:
                qry_me.deleted = False
                qry_me.updated_at = db.func.now()
                point = qry_me

        #rekalkulasi poin untuk posting/konten
        if args['content_type'] in ['article','question']:
            qry2 = TopLevels.query.get(args['locator_id'])
        else:
            qry2 = SecondLevels.query.get(args['locator_id'])

        ###break point kalau ga ada

        qry3 = qry.filter_by(deleted=False)
        qry2.point = qry3.count()

        db.session.commit()

        return marshal(point, Points.response_fields), 200, {'Content-Type':'application/json'}

api.add_resource(PointCRU,'')