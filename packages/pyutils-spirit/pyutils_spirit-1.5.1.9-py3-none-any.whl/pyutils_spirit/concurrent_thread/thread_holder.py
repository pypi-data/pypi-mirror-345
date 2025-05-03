# @Coding: UTF-8
# @Time: 2025/3/28 23:50
# @Author: xieyang_ls
# @Filename: thread_holder.py

from typing import TypeVar, Generic

from threading import current_thread, Lock

from pyutils_spirit.util.assemble import Assemble, HashAssemble

K = TypeVar('K')

V = TypeVar('V')


class ThreadHolder(Generic[K, V]):
    __LOCK: Lock = Lock()

    __THREAD_HOLDER = None

    __IS_CONSTRUCTOR: bool = None

    __instances: Assemble[int | K, V] = None

    def __init__(self):
        if ThreadHolder.__IS_CONSTRUCTOR is True:
            self.__instances = HashAssemble()
        else:
            raise NotImplementedError("ThreadHolder initialization must by constructor")

    @classmethod
    def constructor(cls):
        cls.__LOCK.acquire()
        try:
            if cls.__THREAD_HOLDER is None:
                cls.__IS_CONSTRUCTOR = True
                cls.__THREAD_HOLDER = cls()
            return cls.__THREAD_HOLDER
        finally:
            cls.__IS_CONSTRUCTOR = False
            cls.__LOCK.release()

    def set_thread_holder(self, instance: V) -> None:
        current_thread_id: int = current_thread().ident
        self.__instances[current_thread_id] = instance

    def get_thread_holder(self) -> V:
        current_thread_id = current_thread().ident
        return self.__instances[current_thread_id]

    def remove_thread_holder(self) -> V:
        current_thread_id = current_thread().ident
        return self.__instances.remove(key=current_thread_id)

    def set_holder(self, key: K, value: V) -> None:
        self.__instances[key] = value

    def get_holder(self, key: K) -> V:
        return self.__instances[key]

    def remove_holder(self, key: K) -> V:
        return self.__instances.remove(key=key)
