from pathlib import Path
import requests
from sys import argv
from time import sleep
import urllib.parse

from bs4 import BeautifulSoup 
from dateutil.parser import parse

# Import private packages
from db_sqlite import sqlite_orm
from stringextractor import extract_a_date


# Import and configure logging module
import logging, logging.config
import yaml

logger_conf_path = Path(__file__).with_suffix('.yaml') 
if logger_conf_path.exists():
    logging.config.dictConfig(
        yaml.load(open(logger_conf_path).read(), Loader=yaml.SafeLoader)
    )

# Get logger
logger = logging.getLogger(Path(__file__).name)


# Set database path
DB_DIR_PATH = Path(__file__).parents[1] / 'instance'
DB_FILE_NAME = 'TowerRecordsWishList.db'
DB_FILE_PATH  = DB_DIR_PATH / DB_FILE_NAME


def run_update_products():
    """
    update_products関数を実行する。
    
    Notes:
      コマンドライン引数がある場合は
      それらをすべてartistidとしてupdate_products関数に引き渡す。
    """
    
    logger.debug('=============== start ===============')

    artists = []
    if len(argv) > 1:
        artists = [a for a in argv[1:]]
    
    update_products(artists)

    logger.debug('===============  end  ===============')


def update_products(artists=[], request_interval=1):
    """
    TowerRecordsのWebページに問合せて、
    productsテーブルに登録されていないデータがあれば、
    データ投入する。

    Args:
      artists (list[str]) : [artistid, ...]
      request_interval (int) : request間隔(秒)

    Returns:
      なし

    Notes:
      データベースに登録済みのartistに対してのみ、
      TowerRecordsのWebページにデータを問い合わせるものとする。
    """

    try:
        # データベースに接続する。
        db = sqlite_orm(DB_FILE_PATH)

        # 登録済みのartistidを取得する。
        db_artists_raw = db.cursor.execute(
            "select id from artists ",
        ).fetchall()
        if db_artists_raw:
            db_artists = [row["id"] for row in db_artists_raw]
        else:
            db_artists = []

        # 更新対象のartistidを設定する。
        if len(artists) > 0:
            # 引数が適切か確認する。
            # データベースに登録されていない値は対象から除外する。
            targetids = [a for a in artists]
            
        else:
            # データベースに登録済みのすべてのartistidを
            # 更新対象に設定する。
            targetids = db_artists

        # 更新対象のartistidを1つずつ処理する。
        for artistid in targetids:
            logger.debug(f'processing "artistid = {artistid}" ...')

            # requestの間隔を調整する。
            sleep(request_interval) 

            # TowerRecordsからHTML取得
            html_raw = request_discography(artistid)
            if not html_raw:
                # 不正な応答を取得したので、次のartistidの処理へ進む。
                continue

            # HTML解析
            product_infos = scraping_discography(html_raw)

            # データベースに未登録のproductidがあれば登録する。
            for p in product_infos:
                target_productid = p["productid"]

                exists_productid = db.cursor.execute(
                    "select id from products "
                    "where id = ?",
                    (target_productid,)
                ).fetchone()

                if not exists_productid:
                    logger.debug(f'A new product data found (id = {target_productid}). Insert into the database...')
                    with db.conn:
                        db.cursor.execute(
                            "insert into products (id,title,artistid,category,price,release_date,url,image_src) "
                            "values (?,?,?,?,?,?,?,?);",
                            (p["productid"], p["title"], artistid, p["product_format"], p["release_price"], p["release_date"], p["product_href"], p["img_src"],)
                        )
    except Exception as e:
        logger.error(e)
    
    finally:
        db.disconnect()


def request_discography(
    artistid,
    baseurl = "https://tower.jp/artist/discography",
    param_sort = "New",
    param_format = "121",
):
    """
    タワレコのディスコグラフィのページを取得する。
    
    Args:
      baseurl (str) 
      artistid (str)
      sort (str) : ("New": 新→旧順)
      format (str): ("121": CDの情報を取得する)
    
    Returns:
      res_raw_html (str) : ResponseのHTML
      
    """
    
    search_url = urllib.parse.urljoin(baseurl,artistid)

    params = {
        "sort": param_sort,
        "format": param_format,
    }
    
    user_agent = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    header = {
        "User-Agent": user_agent,
    }
    
    try:
        res = requests.get(
            search_url, 
            params=params,
            headers=header,
        )
        res.raise_for_status() # 不正なリクエスト(200以外)の場合、エラーを発生させる
        
        return res.text
        
    except Exception as e:
        logger.error(f'Could not receive a valid response from {search_url}')
        logger.error(e)
        
        return None


def scraping_discography(html_raw):
    """
    タワーレコードのディスコグラフィのページをスクレイピングして、
    辞書式データに変換する。

    Args:
      html_raw (str)
    Returns:
      product_infos (list[dict])
    """

    bso = BeautifulSoup(html_raw, "html.parser")
    item_objs = bso.select(".artistSectionLine01 li")

    product_infos = []
    for li in item_objs:
        try:
            productid = li.select(".itemId")[0].get("value")
            
            title = li.select(".title")[0].getText()
            product_href = li.a.get("href")
            img_src = li.a.img.get("src")
            
            artist = li.select(".artist")[0].getText()
            release_info = li.select(".artistPriceDl01 dd")
            if release_info:
                rdate = extract_a_date(release_info[0].getText(), format=r'%Y-%m-%d')
                rprice = convert_str_to_int(release_info[1].getText())
            else:
                rdate = None
                rprice = None
            product_format = li.select(".format")[0].getText()
            
            product_info = {
                "productid": productid,
                "product_format": product_format,
                "product_href": product_href,
                "artist": artist,
                "img_src": img_src,
                "release_date": rdate,
                "release_price": rprice,
                "title": title,        
            }
            product_infos.append(product_info)

        except Exception as e:
            logger.error(e)

    return product_infos


def convert_str_to_int(in_str: str):
    """
    入力された文字列をint型に変換する。

    Args:
      in_str (str)
    Returns:
      r_val (int)
    Notes:
      scraping_discography関数のために作成した。
      無視する文字をもっと増やす必要が出てきた場合は、
      引数で設定できるようにしたい。
    """

    tmp_str = in_str.strip()

    if not tmp_str:
        return None
    
    try:
        r_val = int(tmp_str.replace('￥','').replace(',',''))
        return r_val
    except ValueError as e:
        logging.error(e)
        return None
    except Exception as e:
        logging.error(e)
        return None    


if __name__ == "__main__":
    run_update_products()
