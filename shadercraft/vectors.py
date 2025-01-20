from __future__ import annotations
from dataclasses import dataclass

from .asserts import assertType


#dataclass
class Vec2F:
    x: float = 0.0
    y: float = 0.0

    def __init__(self, xx: float, yy: float) -> None:
        assertType(xx, float)
        assertType(yy, float)
        self.x = xx
        self.y = yy


class Vec3F:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __init__(self, xx: float, yy: float, zz: float):
        assertType(xx, float)
        assertType(yy, float)
        assertType(zz, float)
        self.x = xx
        self.y = yy
        self.z = zz

class Vec4F:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0

    def __init__(self, xx: float, yy: float, zz: float, ww: float):
        assertType(xx, float)
        assertType(yy, float)
        assertType(zz, float)
        assertType(ww, float)
        self.x = xx
        self.y = yy
        self.z = zz
        self.w = ww
