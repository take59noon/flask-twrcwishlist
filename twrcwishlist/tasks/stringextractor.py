"""文字列抽出器。テキストから特定の文字列を抽出する為のモジュール。

Notes:
  各関数の入出力値については、test関数も参考にすること。  
"""

from datetime import date
from datetime import datetime, timedelta, timezone
import re

from dateutil.parser import parse


#----------------------------------------
# Constant Variables
#----------------------------------------
# 全角半角変換対象文字列
ZEN = "".join(chr(0xff01 + i) for i in range(94))
HAN = "".join(chr(0x21 + i) for i in range(94))
# 変換テーブル
ZEN2HAN = str.maketrans(ZEN, HAN)
HAN2ZEN = str.maketrans(HAN, ZEN)

# #使用例
# # 全角から半角
# print(ZEN.translate(ZEN2HAN))
# # 結果
# # !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~

# # 半角から全角
# print(HAN.translate(HAN2ZEN))
# # 結果
# # ！＂＃＄％＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿｀ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔ

# 和暦西暦変換辞書
# keyの年号に対して、valueの数値を足すと西暦の年数になる。
WAREKI2SEIREKI = {
    '明治':1867,
    '大正':1911,
    '昭和':1925,
    '平成':1988,
    '令和':2018,
    'M':1867,
    'T':1911,
    'S':1925,
    'H':1988,
    'R':2018,
}


#--------------------------------------------------
# Regex Strings (not compiled)
#--------------------------------------------------

REGEXSTR_YEAR_NUM = r"""
([1-9][0-9]{3}|[0-9]{2})
"""
# 4桁または2桁表記のみ認める場合の正規表現

REGEXSTR_MONTH_NUM = r"""
(1[0-2]|0?[1-9])
"""

REGEXSTR_DAY_NUM = r"""
([1-2][0-9]|3[0-1]|0?[1-9])
"""

REGEXSTR_MONTH_EN = r"""
(JANUARY|JAN|JAN\.
|FEBRUARY|FEB|FEB\.
|MARCH|MAR|MAR\.
|APRIL|APR|APR\.
|MAY
|JUNE|JUN|JUN\.
|JULY|JUL|JUL\.
|AUGUST|AUG|AUG\.
|SEPTEMBER|SEP|SEP\.
|OCTOBER|OCT|OCT\.
|NOVEMBER|NOV|NOV\.
|DECEMBER|DEC|DEC\.)
"""

REGEXSTR_DAY_EN_PRE = r"""
(\d+)(ST|ND|RD|TH|)
"""
REGEXSTR_DAY_EN = rf"""
{REGEXSTR_DAY_NUM}(ST|ND|RD|TH|)
"""
# 「JANUARY 2ND」は抽出できるが、
# 「JANUARY 13TH」だと「JANUARY 13」と抽出してしまう。

REGEXSTR_YEAR_JP = r"""
((明治\s*|大正\s*|昭和\s*|平成\s*|令和\s*)|(M|T|S|H|R|)|)
"""
# ※略称記号と数字の間のスペースは認めない。


#--------------------------------------------------
# Regex Objects (Compiled)
#--------------------------------------------------

# REGEX_NUMBER
REGEX_NUMBER = re.compile(r"""(
    (\+|\-)?(\d*\.\d+|\d+\.\d*|\d+)
)""", re.VERBOSE)

REGEX_DATE_PRE = re.compile(r"""((
    \d+-\d+-\d+
)|(
    \d+/\d+/\d+
)|(
    \d+/\d+
)|(
    \d+-\d+
))""", re.VERBOSE)

