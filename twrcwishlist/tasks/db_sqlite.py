import sqlite3


class sqlite_orm():
    """
    ローカル環境に配置しているSQLiteデータベースに接続するためのクラス。

    Samples:
      # Connect database
      db_obj = sqlite_orm(sqlite_file_path)
      # Execute select query 
      # sample 1
      db_obj.cursor.execute(sql_str)
      datas = db_obj.cursor.fetchall()
      # Execute insert/update query and commit 
      # sample 1
      db_obj.cursor.execute(sql_str)
      db_obj.conn.commit()
      # sample 2
      with db_obj.conn:
          db_obj.cursor.execute(sql_str)
      # Disconnect database (if needed)
      db_obj.disconnect()
    """

    def __init__(self, sqlite_file_path):
        # Initialize
        self.db_path = sqlite_file_path
        self.conn = None
        self.cursor = None
        self.set_cursor()

    def __del__(self):
        self.disconnect()

    def connect(self):
        if self.conn is not None:
            self.disconnect()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # logger.debug('Connect to the database.')
        
    def set_cursor(self):
        if self.conn is None:
            self.connect()
        if self.cursor is None:
            self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            # logger.debug('Disonnect to the database.')
