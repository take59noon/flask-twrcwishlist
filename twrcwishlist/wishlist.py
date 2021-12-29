from flask import (
    Blueprint, 
    g, render_template, request, redirect, url_for,
    #  flash, 
)

from .db import get_db
from .helpers import apology, login_required


bp = Blueprint('wishlist', __name__)


@bp.route('/', methods=('GET',))
@bp.route('/index', methods=('GET',))
@login_required
def index():
    """Show new release products"""

    displaymode = request.args.get("d", "0")

    # Get user information
    userid = g.user['id']

    products = make_wishlist(userid, searchmode=displaymode, ordermode='date')
    artists = make_artistslist(userid)

    return render_template(
        "wishlist/index.html",
        products = products,
        artists = artists,
    )


@bp.route('/artists', methods=('GET',))
@bp.route('/artists/<artistid>', methods=('GET',))
@login_required
def artists(artistid :str = ""):
    """Show new release products of the artist"""

    displaymode = request.args.get("d", "0")

    # Get user information
    userid = g.user['id']

    # Get Artist list
    artists = make_artistslist(userid)

    if not artistid:
        return render_template(
            "wishlist/artists.html",
            artists = artists,
            # message = "Artist Search Box",
            message = "アーティスト検索",
            )

    if not get_db().execute(
        "SELECT name FROM artists "
        " WHERE id = ? ", 
        (artistid,)
    ).fetchone():
        return render_template(
            "wishlist/artists.html",
            artists = artists,
            )

    products = make_wishlist(userid, artistid, searchmode=displaymode)

    return render_template(
        "wishlist/artists.html",
        products = products,
        artists = artists,
    )


