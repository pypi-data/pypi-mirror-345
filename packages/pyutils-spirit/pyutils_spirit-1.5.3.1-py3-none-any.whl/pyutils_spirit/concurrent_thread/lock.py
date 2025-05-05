# @Coding: UTF-8
# @Time: 2024/9/12 23:44
# @Author: xieyang_ls
# @Filename: lock.py
import time

from abc import ABC, abstractmethod

from threading import Lock, Condition, current_thread

from pyutils_spirit.util.assemble import Assemble, HashAssemble

from pyutils_spirit.exception.exception import InvalidThreadWaitError


class Regional(ABC):

    @abstractmethod
    def block(self, timeout: int = None):
        pass

    @abstractmethod
    def wake(self):
        pass

    @abstractmethod
    def wake_all(self):
        pass


class ReentryLock(object):
    __get_count: int = None

    __current_thread_id: int | None = None

    __lock: Lock = None

    __condition: Condition = None

    __assemble: Assemble = None

    def __init__(self):
        self.__get_count = 0
        self.__current_thread_id = None
        self.__lock = Lock()
        self.__condition = Condition(self.__lock)
        self.__assemble: Assemble[int, int] = HashAssemble()

    def try_lock(self) -> None:
        identity = current_thread().ident
        try:
            while True:
                self.__lock.acquire()
                if self.__current_thread_id is None:
                    self.__current_thread_id = identity
                    self.__get_count = 1
                    return None
                elif self.__current_thread_id == identity:
                    self.__get_count += 1
                    return None
                else:
                    self.__condition.wait()
                    self.__lock.release()
        finally:
            self.__lock.release()

    def release(self) -> None:
        if self.__current_thread_id == current_thread().ident:
            self.__get_count -= 1
            if self.__get_count == 0:
                self.__current_thread_id = None
                self.__lock.acquire()
                self.__condition.notify_all()
                self.__lock.release()

    def getReentryCount(self) -> int:
        return self.__get_count

    def __lock_give_up(self) -> None:
        if self.__current_thread_id == current_thread().ident:
            self.__assemble.put(self.__current_thread_id, self.__get_count)
            self.__lock.acquire()
            self.__current_thread_id = None
            self.__condition.notify_all()
            self.__lock.release()
        else:
            raise InvalidThreadWaitError

    def __try_lock_after_block(self) -> None:
        identity = current_thread().ident
        while True:
            self.__lock.acquire()
            if self.__current_thread_id is None:
                self.__current_thread_id = identity
                self.__get_count = self.__assemble.get(identity)
                self.__lock.release()
                return None
            self.__condition.wait()
            self.__lock.release()

    def initBlockRegional(self) -> Regional:
        return ReentryLock.BlockRegional(self.__lock_give_up, self.__try_lock_after_block)

    class BlockRegional(Regional):

        __lock: Lock = None

        __condition: Condition = None

        __lock_give_up: callable = None

        __try_lock_after_block: callable = None

        def __init__(self, lock_give_up, try_lock_after_block) -> None:
            self.__lock = Lock()
            self.__condition = Condition(self.__lock)
            self.__lock_give_up = lock_give_up
            self.__try_lock_after_block = try_lock_after_block

        def block(self, timeout: int = None) -> bool:
            endTime = time.time() + (timeout if timeout is not None else 0)
            self.__lock.acquire()
            self.__lock_give_up()
            self.__condition.wait(timeout=timeout)
            self.__lock.release()
            flag: bool = time.time() >= endTime
            self.__try_lock_after_block()
            return flag

        def wake(self):
            self.__lock.acquire()
            self.__condition.notify()
            self.__lock.release()

        def wake_all(self):
            self.__lock.acquire()
            self.__condition.notify_all()
            self.__lock.release()
