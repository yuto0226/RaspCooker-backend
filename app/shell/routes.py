from app.shell import blueprint
from app.auth import token_required

@blueprint.route('/')
@blueprint.route('/index')
@token_required
def index():
    return 'shell'
