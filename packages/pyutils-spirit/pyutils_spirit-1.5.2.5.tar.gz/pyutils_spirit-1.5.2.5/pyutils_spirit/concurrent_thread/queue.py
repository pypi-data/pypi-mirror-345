# @Coding: UTF-8
# @Time: 2024/9/16 18:19
# @Author: xieyang_ls
# @Filename: queue.py

from abc import ABC, abstractmethod

from typing import TypeVar, Generic

from pyutils_spirit.concurrent_thread.lock import ReentryLock, Regional

E = TypeVar('E')


class Queue(ABC, Generic[E]):

    @abstractmethod
    def addHead(self, element: E) -> None:
        pass

    @abstractmethod
    def addTail(self, element: E) -> None:
        pass

    @abstractmethod
    def removeHead(self) -> E:
        pass

    @abstractmethod
    def removeTail(self) -> E:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def clean(self) -> None:
        pass


class LinkedQueue(Queue[E]):
    __current_capacity: int | None = None

    def __init__(self):
        self.__head_node: LinkedQueue.Node[E] | None = None
        self.__tail_node: LinkedQueue.Node[E] | None = None
        self.__current_capacity = 0

    def addHead(self, element: E) -> None:
        self.__current_capacity += 1
        if self.__head_node is None:
            self.__head_node = LinkedQueue.Node(element)
            self.__tail_node = self.__head_node
            return None
        eNode = LinkedQueue.Node(element)
        self.__head_node.setPrevious(eNode)
        self.__head_node = eNode

    def addTail(self, element: E) -> None:
        self.__current_capacity += 1
        if self.__tail_node is None:
            self.__tail_node = LinkedQueue.Node(element)
            self.__head_node = self.__tail_node
            return None
        eNode = LinkedQueue.Node(element)
        self.__tail_node.setNext(eNode)
        self.__tail_node = eNode

    def removeHead(self) -> E:
        if self.__head_node is None:
            return None
        self.__current_capacity -= 1
        element = self.__head_node.element
        if self.__current_capacity == 0:
            self.__head_node = None
            self.__tail_node = None
            return element
        self.__head_node = self.__head_node.next
        return element

    def removeTail(self) -> E:
        if self.__current_capacity == 0:
            return None
        self.__current_capacity -= 1
        element = self.__tail_node.element
        if self.__current_capacity == 0:
            self.__head_node = None
            self.__tail_node = None
            return element
        self.__tail_node = self.__tail_node.previous
        return element

    def __len__(self) -> int:
        return self.__current_capacity

    def clean(self) -> None:
        self.__current_capacity = 0
        self.__head_node = None
        self.__tail_node = None

    class Node(Generic[E]):

        element: E = None

        def __init__(self, element: E) -> None:
            self.element = element
            self.previous: LinkedQueue.Node[E] | None = None
            self.next: LinkedQueue.Node[E] | None = None

        def setPrevious(self, previous: Generic[E]):
            self.previous = previous
            self.previous.next = self

        def setNext(self, _next: Generic[E]):
            self.next = _next
            self.next.previous = self


class BlockingQueue(Queue[E]):
    __MAX_CAPACITY: int = None

    __lock: ReentryLock = None

    __block_time: int = None

    __put_block_regional: Regional = None

    __get_block_regional: Regional = None

    __current_capacity: int = None

    def __init__(self, max_capacity: int, block_time: int = 5) -> None:
        self.__MAX_CAPACITY = max_capacity
        self.__lock = ReentryLock()
        self.__block_time = block_time
        self.__put_block_regional = self.__lock.initBlockRegional()
        self.__get_block_regional = self.__lock.initBlockRegional()
        self.__head_node: BlockingQueue.Node[E] | None = None
        self.__tail_node: BlockingQueue.Node[E] | None = None
        self.__current_capacity = 0

    def addHead(self, element: E) -> None:
        self.__lock.try_lock()
        try:
            while self.__current_capacity == self.__MAX_CAPACITY:
                can_not_add = self.__put_block_regional.block(timeout=self.__block_time)
                if can_not_add:
                    return None
            self.__current_capacity += 1
            if self.__head_node is None:
                self.__head_node = BlockingQueue.Node(element)
                self.__tail_node = self.__head_node
            else:
                eNode = BlockingQueue.Node(element)
                self.__head_node.setPrevious(eNode)
                self.__head_node = eNode
        finally:
            self.__lock.release()
            self.__get_block_regional.wake_all()

    def addTail(self, element: E) -> None:
        self.__lock.try_lock()
        try:
            while self.__current_capacity == self.__MAX_CAPACITY:
                can_not_add = self.__put_block_regional.block(timeout=self.__block_time)
                if can_not_add:
                    return None
            self.__current_capacity += 1
            if self.__tail_node is None:
                self.__tail_node = BlockingQueue.Node(element)
                self.__head_node = self.__tail_node
            else:
                eNode = BlockingQueue.Node(element)
                self.__tail_node.setNext(eNode)
                self.__tail_node = eNode
        finally:
            self.__lock.release()
            self.__get_block_regional.wake_all()

    def removeHead(self) -> E:
        self.__lock.try_lock()
        try:
            while self.__current_capacity == 0:
                can_not_get = self.__get_block_regional.block(timeout=self.__block_time)
                if can_not_get:
                    return None
            self.__current_capacity -= 1
            element = self.__head_node.element
            if self.__current_capacity == 0:
                self.__head_node = None
                self.__tail_node = None
            else:
                self.__head_node = self.__head_node.next
            return element
        finally:
            self.__lock.release()
            self.__put_block_regional.wake_all()

    def removeTail(self) -> E:
        self.__lock.try_lock()
        try:
            while self.__current_capacity == 0:
                can_not_get = self.__get_block_regional.block(timeout=self.__block_time)
                if can_not_get:
                    return None
            self.__current_capacity -= 1
            element = self.__tail_node.element
            if self.__current_capacity == 0:
                self.__tail_node = None
                self.__head_node = None
                return element
            self.__tail_node = self.__tail_node.previous
            return element
        finally:
            self.__lock.release()
            self.__put_block_regional.wake_all()

    def __len__(self) -> int:
        self.__lock.try_lock()
        try:
            return self.__current_capacity
        finally:
            self.__lock.release()

    def clean(self) -> None:
        self.__lock.try_lock()
        try:
            self.__current_capacity = 0
            self.__head_node = None
            self.__tail_node = None
        finally:
            self.__lock.release()
            self.__put_block_regional.wake_all()

    class Node(Generic[E]):

        element: E = None

        def __init__(self, element: E) -> None:
            self.element = element
            self.previous: BlockingQueue.Node[E] | None = None
            self.next: BlockingQueue.Node[E] | None = None

        def setPrevious(self, previous: Generic[E]):
            self.previous = previous
            self.previous.next = self

        def setNext(self, _next: Generic[E]):
            self.next = _next
            self.next.previous = self
