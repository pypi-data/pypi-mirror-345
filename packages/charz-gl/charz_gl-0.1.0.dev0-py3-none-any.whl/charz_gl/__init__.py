"""
Charz GL
==========

Graphics library built upon `charz`

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
  - `CoreGroup`
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
    "CoreGroup",
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

# Re-exports
from charz_core import (
    Engine,
    Clock,
    DeltaClock,
    Camera,
    Scene,
    group,
    CoreGroup,
    Node,
    Self,
    Node2D,
    Transform,
    lerp,
    sign,
    clamp,
    Vec2,
    Vec2i,
    Vec3,
)

# Exports
# TODO: Add GL exports
