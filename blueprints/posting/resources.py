from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc

from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import admin_required, user_required

from datetime import datetime

from .model import TopLevels
from blueprints import db, app

from . import *

bp_posting = Blueprint('posting', __name__)
api = Api(bp_posting)

#CR features for top-level posting (no param)
class TopLevelCR(Resource):
    #getall, open for all (visitor-level)
    def get(self):
        