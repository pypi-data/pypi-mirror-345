from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


class NoTranasctionError(Exception): ...


@dataclass
class InMemoryDb[ValueT = Any]:
    _storage: list[ValueT] = field(default_factory=list)
    _snapshots: list[list[ValueT]] = field(init=False)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(list(self._storage))

    def __bool__(self) -> bool:
        return bool(self._storage)

    def __len__(self) -> int:
        return len(self._storage)

    def begin(self) -> None:
        self._snapshots.append(deepcopy(self._storage))

    def commit(self) -> None:
        self._validate_has_snapshots()
        self._snapshots.pop()

    def rollback(self) -> None:
        self._validate_has_snapshots()
        snapshot = self._snapshots.pop()
        self._storage = snapshot

    def select_many(
        self, is_selected: Callable[[ValueT], bool]
    ) -> tuple[ValueT, ...]:
        return tuple(value for value in self._storage if is_selected(value))

    def select_one(
        self, is_selected: Callable[[ValueT], bool]
    ) -> ValueT | None:
        for value in self._storage:
            if is_selected(value):
                return value

        return None

    def remove_selected(self, is_selected: Callable[[ValueT], bool]) -> None:
        for value in tuple(self._storage):
            if is_selected(value):
                self._storage.remove(value)

    def remove_many(self, values: Iterable[ValueT]) -> None:
        for value in values:
            self._storage.remove(value)

    def remove(self, value: ValueT) -> None:
        self._storage.remove(value)

    def insert(self, value: ValueT) -> None:
        self._storage.append(value)

    def extend(self, values: Iterable[ValueT]) -> None:
        self._storage.extend(values)

    def subset[SubsetValueT](
        self, type_: type[SubsetValueT]
    ) -> "InMemoryDbSubset[SubsetValueT]":
        return InMemoryDbSubset(self, type_)

    def _validate_has_snapshots(self) -> None:
        if not self._snapshots:
            raise NoTranasctionError


@dataclass(frozen=True, slots=True, unsafe_hash=False)
class InMemoryDbSubset[ValueT]:
    db: InMemoryDb[Any]
    type_: type[ValueT]

    def __iter__(self) -> Iterator[ValueT]:
        for value in self.db:
            if isinstance(value, self.type_):
                yield value

    def __bool__(self) -> bool:
        return bool(tuple(self))

    def __len__(self) -> int:
        return len(tuple(self))

    def select_many(
        self, is_selected: Callable[[ValueT], bool]
    ) -> tuple[ValueT, ...]:
        return tuple(value for value in self if is_selected(value))

    def select_one(
        self, is_selected: Callable[[ValueT], bool]
    ) -> ValueT | None:
        for value in self:
            if is_selected(value):
                return value

        return None

    def remove_selected(self, is_selected: Callable[[ValueT], bool]) -> None:
        for value in self:
            if is_selected(value):
                self.db.remove(value)
