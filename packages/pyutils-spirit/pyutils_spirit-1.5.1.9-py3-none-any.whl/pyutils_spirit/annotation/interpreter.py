# @Coding: UTF-8
# @Time: 2024/9/11 21:54
# @Author: xieyang_ls
# @Filename: interpreter.py

from threading import Lock

from pymysql import Connect

from logging import info, basicConfig, INFO

from pyutils_spirit.exception.exception import NoneSignatureError

basicConfig(level=INFO)


class Annotation:
    __connection = None

    __cursor = None

    __assemble: dict[str, object] = None

    __lock: Lock = None

    @classmethod
    def connection(cls, host: str, port: int, username: str, password: str, database: str) -> callable:
        def decorator_func(func) -> callable:
            def wrapper(*args, **kwargs):
                if cls.__connection is None or cls.__cursor is None:
                    cls.__connection = Connect(host=host, port=port, user=username, password=password)
                    cls.__connection.select_db(database)
                    cls.__cursor = cls.__connection.cursor()
                    info(f"Connected to database {database} is successfully")
                    func(*args, **kwargs)

            wrapper.__decorator__ = "connection"
            wrapper.__decorator_params = {"host": host, "port": port,
                                          "username": username,
                                          "password": password,
                                          "database": database}
            return wrapper

        return decorator_func

    @classmethod
    def singleton(cls, signature: str) -> callable:
        if cls.__lock is None:
            cls.__lock = Lock()
        cls.__lock.acquire()

        try:
            if not isinstance(signature, str):
                raise NoneSignatureError

            if cls.__assemble is None:
                cls.__assemble = dict()

            def get_signature(other_cls) -> callable:

                def get_instance(*args, **kwargs) -> object:
                    instance = cls.__assemble.get(signature)
                    if instance is None:
                        # 创建新实例并存储
                        instance = other_cls(*args, **kwargs)
                        cls.__assemble[signature] = instance
                    return instance

                get_instance.__decorator__ = "singleton"
                get_instance.__decorator_params__ = signature
                return get_instance

            return get_signature

        finally:
            cls.__lock.release()

    @classmethod
    def get_instance_signature(cls, signature: str) -> object:
        return cls.__assemble.get(signature)


connection = Annotation.connection
singleton = Annotation.singleton
get_instance_signature = Annotation.get_instance_signature
