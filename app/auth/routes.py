from app.auth import blueprint


@blueprint.route("/")
@blueprint.route("/index")
def auth():
    return 'auth'
