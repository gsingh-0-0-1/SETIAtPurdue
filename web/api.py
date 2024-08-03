from flask import (
    abort,
    Blueprint,
    render_template,
    request
)

from flask_jwt_extended import jwt_required
from jinja2 import TemplateNotFound
import json
import os

api_blueprint = Blueprint('api', __name__,
                        template_folder='templates')


ITEMS = {
    'training_1': {
        'images' : [
            {
                'url': 'random1.jpg',
                'id': '1'
            },
            {
                'url': 'random2.jpg',
                'id': '2'
            }
        ]
    }
    }

@jwt_required(locations=["cookies"])
@api_blueprint.route('/api', methods = ["GET"])
def show():
    return "API"

@jwt_required(locations=["cookies"])
@api_blueprint.route('/api/training/<trainingid>/<action>', methods = ["GET", "POST"])
def training_action(trainingid, action):
    if trainingid == '1':
        if action == 'images':
            return json.dumps(ITEMS['training_1']['images'])
        if action == 'submit':
            return request.get_json(force = True)
