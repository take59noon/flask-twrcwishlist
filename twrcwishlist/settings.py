from flask import (
    Blueprint, 
    g, render_template, request, 
    #  flash, redirect, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .helpers import apology, login_required


bp = Blueprint('settings', __name__)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Set user information"""

    # Get user information
    userid = g.user['id']
    userhash = g.user['hash']

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        old_pw = request.form.get("oldpassword", "").strip()
        new_pw = request.form.get("newpassword", "").strip()
        new_pw_2 = request.form.get("newpassword_2", "").strip()

        # check if valid values
        if len(old_pw) == 0:
            # return apology("must provide old password in the first box")
            return apology("1番目のボックスに現在のパスワードを入力して下さい。")
        if len(new_pw) == 0:
            # return apology("must provide new password in the second box")
            return apology("2番目のボックスに新しいパスワードを入力して下さい。")
        if len(new_pw_2) == 0:
            # return apology("must provide new password in the third box, too")
            return apology("3番目のボックスに新しいパスワードをもう一度入力して下さい。")

        # Ensure username exists and password is correct
        if not check_password_hash(userhash, old_pw):
            # return apology("invalid password", 403)
            return apology("現在のパスワードの入力が正しくありません。", 403)

        if new_pw != new_pw_2:
            # return apology("not match the new passwords")
            return apology("新しいパスワードが一致しません。")

        if old_pw == new_pw:
            # return apology("new password the same as old one")
            return apology("新しいパスワードが古いパスワードと同じです。")

        # Connect database 
        db = get_db()

        # Update database
        try:
            db.execute(
                "update users set hash=? where id=?",
                (generate_password_hash(new_pw),userid,),
            )
            db.commit()

        except Exception as e:
            # return apology(f'Failed to update. Please contact the administrator.', 500)
            return apology(f'更新に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        return render_template("settings/success_settings.html")

    return render_template(
        "settings/change_pw.html",
    )
