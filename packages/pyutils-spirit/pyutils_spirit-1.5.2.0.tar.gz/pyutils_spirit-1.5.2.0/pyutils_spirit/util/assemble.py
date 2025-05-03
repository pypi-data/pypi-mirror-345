# @Coding: UTF-8
# @Time: 2024/9/10 13:48
# @Author: xieyang_ls
# @Filename: assemble.py

from abc import ABC, abstractmethod

from typing import TypeVar, Generic, Callable, Iterator

K = TypeVar('K')

V = TypeVar('V')


class Assemble(ABC, Generic[K, V]):

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key: K, value: V):
        pass

    @abstractmethod
    def put(self, key: K, value: V) -> None:
        pass

    @abstractmethod
    def __getitem__(self, key: K) -> V:
        pass

    @abstractmethod
    def get(self, key: K) -> V:
        pass

    @abstractmethod
    def remove(self, key: K) -> V:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def get_keys(self) -> list[K]:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        pass

    @abstractmethod
    def __next__(self) -> K:
        pass

    @abstractmethod
    def clean(self) -> None:
        pass


class HashAssemble(Assemble[K, V]):

    def __init__(self, initial_capacity: int = 16) -> None:
        if not isinstance(initial_capacity, int) or initial_capacity <= 0:
            self.__capacity = 16
        else:
            self.__capacity = initial_capacity
        self.__LOAD_FACTOR: float = 0.75
        self.__nodes_size: int = 0
        self.__nodes: list[HashAssemble._Node | None] = [None] * self.__capacity

    def __get_id_hash(self, key: K) -> int:
        __id_hash_code: int | None = None
        try:
            __id_hash_code = hash(key)
        except TypeError:
            __id_hash_code = id(key)
        finally:
            return abs(__id_hash_code) % self.__capacity

    def __auto_expansion(self):
        self.__capacity *= 2
        __new_nodes: list[HashAssemble._Node | None] = [None] * self.__capacity
        for e_node in self.__nodes:
            while e_node is not None:
                index = self.__get_id_hash(key=e_node.key)
                if __new_nodes[index] is None:
                    __new_nodes[index] = e_node
                else:
                    __new_nodes[index].add_node_tail(node=e_node)
                e_node: HashAssemble._Node = e_node.get_different_index_node(index=index, get_index=self.__get_id_hash)
        self.__nodes = __new_nodes

    def __setitem__(self, key: K, value: V) -> None:
        if self.__nodes_size / self.__capacity >= self.__LOAD_FACTOR:
            self.__auto_expansion()
        index = self.__get_id_hash(key=key)
        if self.__nodes[index] is None:
            self.__nodes[index] = HashAssemble._Node(key=key, value=value)
            self.__nodes_size += 1
        else:
            self.__nodes_size += self.__nodes[index].put_node(key=key, value=value)

    def put(self, key: K, value: V) -> None:
        self.__setitem__(key=key, value=value)

    def __getitem__(self, key: K) -> V:
        index = self.__get_id_hash(key=key)
        if self.__nodes[index] is None:
            return None
        return self.__nodes[index].get_node(key=key)

    def get(self, key: K) -> V:
        return self.__getitem__(key=key)

    def remove(self, key: K) -> V:
        index = self.__get_id_hash(key=key)
        if self.__nodes[index] is None:
            return None
        if self.__nodes[index].key is key or self.__nodes[index].key == key:
            value = self.__nodes[index].value
            self.__nodes[index] = self.__nodes[index].next
            self.__nodes_size -= 1
            return value
        value = self.__nodes[index].remove_node(key=key)
        if value is not None:
            self.__nodes_size -= 1
        return value

    def get_keys(self) -> list[K]:
        keys: list[K] = []
        for node in self.__nodes:
            if node is not None:
                keys = node.get_keys(keys=keys)
        return keys

    def __len__(self) -> int:
        return self.__nodes_size

    def __iter__(self) -> Iterator[K]:
        self.index: int = 0
        self.keys: list[K] = self.get_keys()
        return self

    def __next__(self) -> K:
        if self.index >= len(self.keys):
            self.keys = None
            raise StopIteration
        try:
            return self.keys[self.index]
        finally:
            self.index += 1

    def clean(self) -> None:
        self.__nodes_size = 0
        self.__nodes = []
        self.__capacity = 16

    class _Node(Generic[K, V]):
        def __init__(self, key: K, value: V) -> None:
            self.key = key
            self.value = value
            self.next: HashAssemble._Node | None = None

        def put_node(self, key: K, value: V) -> int:
            if self.key is key or self.key == key:
                self.value = value
                return 0
            if self.next is None:
                self.next = HashAssemble._Node(key=key, value=value)
                return 1
            else:
                return self.next.put_node(key=key, value=value)

        def get_node(self, key: K) -> V:
            if self.key is key or self.key == key:
                return self.value
            if self.next is None:
                return None
            return self.next.get_node(key=key)

        def remove_node(self, key: K) -> V:
            if self.next is None:
                return None
            if self.next.key is key or self.next.key == key:
                value = self.next.value
                self.next = self.next.next
                return value
            return self.next.remove_node(key=key)

        def add_node_tail(self, node: Generic[K, V]) -> None:
            if self.next is None:
                self.next = node
            else:
                return self.next.add_node_tail(node=node)

        def get_different_index_node(self, index: int, get_index: Callable[[K], int]) -> Generic[K, V]:
            if self.next is None:
                return None
            different_index = get_index(self.next.key)
            if different_index == index:
                return self.next.get_different_index_node(index=index, get_index=get_index)
            e_node = self.next
            self.next = None
            return e_node

        def get_keys(self, keys: list[K]) -> list[K]:
            keys.append(self.key)
            if self.next is None:
                return keys
            return self.next.get_keys(keys=keys)
