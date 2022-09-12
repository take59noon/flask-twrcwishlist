"""
The __init__.py serves double duty: it will contain the application factory, 
and it tells python that the flaskr directory should be treated as a package.  
"""

import os 
from tempfile import mkdtemp

from flask import Flask
from flask_session import Session
from markupsafe import escape
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from .helpers import apology


def create_app(test_config=None):
    """
    This is the application factory.
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'TowerRecordsWishList.db'),
    )

    # Ensure templates are auto-reloaded
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Configure session to use filesystem (instead of signed cookies)
    app.config["SESSION_FILE_DIR"] = mkdtemp()
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Configure LINE Bot API
    app.config["YOUR_CHANNEL_ACCESS_TOKEN"] = 'linebot_access_token'
    app.config["YOUR_LINE_ID"] = 'linebot_user_id'

    # Read addtional config file
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile(os.path.join(app.instance_path, 'app_settings.cfg'), silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists, and create it if not exist
    os.makedirs(app.instance_path, exist_ok=True)

    # Ensure responses aren't cached
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Set database
    from . import db
    db.init_app(app)

    # Register contents
    from . import auth
    app.register_blueprint(auth.bp)

    from . import wishlist
    app.register_blueprint(wishlist.bp)

    from . import settings
    app.register_blueprint(settings.bp)

    from .tasks import update_db
    app.register_blueprint(update_db.bp)

    # Set default web page
    app.add_url_rule('/', endpoint='index')

    # Ensure error handler
    def errorhandler(e):
        """Handle error"""
        if not isinstance(e, HTTPException):
            e = InternalServerError()
        return apology(escape(e.name), e.code)

    # Listen for errors
    for code in default_exceptions:
        app.errorhandler(code)(errorhandler)

    return app
