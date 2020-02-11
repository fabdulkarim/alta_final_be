import json
import os
from datetime import timedelta
from functools import wraps

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims

from flask_script import Manager

#using flask-cors to solve all the problems?
from flask_cors import CORS

app = Flask(__name__) # app.root location
CORS(app)

#not disabling loading .env
#fadhil using dotenv for not hard-coding database URL
from dotenv import load_dotenv
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
username = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
hostport = os.getenv('DATABASE_URL')
name = os.getenv('DATABASE_NAME')


#jwt secret, generated from random.org
#regenerated for final project
app.config['JWT_SECRET_KEY'] = 'bsNb0Tne6KMuuy6zE8M6ekjWaHb2XOKL'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

#declare wrapper for admin, user-specific cases
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims= get_jwt_claims()
        if not claims['isadmin']:
            return {'status': 'FORBIDDEN', 'message': 'Admin Only!'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper

def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims= get_jwt_claims()
        if claims['isadmin']:
            return {'status': 'FORBIDDEN', 'message': 'User Only!'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper

#################### TESTING
# try:
#     env = os.environ.get('FLASK_ENV', 'development') #nama, default
#     if env == 'testing':
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:JalanTidarno.23@localhost:3306/restDB_test'
#     else:
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:JalanTidarno.23@localhost:3306/restDB'
# except Exception as e:
#     raise e

##### HARUS DI ATAS ##########

app.config['APP_DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{db_user}:{db_pass}@{db_host_port}/{db_name}'.format(db_user=username,db_pass=password,db_host_port=hostport,db_name=name)
##.format(os.getenv("DATABASE_USER"),os.getenv("DATABASE_PASSWORD"),os.getenv("DATABASE_HOST_PORT"),os.getenv("DATABASE_NAME"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

########## MIDDLEWARE #############


@app.after_request
def after_request(response):
    try:
        requestData = request.get_json()
    except Exception as e:
        requestData = request.args.to_dict()
    if response.status_code == 200:
        app.logger.info("REQUEST_LOG\t%s", json.dumps({ 
            'status_code': response.status_code, # ini ngebuat 400 gak bisa masuk 
            'request': requestData, 'response': json.loads(response.data.decode('utf-8'))}))
    else:
        app.logger.error("REQUEST_LOG\t%s", json.dumps({ 
            'status_code': response.status_code,
            'request': requestData, 'response': json.loads(response.data.decode('utf-8'))}))

    return response

##add blueprint here
from blueprints.user.resources import bp_user
app.register_blueprint(bp_user, url_prefix='/users')

from blueprints.auth import bp_auth
app.register_blueprint(bp_auth, url_prefix='/auth')

from blueprints.tag.resources import bp_tag
app.register_blueprint(bp_tag, url_prefix='/tags')

from blueprints.posting.resources import bp_posting
app.register_blueprint(bp_posting, url_prefix='/posting')

from blueprints.upload import bp_upload
app.register_blueprint(bp_upload, url_prefix='/upload')

from blueprints.point.resources import bp_point
app.register_blueprint(bp_point, url_prefix='/point')

from blueprints.admin import bp_admin
app.register_blueprint(bp_admin, '/admin')
db.create_all()