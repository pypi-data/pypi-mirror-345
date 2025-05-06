"""
Custom Annotations for Charz
============================

This file contains private annotations used across this package.

Whenever there is a "?" comment,
it means a type may or may not implement that field or mixin class.
"""

from __future__ import annotations as _annotations


from typing import (
    TypeVar as _TypeVar,
    TypeAlias as _TypeAlias,
    Hashable as _Hashable,
    Protocol as _Protocol,
    runtime_checkable as _runtime_checkable,
    TYPE_CHECKING as _TYPE_CHECKING,
)

from linflex import Vec2 as _Vec2
from typing_extensions import (
    LiteralString as _LiteralString,
    Self as _Self,
)

if _TYPE_CHECKING:
    from ._clock import DeltaClock as _DeltaClock

T = _TypeVar("T")
GroupID: _TypeAlias = _LiteralString | int | _Hashable


@_runtime_checkable
class Engine(_Protocol):
    fps: float
    clock: _DeltaClock
    _is_running: bool

    @property
    def is_running(self) -> bool: ...
    @is_running.setter
    def is_running(self, run_state: bool) -> None: ...


@_runtime_checkable
class Node(_Protocol):
    uid: int

    def __init__(self) -> None: ...
    def with_parent(self, parent: Node | None, /) -> _Self: ...
    def with_process_priority(self, process_priority: int, /) -> _Self: ...
    def update(self, delta: float) -> None: ...
    def queue_free(self) -> None: ...
    def _free(self) -> None: ...


class TransformComponent(_Protocol):
    position: _Vec2
    rotation: float
    top_level: bool

    def with_position(
        self,
        position: _Vec2 | None = None,
        /,
        x: float | None = None,
        y: float | None = None,
    ) -> _Self: ...
    def with_global_position(
        self,
        global_position: _Vec2 | None = None,
        /,
        x: float | None = None,
        y: float | None = None,
    ) -> _Self: ...
    def with_rotation(self, rotation: float, /) -> _Self: ...
    def with_global_rotation(self, global_rotation: float, /) -> _Self: ...
    def with_top_level(self, state: bool = True, /) -> _Self: ...
    @property
    def global_position(self) -> _Vec2: ...
    @global_position.setter
    def global_position(self, position: _Vec2) -> None: ...
    @property
    def global_rotation(self) -> float: ...
    @global_rotation.setter
    def global_rotation(self, rotation: float) -> None: ...


@_runtime_checkable
class TransformNode(
    TransformComponent,
    Node,
    _Protocol,
): ...
