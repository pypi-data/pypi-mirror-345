# @Coding: UTF-8
# @Time: 2024/9/11 0:15
# @Author: xieyang_ls
# @Filename: mysql_handler.py
from abc import ABC, abstractmethod

from logging import info, error, INFO, basicConfig

from pyutils_spirit.util.json_util import deep_loads

from pymysql import Connect, OperationalError, cursors

from pyutils_spirit.annotation.interpreter import singleton

from pyutils_spirit.exception.exception import ArgumentException

basicConfig(level=INFO)


class Handler(ABC):

    @abstractmethod
    def select(self, sql: str) -> tuple:
        pass

    @abstractmethod
    def insert(self, sql: str) -> bool:
        pass

    @abstractmethod
    def update(self, sql: str) -> bool:
        pass

    @abstractmethod
    def delete(self, sql: str) -> bool:
        pass

    @abstractmethod
    def manage_execute(self, sql: str) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_connection(self) -> [Connect]:
        pass


@singleton(signature="MysqlHandler")
class MySQLHandler(Handler):
    __cursor = None

    __connection = None

    def __init__(self, host: str, port: int, user: str, password: str, database: str) -> None:
        try:
            connection: Connect = Connect(
                host=host,
                port=port,
                user=user,
                password=password,
                cursorclass=cursors.DictCursor
            )
            connection.select_db(database)
            info(f"Connected to database {database} successfully!!!")
            info(f"MySQL version: {connection.get_server_info()}")
            cursor = connection.cursor()
            self.__connection = connection
            self.__cursor = cursor
        except (ArgumentException, OperationalError) as e:
            error(e)
            error(f"Connected to database {database} failure")
            raise ArgumentException("please check connected the database arguments")

    def select(self, sql: str) -> tuple:
        self.__cursor.execute(sql)
        result: tuple = self.__cursor.fetchall()
        return deep_loads(data=result)

    def insert(self, sql: str) -> bool:
        try:
            self.__cursor.execute(sql)
            self.__connection.commit()
            return True
        except Exception as e:
            self.__connection.rollback()
            raise e

    def update(self, sql: str) -> bool:
        try:
            self.__cursor.execute(sql)
            self.__connection.commit()
            return True
        except Exception as e:
            self.__connection.rollback()
            raise e

    def delete(self, sql: str) -> bool:
        try:
            self.__cursor.execute(sql)
            self.__connection.commit()
            return True
        except Exception as e:
            self.__connection.rollback()
            raise e

    def manage_execute(self, sql: str) -> bool:
        try:
            self.__cursor.execute(sql)
            self.__connection.commit()
            return True
        except Exception as e:
            self.__connection.rollback()
            raise e

    def get_connection(self) -> [Connect]:
        return self.__connection, self.__cursor

    def disconnect(self) -> None:
        self.__connection.close()
