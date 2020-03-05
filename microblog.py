from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    """automatically imports the following dictionary values
    when running `flask shell` to avoid having multiple imports
    values can be referenced by the dict key in the shell"""
    return {'db': db, 'User': User, 'Post': Post}


if __name__ == '__main__':
    app.run(debug=True)
