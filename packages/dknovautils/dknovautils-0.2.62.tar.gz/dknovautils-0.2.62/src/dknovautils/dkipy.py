from __future__ import annotations


# 导入module 而不是导入函数或者类 可以避免循环import的问题
from dknovautils import commons
from dknovautils.commons import *


class DkIpyUtils(object):
    @staticmethod
    def hello(a: Any) -> Any:
        commons.iprint_info("hello")
        return a  # 为了测试该文件是否正常

    @staticmethod
    def mfc(cmd: str, verbose: bool = True) -> None:
        DkIpyUtils.mfr(cmd, verbose)

    _cmd_id = 1000

    @staticmethod
    def mfr(cmd: str, getoutput: Callable, verbose: bool = True) -> Any:
        """
        为了去掉对ipython的依赖 需要调用方传入函数 getoutput

            from IPython.core.getipython import get_ipython
            getoutput = get_ipython().getoutput
            cmd='ls'
            r= DkIpyUtils.mfr(cmd,getoutput)

        """
        assert cmd and getoutput, "err24618"
        # 这样局部import 只有执行这个函数的时候 才依赖ipython
        # from IPython.core.getipython import get_ipython  # type ignore[import-untyped]

        assert isinstance(cmd, str) and len(cmd) > 0, "err3581"
        DkIpyUtils._cmd_id += 1
        if verbose:
            commons.iprint_info(f"run cmd begin {DkIpyUtils._cmd_id}: {cmd}")

        # r = get_ipython().getoutput(cmd)  # type:ignore
        r = getoutput(cmd)  # type:ignore

        if verbose:
            commons.iprint_info(f"run cmd end {DkIpyUtils._cmd_id}")

        return r


def dk_mfc(cmd: str, verbose: bool = True) -> None:
    DkIpyUtils.mfc(cmd, verbose)


def dk_mfr(cmd: str, verbose: bool = True) -> Any:
    return DkIpyUtils.mfr(cmd, verbose)


"""

!{cmd}

r=get_ipython().getoutput('{cmd}')



不能用 %cd 格式化会出错 用 os.chdir()

不用 echo 用 iprint






"""
