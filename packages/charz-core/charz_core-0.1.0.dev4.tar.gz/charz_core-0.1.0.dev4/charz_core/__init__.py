"""
Charz Core
==========

Core logic for `charz`

Includes
--------

- Annotations
  - `Self`  (from standard `typing` or from package `typing-extensions`)
- Math (from package `linflex`)
  - `lerp`
  - `sign`
  - `clamp`
  - `Vec2`
  - `Vec2i`
  - `Vec3`
- Framework
  - `Engine`
  - `Clock`
  - `DeltaClock`
  - `Scene`
- Decorators
  - `group`
- Enums
  - `Group`
- Components
  - `Transform`
- Nodes
  - `Camera`
  - `Node`
  - `Node2D`
"""

__all__ = [
    "Engine",
    "Clock",
    "DeltaClock",
    "Camera",
    "Scene",
    "group",
    "Group",
    "Node",
    "Self",
    "Node2D",
    "Transform",
    "lerp",
    "sign",
    "clamp",
    "Vec2",
    "Vec2i",
    "Vec3",
]

# re-exports
import sys as _sys

if _sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from linflex import lerp, sign, clamp, Vec2, Vec2i, Vec3

# exports
from ._engine import Engine
from ._clock import Clock, DeltaClock
from ._camera import Camera
from ._scene import Scene
from ._grouping import Group, group
from ._node import Node
from ._components._transform import Transform
from ._prefabs._node2d import Node2D
