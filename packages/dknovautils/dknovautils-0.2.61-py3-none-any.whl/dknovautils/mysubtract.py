from __future__ import annotations

if __name__ == "__main__":
    print("mysubtract 10")

from typing import Any
from .myadd import m_add

if __name__ == "__main__":
    print("mysubtract 20")


def m_subtract(a: Any, b: Any) -> Any:
    return a - b


def fadd() -> Any:
    return m_add(1, 1)