REGEX_DATE = re.compile(rf"""((
    ^
    {REGEXSTR_YEAR_NUM}\-   # 年
    {REGEXSTR_MONTH_NUM}\-  # 月
    {REGEXSTR_DAY_NUM}      # 日
    $
)|(
    ^
    {REGEXSTR_YEAR_NUM}/    # 年
    {REGEXSTR_MONTH_NUM}/   # 月
    {REGEXSTR_DAY_NUM}      # 日
    $
)|(
    ^
    {REGEXSTR_DAY_NUM}\-    # 日
    {REGEXSTR_MONTH_NUM}\-  # 月    
    {REGEXSTR_YEAR_NUM}     # 年
    $
)|(
    ^
    {REGEXSTR_DAY_NUM}/     # 日
    {REGEXSTR_MONTH_NUM}/   # 月
    {REGEXSTR_YEAR_NUM}     # 年
    $
)|(
    ^
    {REGEXSTR_MONTH_NUM}\-  # 月
    {REGEXSTR_DAY_NUM}\-    # 日
    {REGEXSTR_YEAR_NUM}     # 年
    $
)|(
    ^
    {REGEXSTR_MONTH_NUM}/   # 月
    {REGEXSTR_DAY_NUM}/     # 日
    {REGEXSTR_YEAR_NUM}     # 年
    $
)|( 
    ^
    {REGEXSTR_YEAR_NUM}\-   # 年
    {REGEXSTR_MONTH_NUM}    # 月
    $
)|(
    ^
    {REGEXSTR_YEAR_NUM}/    # 年
    {REGEXSTR_MONTH_NUM}    # 月
    $    
)|(
    ^
    {REGEXSTR_MONTH_NUM}\-  # 月
    {REGEXSTR_YEAR_NUM}     # 年
    $
)|(
    ^
    {REGEXSTR_MONTH_NUM}/   # 月
    {REGEXSTR_YEAR_NUM}     # 年
    $    
)|(
    ^
    {REGEXSTR_MONTH_NUM}\-  # 月
    {REGEXSTR_DAY_NUM}      # 日
    $
)|(
    ^
    {REGEXSTR_MONTH_NUM}/   # 月
    {REGEXSTR_DAY_NUM}      # 日
    $
)|(
    ^
    {REGEXSTR_DAY_NUM}\-    # 日
    {REGEXSTR_MONTH_NUM}    # 月
    $
)|(
    ^
    {REGEXSTR_DAY_NUM}/     # 日
    {REGEXSTR_MONTH_NUM}    # 月
    $
))""", re.VERBOSE)

# REGEX_DATE_EN
#   DMY   : 5th January, 2021
#   MDY   : January 5th, 2021
#   DM    : 5th January
#   MY/MD : January, 2021 / January 5th
# ※DMYはイギリス式、MDYはアメリカ式。
# 
REGEX_DATE_EN_PRE = re.compile(rf"""((
    {REGEXSTR_DAY_EN_PRE}\s*      # 日
    {REGEXSTR_MONTH_EN}(|,)\s*    # 月
    (\d+)                         # 年
)|(
    {REGEXSTR_MONTH_EN}\s*        # 月
    {REGEXSTR_DAY_EN_PRE}(|,)\s*  # 日
    (\d+)                         # 年
)|(
    {REGEXSTR_MONTH_EN}(|,)\s*    # 月
    (\d+)                         # 年 or 日 （※stなどは末尾指定をしないと抽出できなかった。）
)|(
    {REGEXSTR_DAY_EN_PRE}\s*      # 日
    {REGEXSTR_MONTH_EN}           # 月 （※「.」は末尾指定をしないと抽出できない。）
))""", re.VERBOSE)

REGEX_DATE_EN = re.compile(rf"""((
    ^
    {REGEXSTR_DAY_EN}\s*        # 日
    {REGEXSTR_MONTH_EN}(|,)\s*  # 月
    (\d+)                       # 年
    $
)|(
    ^
    {REGEXSTR_MONTH_EN}\s*    # 月
    {REGEXSTR_DAY_EN}(|,)\s*  # 日
    (\d+)                     # 年
    $
)|(
    ^
    {REGEXSTR_MONTH_EN}\s*    # 月
    {REGEXSTR_DAY_EN}         # 日
    $
)|(
    ^
    {REGEXSTR_MONTH_EN}(|,)\s* # 月
    (\d+)                      # 年
    $
)|(
    ^
    {REGEXSTR_DAY_EN}\s*  # 日
    {REGEXSTR_MONTH_EN}   # 月
    $
))""", re.VERBOSE)

