# !/usr/bin/python
# -*- coding:utf-8 -*-
"""
████─█──█─████─███─█──█─███─███
█──█─█──█─█──█─█───██─█──█──█──
████─████─█──█─███─█─██──█──███
█────█──█─█──█─█───█──█──█──█──
█────█──█─████─███─█──█─███─███
╔╗╔╗╔╗╔═══╗╔══╗╔╗──╔══╗╔══╗╔══╗╔═══╗╔══╗
║║║║║║║╔══╝╚╗╔╝║║──╚╗╔╝║╔╗║║╔╗║╚═╗─║╚╗╔╝
║║║║║║║╚══╗─║║─║║───║║─║╚╝║║║║║─╔╝╔╝─║║─
║║║║║║║╔══╝─║║─║║───║║─║╔╗║║║║║╔╝╔╝──║║─
║╚╝╚╝║║╚══╗╔╝╚╗║╚═╗╔╝╚╗║║║║║╚╝║║─╚═╗╔╝╚╗
╚═╝╚═╝╚═══╝╚══╝╚══╝╚══╝╚╝╚╝╚══╝╚═══╝╚══╝
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

佛祖保佑       永不宕机     永无BUG

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@project:home
@author:Phoenix,weiliaozi
@file:pywork
@ide:PyCharm
@date:2023/12/3
@time:17:33
@month:十二月
@email:thisluckyboy@126.com
"""
import mysql.connector
import openpyxl
import pandas as pd
from .timingTool import fn_timer
from typing import List, Optional, Union, Any
import pymysql

class Database:
    def __init__(self, host: str, port: int, user: str, password: str, db: str, charset: str = 'utf8'):
        """
        Database class for managing MySQL connections and operations.
        """
        self.connection_state = False
        self.connection = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset

    def _connect(self) -> None:
        """
        Establish a connection to the database if not already connected.
        """
        if not self.connection_state:
            try:
                self.connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    db=self.db,
                    charset=self.charset,
                    cursorclass=pymysql.cursors.DictCursor
                )
                self.connection_state = True
            except Exception as e:
                raise ConnectionError(f"Database connection failed: {e}")

    def _close(self) -> None:
        """
        Close the database connection if open.
        """
        if self.connection_state and self.connection:
            try:
                self.connection.close()
                self.connection_state = False
            except Exception as e:
                raise RuntimeError(f"Error closing the connection: {e}")

    def _execute(
        self, 
        sql: str, 
        params: Optional[Union[List[tuple], tuple]] = None, 
        fetch_all: bool = True, 
        as_df: bool = False, 
        procedure: bool = False
    ) -> Optional[Union[List[dict], pd.DataFrame]]:
        """
        Execute a SQL query or stored procedure.
        """
        self._connect()  # Ensure connection is open
        try:
            with self.connection.cursor() as cursor:
                if procedure:
                    cursor.callproc(sql, params)
                elif params:
                    cursor.executemany(sql, params) if isinstance(params, list) else cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                if fetch_all:
                    results = cursor.fetchall()
                    return pd.DataFrame(results) if as_df else results

                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Error executing query: {e}")
        finally:
            self._close()

    def fetch_all(self, sql: str) -> List[dict]:
        """
        Fetch all results from a query.
        """
        return self._execute(sql, fetch_all=True, as_df=False)

    def fetch_as_df(self, sql: str) -> pd.DataFrame:
        """
        Fetch results as a pandas DataFrame.
        """
        return self._execute(sql, fetch_all=True, as_df=True)

    def execute_write(self, sql: str, params: Optional[Union[List[tuple], tuple]] = None) -> None:
        """
        Execute a write (INSERT, UPDATE, DELETE) operation.
        """
        self._execute(sql, params=params, fetch_all=False)

    def execute_many(self, sql: str, params: List[tuple]) -> None:
        """
        Execute many write operations (batch insert/update/delete).
        """
        self._execute(sql, params=params, fetch_all=False)

    def call_procedure(self, procedure_name: str, params: Optional[tuple] = None) -> None:
        """
        Call a stored procedure.
        """
        self._execute(procedure_name, params=params, fetch_all=False, procedure=True)

    def __call__(
        self, 
        sql: str, 
        params: Optional[Union[List[tuple], tuple]] = None, 
        operation_mode: str = "r", 
        as_df: bool = False
    ) -> Optional[Union[List[dict], pd.DataFrame, None]]:
        """
        A unified method for executing different types of operations.
        
        Modes:
            - 'r': Read query, fetch results.
            - 'w': Write operation.
            - 'm': Write many (batch operations).
            - 'p': Call a stored procedure.
        """
        if operation_mode == "r":
            return self.fetch_as_df(sql) if as_df else self.fetch_all(sql)
        elif operation_mode == "w":
            self.execute_write(sql, params=params)
        elif operation_mode == "m":
            if not isinstance(params, list):
                raise ValueError("For batch operations, 'params' must be a list of tuples.")
            self.execute_many(sql, params=params)
        elif operation_mode == "p":
            self.call_procedure(sql, params=params)
        else:
            raise ValueError(f"Invalid operation mode: {operation_mode}")

# Example Usage:
# db = Database(host='localhost', port=3306, user='root', password='password', db='testdb')
# db('SELECT * FROM users', operation_mode='r')
# db('INSERT INTO users (name, age) VALUES (%s, %s)', params=[('Alice', 30), ('Bob', 25)], operation_mode='m')

class MySQLDatabase:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("Connected to MySQL database")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("MySQL connection closed")

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()

    def fetch_query(self, query, params=None,dictionary=False):
        cursor = self.connection.cursor(dictionary=dictionary)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()