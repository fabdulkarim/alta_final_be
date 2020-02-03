from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

#using base to do images upload
from flask import request

import os, random
import string, json

bp_upload = Blueprint('upload', __name__)
api = Api(bp_upload)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploads(fileto):
    cmd = "curl -sb POST --include " + "'https://api.pixhost.to/images' " + "-H 'Content-Type: multipart/form-data; charset=utf-8' " + "-H 'Accept: application/json' " + "-F 'img=@" + fileto + "' -F 'content_type=0' > out.json" 

    os.system(cmd)
    
    with open('out.json') as src:
        lines = src.readlines()
        for i,line in enumerate(lines):
            #print(i, line)
            if i == len(lines) - 1:
                data = json.loads(line)
                data = data['th_url']

    os.system("rm "+fileto)
    os.system("rm out.json")
                
    true_link = data.replace('thumbs','images')
    true_link = 'https://img' + ''.join(true_link[9:])

    return true_link

class UploadResources(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'no input file given'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'message': 'unproper name for uploaded file'}, 401

        if file and allowed_file(file.filename):
            filename3 = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8)) + '.jpg'
            file.save(os.path.abspath(filename3))

            temp_abs_path = os.path.abspath(filename3)

            img_link = uploads(temp_abs_path)

            return {'status':'success', 'url_to_see':img_link}, 200, {'Content-Type': 'application/json'}


api.add_resource(UploadResources,'')
