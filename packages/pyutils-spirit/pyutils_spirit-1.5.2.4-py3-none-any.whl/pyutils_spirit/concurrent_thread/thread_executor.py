# @Coding: UTF-8
# @Time: 2024/9/17 16:48
# @Author: xieyang_ls
# @Filename: thread_executor.py

from typing import Any

from threading import Thread

from pyutils_spirit.util.set import Set, HashSet

from pyutils_spirit.concurrent_thread.lock import ReentryLock

from pyutils_spirit.concurrent_thread.queue import Queue, BlockingQueue


class ThreadExecutor:
    __lock: ReentryLock = None

    __executor_count: int = None

    __timeout: int = None

    __task_queue_capacity: int = None

    __task_queue: Queue[callable] = None

    __executors: Set[Thread] = None

    def __init__(self, executor_count: int = 5, timeout: int = 2, task_queue_capacity: int = 10):
        self.__lock = ReentryLock()
        self.__executor_count = executor_count
        self.__timeout = timeout
        self.__task_queue_capacity = task_queue_capacity
        self.__task_queue = BlockingQueue(max_capacity=self.__task_queue_capacity, block_time=self.__timeout)
        self.__executors = HashSet()

    def execute(self, task: callable, *args: Any, **kwargs: Any) -> None:
        self.__lock.try_lock()
        try:
            if len(self.__executors) < self.__executor_count:
                executor = ThreadExecutor.__Executor(task,
                                                     self.__task_queue,
                                                     self.__lock,
                                                     self.__executors,
                                                     *args,
                                                     **kwargs)
                self.__executors.add(executor)
                executor.start()
                return None
        finally:
            self.__lock.release()
        self.__task_queue.addTail(lambda: task(*args, **kwargs))

    class __Executor(Thread):
        __task: callable = None

        __task_queue: Queue[callable] = None

        __lock: ReentryLock = None

        __executors: Set[Thread] = None

        __args: Any = None

        __kwargs: Any = None

        def __init__(self,
                     task: callable,
                     task_queue: Queue[callable],
                     lock: ReentryLock,
                     executors: Set[Thread],
                     *args: Any,
                     **kwargs: Any) -> None:
            super().__init__()
            self.__task = task
            self.__task_queue = task_queue
            self.__lock = lock
            self.__executors = executors
            self.__args = args
            self.__kwargs = kwargs

        def run(self) -> None:
            while self.__task is not None:
                self.__task(*self.__args, **self.__kwargs)
                self.__task = self.__task_queue.removeHead()
            self.__lock.try_lock()
            try:
                self.__executors.remove(self)
            finally:
                self.__lock.release()