@bp.route('/purchased', methods=('POST',))
@login_required
def purchased():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        productid = request.form.get("productid", "").strip()

        # Get user information
        userid = g.user['id']
        error_message = None

        # Check if valid values
        if not productid:
            # error_message = "could not get the product ID" 
            error_message = "製品IDが取得できませんでした。" 
        elif not userid:
            # error_message = "could not get the user ID" 
            error_message = "ユーザーIDが取得できませんでした。" 

        # Connect database 
        db = get_db()
        
        if db.execute(
            "select createdon from products_purchased "
            "where userid = ? "
            "  and productid = ? ",
            (userid,productid,)
        ).fetchone() is not None:
            # error_message = "need not update the database"
            error_message = "既に購入済みであるため、データ更新は不要です。"

        # Register
        try:
            if error_message is None:
                db.execute(
                    "insert into products_purchased (userid, productid) values (?, ?)",
                    (userid, productid,)
                )
                db.commit()
            else:
                return apology(error_message)

        except Exception as e:
            # return apology(f'Failed to register. Please contact the administrator.', 500)
            return apology(f'登録に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        # return redirect(url_for('wishlist.index'))
        return redirect(request.referrer)

    else:
        return apology("Malformed request.", 400)


@bp.route('/product-hidden', methods=('POST',))
@login_required
def product_hidden():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        productid = request.form.get("productid", "").strip()

        # Get user information
        userid = g.user['id']
        error_message = None

        # Check if valid values
        if not productid:
            # error_message = "could not get the product ID" 
            error_message = "製品IDが取得できませんでした。" 
        elif not userid:
            # error_message = "could not get the user ID" 
            error_message = "ユーザーIDが取得できませんでした。" 

        # Connect database 
        db = get_db()
        
        if db.execute(
            "select createdon from products_not_displayed "
            "where userid = ? "
            "  and productid = ? ",
            (userid,productid,)
        ).fetchone() is not None:
            # error_message = "need not update the database"
            error_message = "既に非表示済みであるため、データ更新は不要です。"

        # Register
        try:
            if error_message is None:
                db.execute(
                    "insert into products_not_displayed (userid, productid) values (?, ?)",
                    (userid, productid,)
                )
                db.commit()
            else:
                return apology(error_message)

        except Exception as e:
            # return apology(f'Failed to register. Please contact the administrator.', 500)
            return apology(f'登録に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        # return redirect(url_for('wishlist.index'))
        return redirect(request.referrer)

    else:
        return apology("Malformed request.", 400)


@bp.route('/product-unhidden', methods=('POST',))
@login_required
def product_unhidden():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        productid = request.form.get("productid", "").strip()

        # Get user information
        userid = g.user['id']
        error_message = None

        # Check if valid values
        if not productid:
            # error_message = "could not get the product ID" 
            error_message = "製品IDが取得できませんでした。" 
        elif not userid:
            # error_message = "could not get the user ID" 
            error_message = "ユーザーIDが取得できませんでした。" 

        # Connect database 
        db = get_db()
        
        if db.execute(
            "select createdon from products_not_displayed "
            "where userid = ? "
            "  and productid = ? ",
            (userid,productid,)
        ).fetchone() is None:
            # error_message = "need not update the database"
            error_message = "表示データであるため、更新は不要です。"

        # Register
        try:
            if error_message is None:
                db.execute(
                    "delete from products_not_displayed "
                    "where userid = ? and productid = ? ",
                    (userid, productid,)
                )
                db.commit()
            else:
                return apology(error_message)

        except Exception as e:
            # return apology(f'Failed to update. Please contact the administrator.', 500)
            return apology(f'更新に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        # return redirect(url_for('wishlist.index'))
        return redirect(request.referrer)

    else:
        return apology("Malformed request.", 400)


@bp.route('/unpurchased', methods=('POST',))
@login_required
def unpurchased():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        productid = request.form.get("productid", "").strip()

        # Get user information
        userid = g.user['id']
        error_message = None

        # Check if valid values
        if not productid:
            # error_message = "could not get the product ID" 
            error_message = "製品IDが取得できませんでした。" 
        elif not userid:
            # error_message = "could not get the user ID" 
            error_message = "ユーザーIDが取得できませんでした。" 

        # Connect database 
        db = get_db()
        
        if db.execute(
            "select createdon from products_purchased "
            "where userid = ? "
            "  and productid = ? ",
            (userid,productid,)
        ).fetchone() is None:
            # error_message = "need not update the database"
            error_message = "購入済みでないため、データ更新は不要です。"

        # Register
        try:
            if error_message is None:
                db.execute(
                    "delete from products_purchased "
                    "where userid = ? and productid = ? ",
                    (userid, productid,)
                )
                db.commit()
            else:
                return apology(error_message)

        except Exception as e:
            # return apology(f'Failed to update. Please contact the administrator.', 500)
            return apology(f'更新に失敗しました。この問題が解決しない場合は、サーバー管理者に連絡願います。', 500)

        # return redirect(url_for('wishlist.index'))
        return redirect(request.referrer)

    else:
        return apology("Malformed request.", 400)


def make_wishlist(userid: str, artistid="", searchmode="0", ordermode="a"):
    """
    ユーザーのWishListを取得する。

    Args:
      userid (str)
      artistid (str)
      searchmode (str) : 検索タイプ(0: 未購入を表示, 1: 購入済みも表示 など)
      ordermode (str) : ソート順タイプ(a: アーティスト優先, それ以外: 発売日優先)
    Returns
      wishlist
    """

    if not userid:
        return None

    # Connect database 
    db = get_db()

    # Query user-products information
    if artistid:
        wishlist = db.execute(
            "select p.id, p.title, a.name, p.release_date, p.price, p.url "
            + "   , ad.createdon as artist_not_displayed "
            + "   , pd.createdon as product_not_displayed "
            + "   , pp.createdon as product_not_purchased "
            + "from products as p "
            + "inner join artists as a on a.id = ? and p.artistid = a.id "
            + "left join artists_not_displayed as ad on ad.userid = ? and ad.artistid = a.id "
            + "left join products_not_displayed as pd on pd.userid = ? and pd.productid = p.id "
            + "left join products_purchased as pp on pp.userid = ? and pp.productid = p.id "
            + "where (artist_not_displayed is NULL) and "
            + make_search_conditions_on_display(searchmode)
            + make_order_by(ordermode), 
            (artistid, userid, userid, userid,)
        ).fetchall()
    else:
        wishlist = db.execute(
            "select p.id, p.title, a.name, p.release_date, p.price, p.url "
            + "   , ad.createdon as artist_not_displayed "
            + "   , pd.createdon as product_not_displayed "
            + "   , pp.createdon as product_not_purchased "
            + "from products as p "
            + "left join artists as a on a.id = p.artistid "
            + "left join artists_not_displayed as ad on ad.userid = ? and ad.artistid = a.id "
            + "left join products_not_displayed as pd on pd.userid = ? and pd.productid = p.id "
            + "left join products_purchased as pp on pp.userid = ? and pp.productid = p.id "
            + "where (artist_not_displayed is NULL) and "
            + make_search_conditions_on_display(searchmode)
            + make_order_by(ordermode), 
            (userid, userid, userid,)
        ).fetchall()

    return wishlist


def make_search_conditions_on_display(mode :str):
    """
    表示に関する検索条件を作成する。

    Args:
      mode (str) : 検索タイプのキーワード
    Returns:
      r_val (str) : 検索条件文字列(SQLの一部)  
    """

    if mode in ('1','purchased',):
        # 購入済みも表示する（非表示を取得しない）
        r_val = "(product_not_displayed is NULL) "
    elif mode in ('2','purchasedonly',):
        # 購入済みのみ表示する
        r_val = "(product_not_purchased is not NULL) "
    elif mode in ('3','hiddenonly',):
        # 非表示のみ表示する
        r_val = "(product_not_displayed is not NULL) "
    elif mode in ('4','all','hidden',):
        # すべて表示する
        r_val = "(1==1) "
    else:
        # 未購入かつ非表示でないものを表示する。
        r_val = "(product_not_displayed is NULL and product_not_purchased is NULL) "

    return r_val

def make_order_by(mode: str):
    """SQLの表示順文字列を作成する"""

    if mode in ('1','a','artists',):
        r_val = "order by a.name collate nocase, p.release_date desc "
    else:
        r_val = "order by p.release_date desc, a.name collate nocase "

    return r_val

def make_artistslist(userid: str):
    """
    ユーザーのArtistsListを取得する。

    Args:
      userid (str)
    Returns
      artistslist
    """

    if not userid:
        return None

    # Connect database 
    db = get_db()

    # Query user-products information
    artistslist = db.execute(
        "select a.id, a.name, ad.createdon "
        + "from artists as a "
        + "left join artists_not_displayed as ad on ad.artistid = a.id and ad.userid = ? "
        + "where ad.createdon is NULL "
        + "order by a.name collate nocase ",
        (userid,)
    ).fetchall()

    return artistslist
