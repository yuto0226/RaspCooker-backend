from app.task import blueprint


@blueprint.route('/')
@blueprint.route('/index')
def index():
    return 'task'
