from app.file import blueprint


@blueprint.route('/')
@blueprint.route('/index')
def index():
    return 'file'
