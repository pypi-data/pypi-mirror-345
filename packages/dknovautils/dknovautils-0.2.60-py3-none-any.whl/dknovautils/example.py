from __future__ import annotations

import itertools
from typing import List

from dknovautils import commons, iprint_debug, iprint_warn, AT  # type:ignore
from dknovautils.commons import *


_case_list = ["用户名", "密码"]
_value_list = ["正确", "不正确", "特殊符号", "超过最大长度"]


def add_one(number: int) -> int:
    return number + 1


def gen_case(item: List[str] = _case_list, value: List[str] = _value_list) -> None:
    """输出笛卡尔用例集合"""
    for i in itertools.product(item, value):
        print("输入".join(i))


def hello() -> str:
    ver = AT.VERSION
    r = f"welcome allok 大家好 version:{ver}"
    print(r)
    return r


if __name__ == "__main__":
    hello()
