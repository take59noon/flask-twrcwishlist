--------------------------------
-- テーブル作成
--------------------------------
CREATE TABLE artists (
  id TEXT NOT NULL 
, name TEXT NOT NULL UNIQUE
, PRIMARY KEY(id) 
);

CREATE TABLE products (
  id TEXT NOT NULL 
, title TEXT NOT NULL
, artistid TEXT NOT NULL
, category TEXT
, price INTEGER 
, release_date TEXT NOT NULL -- yyyy-mm-dd
, url TEXT
, image_src TEXT 
, PRIMARY KEY(id) 
);

CREATE TABLE users (
  id INTEGER 
, username TEXT NOT NULL UNIQUE
, hash TEXT NOT NULL
, PRIMARY KEY(id)
);

CREATE TABLE artists_not_displayed (
  userid INTEGER NOT NULL 
, artistid TEXT NOT NULL 
, createdon TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')) -- yyyy-mm-dd HH:MM:SS
, PRIMARY KEY(userid, artistid)
);

CREATE TABLE products_not_displayed (
  userid INTEGER NOT NULL 
, productid TEXT NOT NULL 
, createdon TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')) -- yyyy-mm-dd HH:MM:SS
, PRIMARY KEY(userid, productid)
);

CREATE TABLE products_purchased (
  userid INTEGER NOT NULL 
, productid TEXT NOT NULL 
, createdon TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')) -- yyyy-mm-dd HH:MM:SS
, PRIMARY KEY(userid, productid)
);


--------------------------------
-- インデックス作成
--------------------------------
create index artist_name_index on artists (name);


--------------------------------
-- 初期データ投入
--------------------------------
insert into artists (id,name) values ('1936852','Aimer');
insert into artists (id,name) values ('1079137','amazarashi');
insert into artists (id,name) values ('2384275','Anly');
insert into artists (id,name) values ('2886509','asmi');
insert into artists (id,name) values ('2348176','FINLANDS');
insert into artists (id,name) values ('1417724','GLIM SPANKY');
insert into artists (id,name) values ('2708393','Hakubi');
insert into artists (id,name) values ('2323230','Half time Old');
insert into artists (id,name) values ('2405608','Hump Back');
insert into artists (id,name) values ('2579072','kobore');
insert into artists (id,name) values ('2357239','Mrs. GREEN APPLE');
insert into artists (id,name) values ('2786423','Rin音');
insert into artists (id,name) values ('2347970','Saucy Dog');
insert into artists (id,name) values ('2128530','SHE''S');
insert into artists (id,name) values ('2536496','Split end');
insert into artists (id,name) values ('2705320','TETORA');
insert into artists (id,name) values ('2690290','todo');
insert into artists (id,name) values ('2500307','Uru');
insert into artists (id,name) values ('3022240','yama');
insert into artists (id,name) values ('2906838','YOASOBI');
insert into artists (id,name) values ('2429441','yonige');
insert into artists (id,name) values ('2381274','あいみょん');
insert into artists (id,name) values ('2461727','ドラマストア');
insert into artists (id,name) values ('2707098','なきごと');
insert into artists (id,name) values ('2643143','フラスコテーション');
insert into artists (id,name) values ('2538175','ポルカドットスティングレイ');
insert into artists (id,name) values ('2587328','ヨルシカ');
insert into artists (id,name) values ('2693192','リツカ');
insert into artists (id,name) values ('2689676','レベル27');
insert into artists (id,name) values ('282110','宇多田ヒカル');
-- insert into artists (id,name) values ('2570918','花房真優');  -- 「ハナフサマユ」のidに変更
insert into artists (id,name) values ('5209868','花房真優');
insert into artists (id,name) values ('1739330','関取花');
insert into artists (id,name) values ('1895012','黒木渚');
insert into artists (id,name) values ('2528621','坂口有望');
insert into artists (id,name) values ('2705562','崎山蒼志');
insert into artists (id,name) values ('509832','植田真梨恵');
insert into artists (id,name) values ('2150608','新山詩織');
insert into artists (id,name) values ('2596995','足立佳奈');
insert into artists (id,name) values ('2333459','中村千尋');
insert into artists (id,name) values ('2938378','灯橙あか');
insert into artists (id,name) values ('2224382','藤原さくら');
insert into artists (id,name) values ('2011531','日食なつこ');
insert into artists (id,name) values ('2617205','美波');
insert into artists (id,name) values ('2715575','諭吉佳作／men');
insert into artists (id,name) values ('4968592','あたらよ');


--------------------------------
-- 以下のSQLはメンテナンス用
--------------------------------
-- テーブル一覧取得
select * 
from sqlite_master 
where type = 'table'

-- テーブル削除
DROP TABLE artists;
DROP TABLE products;
DROP TABLE users;
DROP TABLE artists_not_displayed;
DROP TABLE products_not_displayed;
DROP TABLE products_purchased;

-- データ確認
select * from artists

select * from products 

select * from users 

select * from products_not_displayed

select * from products_purchased

select * from artists_not_displayed


select p.id, p.title, a.name, p.release_date, p.price 
from products as p
left join artists as a on p.artistid = a.id 

select p.id, p.title, a.name, p.release_date, p.price, p.url 
     , ad.createdon as artist_not_displayed 
     , pd.createdon as product_not_displayed 
     , pp.createdon as product_not_purchased 
from products as p 
inner join artists as a on p.artistid = a.id 
left join artists_not_displayed as ad on ad.userid = 3 and ad.artistid = a.id 
left join products_not_displayed as pd on pd.userid = 3 and pd.productid = p.id 
left join products_purchased as pp on pp.userid = 3 and pp.productid = p.id 
where (artist_not_displayed is NULL) and  
(product_not_displayed is NULL and product_not_purchased is NULL) 
order by a.name collate nocase, p.release_date desc 

select a.id, a.name, ad.createdon 
from artists as a 
left join artists_not_displayed as ad on ad.artistid = a.id and ad.userid = 1 
order by a.name collate nocase 

-- id変更に伴う修正
---- artistsテーブル
select * from artists where id='2570918';

update artists set id='5209868' where id='2570918';

select * from artists where id='5209868';

---- productsテーブル
select * from products where artistid='2570918';

update products set artistid='5209868' where artistid='2570918';

select * from products where artistid='5209868';

--------------------------------
-- memo 
--------------------------------
-- テーブル名を変更する
-- ALTER TABLE テーブル名 RENAME TO 新しいテーブル名;

-- カラムを追加する
-- ALTER TABLE テーブル名 ADD COLUMN カラム名[ データ型];
-- *** 注意事項 ***
--  1. PRIMARY KEY や UNIQUE 制約は設定できない
--  2. DEFAULT 制約を設定する時は、CURRENT_TIME/CURRENT_DATE/CURRENT_TIMESTAMP は指定できない
--  3. NOT NULL 制約を設定する時は、NULL以外のデフォルト値の設定が必要

delete from products where id = '3859509';
delete from products where id = '5303323';
delete from products where id = '5303385';