# REGEX_DATE_JP
#   YMD : 令和3年6月10日
#   YMD : R3年6月10日
#   YMD : 2021年6月10日
#   YM  : 令和3年6月
#   YM  : R3年6月
#   YM  : 2021年6月
#   MD  : 6月10日
#
REGEX_DATE_JP = re.compile(rf"""((
    {REGEXSTR_YEAR_JP}(\d+)\s*年\s*  # 年
    (\d+)\s*月\s*  # 月
    (\d+)\s*日     # 日
)|(
    {REGEXSTR_YEAR_JP}(\d+)\s*年\s*  # 年
    (\d+)\s*月     # 月
)|(  
    (\d+)\s*月\s*  # 月
    (\d+)\s*日     # 日
))""", re.VERBOSE)

REGEX_YEAR_JP = re.compile(rf"""
    {REGEXSTR_YEAR_JP}(\d+)\s*年
""", re.VERBOSE)
REGEX_MONTH_JP = re.compile(rf"""
    (\d+)\s*月
""", re.VERBOSE)
REGEX_DAY_JP = re.compile(rf"""
    (\d+)\s*日
""", re.VERBOSE)


#----------------------------------------
# Functions
#----------------------------------------
def extract_numbers(in_sentence: str):
    """文章の中から数値を示す文字列を抽出する。

    Args:
      in_sentence (str) : 入力テキスト
    Returns:
      抽出した文字列のリスト
    Notes:
      対象文字列が見つからなかった場合は、空のリストを出力する。
    """
    
    if in_sentence is None:
        return []

    # 前処理
    tmp_str = in_sentence.strip()         # トリミング処理
    tmp_str = tmp_str.translate(ZEN2HAN)  # 全角->半角処理

    # 抽出処理
    fo = REGEX_NUMBER.findall(tmp_str)

    # 結果出力
    list_extracted_numbers = [mo[0] for mo in fo]
    
    return list_extracted_numbers

def extract_a_number(in_sentence: str):
    """文章の中に数値を示す文字列が1つあれば、それを抽出する。

    Args:
      in_sentence (str) : 入力テキスト
    Returns:
      抽出した文字列
    Notes:
      対象文字列が見つからない場合や、複数見つかる場合はNoneを返す。
    """

    list_extracted_numbers = extract_numbers(in_sentence)

    if len(list_extracted_numbers) == 1:
        r_val = list_extracted_numbers[0]
    else:
        r_val = None

    return r_val


def extract_dates(in_sentence: str, checkifvalid=True):
    """文章の中から日付を示す文字列を抽出する。

    Args:
      in_sentence (str) : 入力テキスト
      checkifvalid (bool) : 値の妥当性を確認するかどうか（True: する）
    Returns:
      抽出した日付のリスト
    Notes:
      対象文字列が見つからなかった場合は、空のリストを出力する。
    """
    
    if not in_sentence:
        return []

    # 抽出処理
    list_extracted_dates_num = extract_dates_num(in_sentence,checkifvalid=checkifvalid)  # /-表記を抽出する
    list_extracted_dates_en = extract_dates_en(in_sentence,checkifvalid=checkifvalid)  # 英語表記を抽出する
    list_extracted_dates_jp = extract_dates_jp(in_sentence,checkifvalid=checkifvalid)  # 和暦表記を抽出する

    # 結果出力
    list_extracted_dates = list_extracted_dates_num + list_extracted_dates_en + list_extracted_dates_jp
            
    return list_extracted_dates

def extract_a_date(in_sentence: str, checkifvalid=True, format='%Y/%m/%d'):
    """文章の中に日付を示す文字列が1つあれば、それを抽出する。
    抽出した日付はformatに従う形式で文字列として出力する。

    Args:
      in_sentence (str) : 入力テキスト
      checkifvalid (bool) : 値の妥当性を確認するかどうか（True: する）
    Returns:
      format形式で表現した日付
    Notes:
      対象文字列が見つからない場合や、複数見つかる場合はNoneを返す。
    """

    list_extracted_dates_tmp = extract_dates(in_sentence,checkifvalid=checkifvalid)

    # date型への変換と重複削除
    list_extracted_dates = []
    for tmp_date in list_extracted_dates_tmp:
        if re.search('(年|月|日)',tmp_date):
            date_str = convert_wareki_to_yyyymmdd(tmp_date,checkifvalid=checkifvalid,format=format)
        else:
            date_date = convert_str_to_date(tmp_date)
            if date_date:
                date_str = date_date.strftime(format)
            else:
                date_str = None
        if date_str:
            list_extracted_dates.append(date_str)
    list_extracted_dates = list(dict.fromkeys(list_extracted_dates))

    if len(list_extracted_dates) == 1:
        r_val = list_extracted_dates[0]
    else:
        r_val = None

    return r_val


