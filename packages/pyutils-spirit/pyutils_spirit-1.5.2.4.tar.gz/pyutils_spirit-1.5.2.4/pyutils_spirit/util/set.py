# @Coding: UTF-8
# @Time: 2024/9/18 21:15
# @Author: xieyang_ls
# @Filename: set.py
import time
from abc import ABC, abstractmethod
from threading import Thread

from typing import TypeVar, Generic

E = TypeVar('E')


class Set(ABC, Generic[E]):

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add(self, element: E) -> None:
        pass

    @abstractmethod
    def remove(self, element: E) -> E:
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

    def __init__(self, initial_capacity: int = 8) -> None:
        if not isinstance(initial_capacity, int) or initial_capacity < 1:
            self.__initial_capacity: int = 8
        else:
            self.__initial_capacity: int = initial_capacity
        self.__nodes: list[HashSet._Node[E] | None] = [None] * self.__initial_capacity
        self.__nodes_size: int = 0

    def __get_hash_id_code(self, element: E) -> int:
        hash_id_code: int | None = None
        try:
            hash_id_code = hash(element)
        except TypeError:
            hash_id_code = id(element)
        finally:
            return abs(hash_id_code) % self.__initial_capacity

    def __auto_expansion(self) -> None:
        self.__initial_capacity *= 2
        new_nodes: list[HashSet._Node[E] | None] = [None] * self.__initial_capacity
        for node in self.__nodes:
            while node is not None:
                index: int = self.__get_hash_id_code(node.element)
                if new_nodes[index] is None:
                    new_nodes[index] = node
                else:
                    new_nodes[index].add_element_tail(e_node=node)
                node = node.get_different_hash_id_node(index=index, get_hash_id_code=self.__get_hash_id_code)
        self.__nodes = new_nodes

    def add(self, element: E) -> None:
        if self.__nodes_size / self.__initial_capacity >= HashSet.__LOAD_FACTOR:
            self.__auto_expansion()
        index: int = self.__get_hash_id_code(element=element)
        if self.__nodes[index] is None:
            self.__nodes[index] = HashSet._Node(element=element)
            self.__nodes_size += 1
        elif self.__nodes[index].element is element or self.__nodes[index].element == element:
            return None
        else:
            if self.__nodes[index].add_element(element=element):
                self.__nodes_size += 1

    def remove(self, element: E) -> E:
        index: int = self.__get_hash_id_code(element=element)
        if self.__nodes[index] is None:
            return None
        if self.__nodes[index].element is element or self.__nodes[index].element == element:
            r_element: HashSet._Node = self.__nodes[index].element
            self.__nodes[index] = self.__nodes[index].next
            self.__nodes_size -= 1
            return r_element
        r_element: HashSet._Node = self.__nodes[index].remove_element(element=element)
        if r_element is not None:
            self.__nodes_size -= 1
        return r_element

    def clean(self) -> None:
        self.__initial_capacity = 8
        self.__nodes_size = 0
        self.__nodes = [None] * self.__initial_capacity

    def __contains__(self, element: E) -> bool:
        index: int = self.__get_hash_id_code(element=element)
        if self.__nodes[index] is None:
            return False
        elif self.__nodes[index].element is element or self.__nodes[index].element == element:
            return True
        return self.__nodes[index].contains_element(element=element)

    def __len__(self) -> int:
        return self.__nodes_size

    class _Node(Generic[E]):

        def __init__(self, element: E) -> None:
            self.element: E = element
            self.next: HashSet._Node[E] | None = None

        def add_element(self, element: E) -> bool:
            if self.next is None:
                self.next = HashSet._Node(element=element)
                return True
            elif self.next.element is element or self.next.element == element:
                return False
            return self.next.add_element(element=element)

        def remove_element(self, element: E) -> E:
            if self.next is None:
                return None
            if self.next.element is element or self.next.element == element:
                r_element: HashSet._Node = self.next.element
                self.next = self.next.next
                return r_element
            return self.next.remove_element(element=element)

        def add_element_tail(self, e_node) -> None:
            if self.next is None:
                self.next = e_node
            else:
                return self.next.add_element_tail(e_node=e_node)

        def get_different_hash_id_node(self, index: int, get_hash_id_code: callable):
            if self.next is None:
                return None
            other_index: int = get_hash_id_code(element=self.next.element)
            if other_index == index:
                return self.next.get_different_hash_id_node(index=index, get_hash_id_code=get_hash_id_code)
            e_node: HashSet._Node = self.next
            self.next = None
            return e_node

        def contains_element(self, element: E) -> bool:
            if self.next is None:
                return False
            if self.next.element is element or self.next.element == element:
                return True
            return self.next.contains_element(element=element)
