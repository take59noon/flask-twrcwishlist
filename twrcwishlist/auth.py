from flask import (
    Blueprint, 
    g, render_template, request, session, redirect, url_for
    # flash
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .helpers import apology


bp = Blueprint('auth', __name__)


@bp.before_app_request
def load_logged_in_user():
    """
    At the beginning of each request, if a user is logged in their information 
    should be loaded and made available to other views.

    Notes:
      bp.before_app_request() registers a function that runs before the view function, 
      no matter what URL is requested.
      
      load_logged_in_user() checks if a user id is stored in the session 
      and gets that user’s data from the database
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', 
            (user_id,)
        ).fetchone()


@bp.route('/login', methods=('GET','POST'))
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        pw = request.form.get("password", "").strip()

        # Ensure username was submitted
        if not name:
            # return apology("must provide username", 403)
            return apology("ユーザー名の入力が必要です。")

        # Ensure password was submitted
        elif not pw:
            # return apology("must provide password", 403)
            return apology("パスワードの入力が必要です。")

        # Connect database 
        db = get_db()

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", 
            (name,)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], pw):
            # return apology("invalid username and/or password", 403)
            return apology("ユーザー名、パスワードの入力が正しくありません。", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for('wishlist.index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=('GET','POST'))
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        pw = request.form.get("password", "").strip()
        pw_2 = request.form.get("confirmation", "").strip()

        # check if valid values
        if len(name) == 0:
            # return apology("must provide username")
            return apology("ユーザー名の入力が必要です。")
        if len(pw) == 0:
            # return apology("must provide password")
            return apology("パスワードの入力が必要です。")
        if len(pw_2) == 0:
            # return apology("Please re-enter password")
            return apology("パスワードの再入力が必定です。")

        if pw != pw_2:
            # return apology("not match the passwords")
            return apology("入力したパスワードが一致しません。")

        # Connect database 
        db = get_db()

        # Check if username is already registered
        if name:
            # Query username (nocase)
            users = db.execute(
                "select username from users where username like ?", 
                (name,)
            ).fetchone()
            if users:
                # return apology(f'Sorry, "{name}" has been already registered.', 409)
                return apology(f'あいにくですが、"{name}" はすでに登録されています。', 409)

            # Register
            try:
                db.execute(
                    "insert into users (username, hash) values (?, ?)",
                    (name, generate_password_hash(pw),)
                )
                db.commit()

            except Exception as e:
                # return apology(f'Failed to register. Please contact the administrator.', 500)
                return apology(f'登録に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

            return render_template("auth/success_register.html")
        
        else:
            # return apology("must provide username to register")
            return apology("ユーザー名がないため、データ登録できません。", 409)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/register.html")
