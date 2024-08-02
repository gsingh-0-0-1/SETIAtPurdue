from flask import (
    abort,
    Blueprint, 
    render_template,
    request
)

from jinja2 import TemplateNotFound
import json

train_blueprint = Blueprint('training', __name__,
                        template_folder='templates')


@train_blueprint.route('/training/<trainingid>', methods = ["GET"])
def show(trainingid):
    return render_template('training.html')
