from app.shell import blueprint


@blueprint.route('/')
@blueprint.route('/index')
def index():
    return 'shell'
