# @Coding: UTF-8
# @Time: 2024/9/14 21:48
# @Author: xieyang_ls
# @Filename: exception.py

class ArgumentException(Exception):

    def __init__(self, msg):
        super(ArgumentException, self).__init__(msg)


class NoneSignatureError(Exception):
    def __init__(self):
        super().__init__("the signature is None, please check the signature")


class ConflictSignatureError(Exception):
    def __init__(self):
        super().__init__("the signature is conflict, please check the signature")


class InvalidThreadWaitError(Exception):
    def __init__(self):
        super().__init__("the thread wait is invalid, caused by not get lock")

class SpiritContainerServiceException(Exception):
    def __init__(self):
        super().__init__("the spirit container service is start, please do not repeat start")


class BusinessException(Exception):
    def __init__(self, msg):
        super(BusinessException, self).__init__(msg)


class SystemException(Exception):
    def __init__(self, msg):
        super(SystemException, self).__init__(msg)
