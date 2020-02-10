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
    def get(self):
        parser =reqparse.RequestParser()
        parser.add_argument("content_type", location="args", choices=('article','question','answer','comment'))
        parser.add_argument('user_id',location='args')
        parser.add_argument('locator_id',location='args')
        args = parser.parse_args()

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
        parser.add_argument('locator_id',location='json', required=True)
        parser.add_argument('value',location='json', choices=(0,1), required=True)
        args = parser.parse_args()

        #filter first
        qry = Points.query
        qry = qry.filter_by(content_type=args['content_type']).filter_by(locator_id=args['locator_id'])

        qry_me = qry.filter_by(user_id=user_id)
        qry_me = qry_me.first()
        
        #delete/unvote
        if args['value'] == 0:

            qry_me.deleted = True
        #renew or mint
        else:
            #mint
            if qry_me is None:
                point = Points(user_id, args['content_type'], args['locator_id'])

                db.session.add(point)
            #renew
            else:
                qry_me.deleted = False

        #rekalkulasi poin untuk posting/konten
        if args['content_type'] in ['article','question']:
            qry2 = TopLevels.query.get(args['locator_id'])
        else:
            qry2 = SecondLevels.query.get(args['locator_id'])



        qry2.point

        db.session.commit()

