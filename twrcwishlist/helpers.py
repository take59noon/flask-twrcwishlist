from flask import g, redirect, render_template, url_for
from functools import wraps
from markupsafe import escape


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", message=escape(message), code=code), code


def login_required(view):
    """
    Decorate routes to require login.

    Notes:
      This decorator returns a new view function that wraps the original view it’s applied to. 
      The new function checks if a user is loaded and redirects to the login page otherwise. 
      If a user is loaded the original view is called and continues normally.

      https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
    """
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            # return redirect("/login")
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return decorated_function


def yen(value):
    """Format value as YEN."""
    return f"￥{value:,}"
