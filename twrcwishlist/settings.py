from flask import (
    Blueprint, 
    g, render_template, redirect, request, 
    #  flash, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .helpers import apology, login_required


bp = Blueprint('settings', __name__, url_prefix='/settings')


SETTINGS_LIST = [
    # /url_tail, name
    ['/change-password', 'パスワード変更'],
    ['/register-artist', 'アーティスト登録'],
    ['/artistlist', 'アーティスト設定'], 
]


@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    return render_template(
        "settings/settings_index.html",
        is_hidden_signature=True,
        settings=SETTINGS_LIST,
    )


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

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

        return render_template(
            "settings/success_settings.html",
            is_hidden_signature=True,
            settings=SETTINGS_LIST,
            )

    return render_template(
        "settings/change_pw.html",
        is_hidden_signature=True,
        settings=SETTINGS_LIST,
    )


@bp.route("/artistlist", methods=["GET",])
@login_required
def artistlist():
    """Display artist list"""

    displaymode = request.args.get("d", "all")

    # Get user information
    userid = g.user['id']

    artists = make_artistslist(userid, searchmode=displaymode)

    return render_template(
        "settings/artistlist.html",
        is_hidden_signature=True,
        settings=SETTINGS_LIST,
        artists=artists,
    )


@bp.route('/artist-hidden', methods=('POST',))
@login_required
def artist_hidden():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        artistid = request.form.get("artistid", "").strip()

        # Get user information
        userid = g.user['id']
        error_message = None

        # Check if valid values
        if not artistid:
            # error_message = "could not get the artist ID" 
            error_message = "アーティストIDが取得できませんでした。" 
        elif not userid:
            # error_message = "could not get the user ID" 
            error_message = "ユーザーIDが取得できませんでした。" 

        # Connect database 
        db = get_db()
        
        if db.execute(
            "select createdon from artists_not_displayed "
            "where userid = ? "
            "  and artistid = ? ",
            (userid, artistid,)
        ).fetchone() is not None:
            # error_message = "need not update the database"
            error_message = "既に非表示済みであるため、データ更新は不要です。"

        # Register
        try:
            if error_message is None:
                db.execute(
                    "insert into artists_not_displayed (userid, artistid) values (?, ?)",
                    (userid, artistid,)
                )
                db.commit()
            else:
                return apology(error_message)

        except Exception as e:
            # return apology(f'Failed to register. Please contact the administrator.', 500)
            return apology(f'登録に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        # return redirect(url_for('settings.artistlist'))
        return redirect(request.referrer)

    else:
        return apology("Malformed request.", 400)


@bp.route('/artist-unhidden', methods=('POST',))
@login_required
def artist_unhidden():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        artistid = request.form.get("artistid", "").strip()

        # Get user information
        userid = g.user['id']
        error_message = None

        # Check if valid values
        if not artistid:
            # error_message = "could not get the artist ID" 
            error_message = "アーティストIDが取得できませんでした。" 
        elif not userid:
            # error_message = "could not get the user ID" 
            error_message = "ユーザーIDが取得できませんでした。" 

        # Connect database 
        db = get_db()
        
        if db.execute(
            "select createdon from artists_not_displayed "
            "where userid = ? "
            "  and artistid = ? ",
            (userid, artistid,)
        ).fetchone() is None:
            # error_message = "need not update the database"
            error_message = "表示データであるため、更新は不要です。"

        # Register
        try:
            if error_message is None:
                db.execute(
                    "delete from artists_not_displayed "
                    "where userid = ? and artistid = ? ",
                    (userid, artistid,)
                )
                db.commit()
            else:
                return apology(error_message)

        except Exception as e:
            # return apology(f'Failed to update. Please contact the administrator.', 500)
            return apology(f'更新に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        # return redirect(url_for('settings.artistlist'))
        return redirect(request.referrer)

    else:
        return apology("Malformed request.", 400)


@bp.route('/register-artist', methods=('GET','POST'))
@login_required
def register_artist():
    """Register artist"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        artistid = request.form.get("artistid", "").strip()
        artistname = request.form.get("artistname", "").strip()

        # check if valid values
        if len(artistid) == 0:
            # return apology("must provide artist ID")
            return apology("アーティストIDの入力が必要です。")
        if len(artistname) == 0:
            # return apology("must provide artist name")
            return apology("アーティスト名の入力が必要です。")

        # Connect database 
        db = get_db()

        # Check if artistname is already registered
        artists = db.execute( 
            "select id, name from artists where name like ?", 
            (artistname,)
        ).fetchone()  # Query artistname (nocase)
        if artists:
            # return apology(f'Sorry, "{artistname}" has been already registered.', 409)
            return apology(f'あいにくですが、"{artistname}" はすでに登録されています。', 409)

        # Check if artistid is already registered
        artists = db.execute( 
            "select id, name from artists where id like ?", 
            (artistid,)
        ).fetchone()  # Query artistid (nocase)
        if artists:
            # return apology(f'Sorry, "{artistid}" has been already registered.', 409)
            return apology(f'あいにくですが、"{artistid}" はすでに登録されています。', 409)

        # Register
        if artistname and artistid:
            try:
                db.execute(
                    "insert into artists (id, name) values (?, ?)",
                    (artistid, artistname,)
                )
                db.commit()

            except Exception as e:
                # return apology(f'Failed to register. Please contact the administrator.', 500)
                return apology(f'登録に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

            return render_template(
                "settings/success_register_artist.html",
                is_hidden_signature=True,
                settings=SETTINGS_LIST,
            )
        
        else:
            # return apology("must provide artist ID and artist name to register")
            return apology("アーティストIDあるいはアーティスト名がないため、データ登録できません。", 409)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template(
            "settings/register_artist.html",
            is_hidden_signature=True,
            settings=SETTINGS_LIST,
        )


def make_artistslist(userid: str, searchmode="all"):
    """
    ユーザーのArtistsListを取得する。

    Args:
      userid (str)
      searchmode (str) : 検索タイプ(all: 全て表示, 1: アクティブのみ表示 など)
    Returns
      artistslist
    """

    if not userid:
        return None

    # Connect database 
    db = get_db()

    # Query user-products information
    artistslist = db.execute(
        "select a.id, a.name, ad.createdon as not_displayed "
        + "from artists as a "
        + "left join artists_not_displayed as ad on ad.artistid = a.id and ad.userid = ? "
        + "where "
        + make_search_conditions_on_display(searchmode)
        + "order by a.name collate nocase ",
        (userid,)
    ).fetchall()

    return artistslist


def make_search_conditions_on_display(mode :str):
    """
    表示に関する検索条件を作成する。

    Args:
      mode (str) : 検索タイプのキーワード
    Returns:
      r_val (str) : 検索条件文字列(SQLの一部)  
    """

    if mode in ('1','active',):
        # アクティブデータのみ表示する
        r_val = "(not_displayed is NULL) "
    elif mode in ('2','inactive',):
        # 非アクティブデータのみ表示する
        r_val = "(not_displayed is not NULL) "
    else:
        # すべて表示する
        r_val = "(1==1) "

    return r_val

