from __future__ import annotations


# 导入module避免某些循环import的问题
from dknovautils import commons, iprint_debug, iprint_warn, AT  # type:ignore
from dknovautils.commons import *


class DKProcessUtil(object):
    _cmdid = 1000

    _retcode_default: int = -999

    @staticmethod
    def run_simple_a(cmd: str, verbose: bool = False) -> int:
        """执行系统命令并有进程返回码。
        
        这个例子说明 call() 函数具有不可替代的价值。


        """
        cmdid = DKProcessUtil._cmdid
        DKProcessUtil._cmdid += 1

        if verbose:
            iprint_debug(f"run_simple_a {cmdid} begin {cmd[:1024]}")

        retcode: int = DKProcessUtil._retcode_default

        try:
            retcode = subprocess.call(cmd, shell=True)
            if verbose and retcode < 0:
                iprint_debug(f"Child was terminated by signal {retcode}")

            if verbose:
                iprint_debug(f"Child returned {retcode}")
        except OSError as e:
            iprint_warn(f"run_simple_a {cmdid} Execution failed: {e}")
        finally:
            if verbose:
                iprint_debug(f"run_simple_a {cmdid} end ")

        return retcode

    @staticmethod
    def run_simple_b(
        cmd: str,
        *,
        splitLines: bool = False,
        throwOnErrReturnCode: bool = False,
        strip: bool = True,
        verbose: bool = False,
        encoding: Any = None,
        errors: Any = None,
    ) -> Tuple[int, str, str]:
        """ 
        
        Use shell to execute the command, store the stdout and stderr in sp variable
        
        """
        # Tuple[int, str|List,str|List]
        cmdid = DKProcessUtil._cmdid
        DKProcessUtil._cmdid += 1

        AT.assert_(not splitLines, "err51042 no splitlines")

        if verbose:
            iprint_debug(f"run_simple_b {cmdid} start {cmd[:1024]}")

        # Use shell to execute the command, store the stdout and stderr in sp variable
        # 运行中，会缓存结果，直到执行完成才会输出。
        sp = subprocess.Popen(
            cmd,
            shell=True,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=encoding,
            errors=errors,
        )

        # Store the return code in rc variable
        # 这个rc值如何获取？如果打开这一行，将在某些情况下产生死锁问题。
        # 来自文档中的说明: This will deadlock when using stdout=PIPE or stderr=PIPE and the child process generates enough output to a pipe such that it blocks waiting for the OS pipe buffer to accept more data. Use Popen.communicate() when using pipes to avoid that.
        # rc = sp.wait()

        # Separate the output and error by communicating with sp variable.
        # This is similar to Tuple where we store two values to two different variables
        out, err = sp.communicate()
        rc: int | None = sp.returncode
        rc = rc if rc else 0

        if verbose:
            iprint_debug(f"Return Code: {rc}")
            iprint_debug(f"stdout is: {out[:1024]}")
            if rc != 0:
                iprint_debug(f"stderr is: {err}")

        if verbose:
            iprint_debug(f"run_simple_b {cmdid} end ")

        if out is None:
            out = ""
        if err is None:
            err = ""

        if strip:
            out = out.strip()
            err = err.strip()

        if throwOnErrReturnCode and (rc != 0):
            msg = f"cmd {cmdid} run error. err: {rc} {err}"
            raise Exception(msg)

        """
        
        这个函数发现的问题之一 是在wsl中执行robocopy等win命令时 会输出非unicode编码的字符 从而导致out解码出现错误.
        有时候似乎加上encoding也不行. 比如 encoding='utf-16'也是不行的
        这个问题后来似乎解决了？忘记是怎么解决的了？
        
        
        关于encoding errors 参考如下文档
        https://docs.python.org/3/howto/unicode.html
        https://docs.python.org/3/library/io.html#io.TextIOWrapper
        
        
        
        """

        return (rc, out, err)


run_simple_a = DKProcessUtil.run_simple_a
run_simple_b = DKProcessUtil.run_simple_b


"""




"""
