# @Coding: UTF-8
# @Time: 2024/9/18 21:15
# @Author: xieyang_ls
# @Filename: set.py

from typing import TypeVar, Generic

from abc import ABC, abstractmethod

E = TypeVar('E')


class Set(ABC, Generic[E]):

    @abstractmethod
    def add(self, element: E) -> None:
        pass

    @abstractmethod
    def discard(self, element: E) -> E:
        pass

    @abstractmethod
    def clean(self) -> None:
        pass

    @abstractmethod
    def __contains__(self, element: E) -> bool:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass


class HashSet(Set[E]):
    __LOAD_FACTOR = 0.75

    __initial_capacity: int = None

    __current_capacity: int = None

    __nodes = None

    __expansion_nodes = None

    def __init__(self, initial_capacity: int = 15) -> None:
        if initial_capacity is None or initial_capacity <= 0:
            self.__initial_capacity = 15
        else:
            self.__initial_capacity = initial_capacity
        self.__current_capacity = 0
        self.__nodes: list[HashSet.Node[E] | None] = [None] * self.__initial_capacity
        self.__expansion_nodes: None = None

    def __handler(self, flag):
        if flag == 'a':
            self.__current_capacity += 1
        else:
            self.__current_capacity -= 1

    def __setattr__(self, key, value):
        if hasattr(self, key):
            super().__setattr__(key, value)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __getCode(self, element: E) -> int:
        try:
            code = hash(element)
        except TypeError:
            code = id(element)
        return abs(code) % self.__initial_capacity

    def __expansion(self):
        self.__initial_capacity *= 2
        self.__expansion_nodes: list[HashSet.Node[E] | None] = [None] * self.__initial_capacity
        for node in self.__nodes:
            while node is not None:
                idCode: int = self.__getCode(node.element)
                if self.__expansion_nodes[idCode] is None:
                    self.__expansion_nodes[idCode] = node
                else:
                    self.__expansion_nodes[idCode].putNodeToLast(node)
                node = node.getNextDifferenceIdNode(idCode, self.__getCode)
        self.__nodes = self.__expansion_nodes
        self.__expansion_nodes = None

    def add(self, element: E) -> None:
        if self.__current_capacity / self.__initial_capacity >= HashSet.__LOAD_FACTOR:
            self.__expansion()
        idCode: int = self.__getCode(element)
        if self.__nodes[idCode] is None:
            self.__nodes[idCode] = HashSet.Node(element=element)
            self.__current_capacity += 1
        elif self.__nodes[idCode].element == element or self.__nodes[idCode].element is element:
            self.__nodes[idCode].element = element
        else:
            self.__nodes[idCode].putNextNode(element, self.__handler)

    def discard(self, element: E) -> E:
        idCode: int = self.__getCode(element)
        if self.__nodes[idCode] is None:
            return None
        elif self.__nodes[idCode].element == element or self.__nodes[idCode].element is element:
            value = self.__nodes[idCode].element
            self.__nodes[idCode] = self.__nodes[idCode].nextNode
            self.__current_capacity -= 1
            return value
        else:
            return self.__nodes[idCode].removeNextNode(element, self.__handler)

    def clean(self) -> None:
        self.__current_capacity = 0
        self.__initial_capacity = 15
        self.__nodes = [None] * self.__initial_capacity

    def __contains__(self, element: E) -> bool:
        idCode: int = self.__getCode(element)
        if self.__nodes[idCode] is None:
            return False
        elif self.__nodes[idCode].element == element or self.__nodes[idCode].element is element:
            return True
        else:
            return self.__nodes[idCode].compareNextNode(element=element)

    def __len__(self):
        return self.__current_capacity

    class Node(Generic[E]):

        element: E = None

        def __init__(self, element: E) -> None:
            self.element = element
            self.nextNode: [HashSet.Node[E] | None] = None

        def putNextNode(self, element: E, handler: callable(str)) -> None:
            if self.nextNode is None:
                self.nextNode = HashSet.Node(element=element)
                handler('a')
            elif self.nextNode.element == element or self.nextNode.element is element:
                self.nextNode.element = element
            else:
                return self.nextNode.putNextNode(element, handler)

        def removeNextNode(self, element: E, handler: callable(str)) -> E:
            if self.nextNode is None:
                return None
            elif self.nextNode.element == element or self.nextNode.element is element:
                element = self.nextNode.element
                self.nextNode = self.nextNode.nextNode
                handler('r')
                return element
            else:
                return self.nextNode.removeNextNode(element, handler)

        def compareNextNode(self, element: E) -> bool:
            if self.nextNode is None:
                return False
            elif self.nextNode.element == element or self.nextNode.element is element:
                return True
            else:
                return self.nextNode.compareNextNode(element=element)

        def putNodeToLast(self, node: Generic[E]) -> None:
            if self.nextNode is None:
                self.nextNode = node
            else:
                self.nextNode.putNodeToLast(node)

        def getNextDifferenceIdNode(self, idCode: int, getIdCode: callable(E)) -> Generic[E]:
            if self.nextNode is None:
                return None
            differenceIdCode = getIdCode(self.nextNode.element)
            if differenceIdCode == idCode:
                return self.nextNode.getNextDifferenceIdNode(idCode, getIdCode)
            else:
                eNode: HashSet.Node[E] = self.nextNode
                self.nextNode = None
                return eNode
