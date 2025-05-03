# @Coding: UTF-8
# @Time: 2025/3/29 23:28
# @Author: xieyang_ls
# @Filename: request_result.py

class Result:

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def SUCCESS(cls, data: object) -> dict:
        return {'code': 20001, 'data': data, 'message': "Request success"}

    @classmethod
    def WARN(cls, message: str) -> dict:
        return {'code': 40001, 'data': None, 'message': message}

    @classmethod
    def ERROR(cls, message: str) -> dict:
        return {'code': 50001, 'data': None, 'message': message}

    @classmethod
    def new(cls, code: int, data: object, message: str) -> dict:
        return {'code': code, 'data': data, 'message': message}
