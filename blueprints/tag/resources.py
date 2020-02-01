from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from datetime import datetime

from .model import Tags
from blueprints import db, app

from . import *

bp_tag = Blueprint('tag', __name__)
api = Api(bp_tag)

#CUD untuk admin
class AdminTagEdit(Resource):
    @jwt_required
    @admin_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('photo_url', location='json', required=True)
        
        args = parser.parse_args()

        tag = Tags(args['name'],args['photo_url'])

        db.session.add(tag)
        db.session.commit()

        return marshal(tag, Tags.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @admin_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('photo_url', location='json', required=True)
        parser.add_argument('deleted', location='json', required=True)

        args = parser.parse_args()

        qry = Tags.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404, {'Content-Type': 'application/json'}

        qry.name = args['name']
        qry.photo_url = args['photo_url']
        qry.deleted = bool(args['deleted'])
        qry.updated_at = db.func.now()
        