def extract_dates_num(in_sentence: str, checkifvalid=True):
    """文章の中から年月日（/-表記）を抽出する。

    Args:
      in_sentence (str) : 入力テキスト
      checkifvalid (bool) : 値の妥当性を確認するかどうか（True: する）
    Returns:
      抽出した文字列のリスト
    Notes:
      * 対象文字列が見つからなかった場合は、空のリストを出力する。
      * 妥当性評価はconvert_str_to_date関数に任せる。
        この関数はdateutil.parser.parse関数を利用しているが、
        予想外の認識の仕方をすることがあるので注意すること。
    """

    if not in_sentence:
        return []

    # 前処理
    tmp_str = in_sentence.strip()         # トリミング処理
    tmp_str = tmp_str.translate(ZEN2HAN)  # 全角->半角処理
    # tmp_str = tmp_str.upper()             # 小文字->大文字処理

    # 抽出処理
    fo_pre = REGEX_DATE_PRE.findall(tmp_str)
    list_extracted_pre = [mo_pre[0] for mo_pre in fo_pre]
    list_extracted_tmp = []
    for str_pre in list_extracted_pre:
        mo = REGEX_DATE.search(str_pre)
        if mo:
            list_extracted_tmp.append(mo.group())

    # 妥当性評価
    if checkifvalid:
        list_extracted = []
        for v in list_extracted_tmp:
            if convert_str_to_date(v):
                list_extracted.append(v)
    else:
        list_extracted = list_extracted_tmp

    # 結果出力
    return list_extracted

def extract_dates_en(in_sentence: str, checkifvalid=True):
    """文章の中から年月日（英語表記）を抽出する。

    Args:
      in_sentence (str) : 入力テキスト
      checkifvalid (bool) : 値の妥当性を確認するかどうか（True: する）
    Returns:
      抽出した文字列のリスト
    Notes:
      * 対象文字列が見つからなかった場合は、空のリストを出力する。
      * 妥当性評価はconvert_str_to_date関数に任せる。
        この関数はdateutil.parser.parse関数を利用しているが、
        「123th October」を「123年10月」、
        「32th October」を「2032年10月」と認識するなど、
        認識の仕方にクセがあるので注意すること。
    """

    if not in_sentence:
        return []

    # 前処理
    tmp_str = in_sentence.strip()         # トリミング処理
    tmp_str = tmp_str.translate(ZEN2HAN)  # 全角->半角処理
    tmp_str = tmp_str.upper()             # 小文字->大文字処理

    # 抽出処理
    fo_pre = REGEX_DATE_EN_PRE.findall(tmp_str)
    list_extracted_pre = [mo_pre[0] for mo_pre in fo_pre]
    list_extracted_tmp = []
    for str_pre in list_extracted_pre:
        mo = REGEX_DATE_EN.search(str_pre)
        if mo:
            list_extracted_tmp.append(mo.group())

    # 妥当性評価
    if checkifvalid:
        list_extracted = []
        for v in list_extracted_tmp:
            if convert_str_to_date(v):
                list_extracted.append(v)
    else:
        list_extracted = list_extracted_tmp

    # 結果出力
    return list_extracted

def extract_dates_jp(in_sentence: str, checkifvalid=True):
    """文章の中から年月日（日本語表記）を抽出する。

    Args:
      in_sentence (str) : 入力テキスト
      checkifvalid (bool) : 値の妥当性を確認するかどうか（True: する）
    Returns:
      抽出した文字列のリスト
    Notes:
      対象文字列が見つからなかった場合は、空のリストを出力する。
      出力文字列はスペースを全て取り除く。
    """

    if not in_sentence:
        return []

    # 前処理
    tmp_str = in_sentence.strip()         # トリミング処理
    tmp_str = tmp_str.translate(ZEN2HAN)  # 全角->半角処理
    tmp_str = tmp_str.upper()             # 小文字->大文字処理

    # 抽出処理
    fo = REGEX_DATE_JP.findall(tmp_str)
    list_extracted_tmp = [mo[0].replace(' ','') for mo in fo]  #スペースは全て取り除く。

    # 妥当性評価
    if checkifvalid:
        list_extracted = []
        for v in list_extracted_tmp:
            if convert_wareki_to_yyyymmdd(v, checkifvalid=True):
                list_extracted.append(v)
    else:
        list_extracted = list_extracted_tmp

    # 結果出力
    return list_extracted

