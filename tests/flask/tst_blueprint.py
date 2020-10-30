from flask import Blueprint, render_template, current_app

route = Blueprint('test_blueprint', __name__, template_folder='views')

service_locator = None

@route.route('/sub/hello')
def hello():
    config = service_locator.get('config')
    return 'hello '+config['foo']+' in sub module!'
