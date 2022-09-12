# 音楽CD欲しいものリスト（Music CD Wishlist）  

####  Video Demo:  https://youtu.be/HgagxEv6rEg

#### Description:  

1. 概要  
<span>　</span>音楽CD欲しいものリスト（Music CD Wishlist）は音楽CDの購入・検討・見送りを管理するためのWebアプリケーションです。音楽CD販売サイトのサービスでは自分の欲しい情報だけを得ることや、CDの購入・検討・見送りの3つのステータスを簡単に管理することができないため、個人で使用する便利ツールとして作成しました。 
<br>
1. アプリの使い方  
<span>　</span>アプリの実際の動作や使用方法については[デモビデオ](https://youtu.be/HgagxEv6rEg)を参照して下さい。
<br>  
1. アプリの仕様    
<span>　</span>Pythonを使用して、Flask + Jinja2アプリとして実装しました。アプリのStyleはBootstrapを採用しています。どちらも、公式サイトのサンプルプログラムを参考にして機能改修しました。また、一部の機能のためにJavaScriptを追加しました。データベースはSQLite3を採用しています。  
<span>　</span>音楽CDデータの入手はCD販売サイト（[タワーレコードオンライン](https://tower.jp/)）からWebスクレイピングを使用して行います。2021年12月29日時点のページ構成を対象としています。Webアプリとは別に、定期的にデータ更新スクリプトを実行することで、最新の音楽CD情報を保ちます。  
<span>　</span>データ取得対象は、あらかじめデータベースに登録してある特定の音楽アーティストです。販売サイト内の全データを収集するわけではありません。  
<br>
1. 仕様詳細  
以下はより技術的な内容を含みます。<br>  
    4.1. プログラムの構成について  
    <span>　</span>以下がこのアプリのファイル構成です。
    ~~~:text
   flask-twrcwishlist/
    ├─ instance/
    ├─ scripts/
    ├─ twrcwishlist/
    ├─ README.md  
    ├─ requirements.txt  
    └─ wsgi.py  
    ~~~
    * instanceフォルダ
    <span>　</span>SQLite3データベースを配置するフォルダです。
    * scriptsフォルダ
    <span>　</span>データ更新スクリプトを保管するフォルダです。このスクリプトはWebアプリとは独立して動作します。詳細については後述します。
    * twrcwishlistフォルダ
    <span>　</span>Webアプリ本体です。詳細については後述します。
    * <span>wsgi.py</span>
    <span>　</span>Webアプリの起動プログラムです。`python .\wsgi.py`で立ち上がります。環境に応じて、wsgi.pyのファイル名をapp.pyやapplication.pyに変更して使用して下さい。

    4.2. データ更新スクリプトの仕様および構成について  
    <span>　</span>以下がデータ更新スクリプトのファイル構成です。
    ~~~:text
   scripts/
    ├─ db_sqlite.py
    ├─ requirements.txt  
    ├─ stringextractor.py
    ├─ update_products.py
    └─ update_products.yaml
    ~~~  
   <span>　</span>update_products.pyがデータ更新スクリプトのメインファイルです。`python .\update_products.py`を実行することにより、instanceフォルダ内のTowerRecordsWishList.dbを更新します。instanceフォルダはscriptsフォルダと同階層に配置する必要があります。また、TowerRecordsWishList.dbはテーブル定義済みのものを用意しておく必要があります。データ更新対象となる音楽アーティストは、データベースに登録されている全ての音楽アーティストです。プログラムを実行すると、update_products.logというログファイルが出力されます。  
   <span>　</span>db_sqlite.pyはデータベース接続を管理するORMモジュールです。
   <span>　</span>stringextractor.pyは文字列から日付を読み取るためのモジュールです。他の開発で作成したものを流用しているため、今回のプロジェクトで使用したい機能よりも多機能です。
   <span>　</span>update_products.yamlはloggingモジュールの設定ファイルです。ログ内容を変更したい場合は、このファイルを修正します。    

    4.3. Webアプリ本体の仕様および構成について  
    <span>　</span>以下がWebアプリ本体のファイル構成です。
    ~~~:text
   twrcwishlist/
    ├─ static/
    ├─ templates/  
    ├─ __init__.py
    ├─ auth.py
    ├─ db.py
    ├─ helpers.py
    └─ wishlist.py
    ~~~  
   <span>　</span>Webアプリの構成は[Flask公式ページ](https://flask.palletsprojects.com/en/2.0.x/tutorial/)のサンプルプログラムを元にしています。staticフォルダにはCSSファイル、JavaScriptファイル、その他画像ファイルを配置します。templatesフォルダにはHTMLファイルを配置します。\_\_init__.pyでは、application factoryを定義します。
   <span>　</span>auth.pyでは、ログインやユーザー管理に関するプログラムを記述しています。
   <span>　</span>db.pyでは、データベースの接続・切断を管理するプログラムを記述しています。
   <span>　</span>helpers.pyでは、アプリ内で汎用的に使用する関数を記述しています。
   <span>　</span>wishlist.pyでは、Webページを定義するプログラムを記述しています。
<br>
1. ライセンスについて  
<span>　</span>このアプリは個人利用を前提としており、一般にサービスを公開する予定はありません。ソースコードは[GitHub](https://github.com/take59noon/flask-twrcwishlist)にて公開しているので、自由にダウンロードし使用してください。（MITライセンス）