def convert_wareki_to_yyyymmdd(in_str: str, checkifvalid=True, format='%Y/%m/%d'):
    """和暦表記をyyyymmdd表記に変換する。
    
    Args:
      in_str (str) : 入力文字列
      checkifvalid (bool) : Trueの場合、有効な日付かどうか確認する。
      format (str) : 出力文字列のフォーマット。checkifvalid=True時のみ有効。
    Returns:
      変換された文字列 or None
    Notes:
      変換された文字列が無効な日付である場合は、Noneを返す。
      日付が有効かどうかはconvert_str_to_date関数によって判定する。
      年の取得ができなかった場合、日本時刻での年を取得する。
    """
    
    if not in_str:
        return None
    
    year_str = search_year_jp(in_str)    # 年の取得
    if year_str is None:
        year_str = str(datetime.now(timezone(timedelta(hours=9))).date().year)  # 日本時刻から年を取得する。 
    month_str = search_month_jp(in_str)  # 月の取得
    day_str = search_day_jp(in_str)      # 日の取得
    if day_str is None:
        day_str = '1'
    
    r_val = '/'.join([year_str,month_str,day_str])
    if  checkifvalid:
        r_val_date = convert_str_to_date(r_val,yearfirst=True)
        if r_val_date is None:
            r_val = None
        else:
            r_val = r_val_date.strftime(format)
    
    return r_val

def search_year_jp(in_str: str):
    """日本語表記で書かれた年月日から、年の数値を文字列で取得する。
    年号表記の場合は西暦の数値に変換する。
    """

    if not in_str:
        return None

    mo_year = REGEX_YEAR_JP.search(in_str)
    if not mo_year:
        return None

    len_mo_year = len(mo_year.groups())
    year_str = mo_year.group(len_mo_year)
    
    nengo_str = mo_year.group(1)
    offset_num = WAREKI2SEIREKI.get(nengo_str,0)
    year_str = str(int(year_str)+offset_num)
    
    return year_str

def search_month_jp(in_str: str):
    """日本語表記で書かれた年月日から、月の数値を文字列で取得する。"""
    
    if not in_str:
        return None
    
    mo_month = REGEX_MONTH_JP.search(in_str)
    if not mo_month:
        return None
    
    len_mo_month = len(mo_month.groups())
    month_str = mo_month.group(len_mo_month)

    return month_str

def search_day_jp(in_str: str):
    """日本語表記で書かれた年月日から、日の数値を文字列で取得する。"""

    if not in_str:
        return None
    
    mo_day = REGEX_DAY_JP.search(in_str)
    if not mo_day:
        return None
    
    len_mo_day = len(mo_day.groups())
    day_str = mo_day.group(len_mo_day)
    
    return day_str

def convert_str_to_date(in_str: str, fuzzy=False, yearfirst=None):
    """
    入力された文字列をdate型に変換する。
    変換はdateutil.parser.parse()関数を利用する。

    Args:
      in_str (str) : 文字列
      fuzzy (bool) : あいまい入力を認めるかどうか。 
      yearfirst (bool) : Trueの場合、必ずはじめの数値をYearと解釈する。
    Returns:
      date型変数 or None
    Notes:
      dateutil.parser.parseのリファレンス
      https://dateutil.readthedocs.io/en/stable/parser.html
    """
    
    if not in_str:
        return None
    
    try:
        r_val = parse(in_str, fuzzy=fuzzy, yearfirst=yearfirst).date()
        return r_val
    except ValueError:
        return None
    except Exception:
        return None


if __name__ == '__main__':
    in_str = input('Enter an integer: ')
    print(extract_numbers(in_str))
    # print(extract_dates_jp(in_str))
    # print(extract_a_date(in_str))
    # print(extract_dates(in_str))