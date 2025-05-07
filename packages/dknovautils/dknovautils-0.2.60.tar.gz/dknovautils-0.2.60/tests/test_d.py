from __future__ import annotations

"""

测试注释1

"""

# 单行注释1

from dknovautils import *

# from dknovautils.commons import *
# from dknovautils.dkfiles import DkPyFiles
# from dknovautils.dkat import AT

# from dknovautils.dkipy import DkIpyUtils

# from commons import *
# from dkfiles import DkPyFiles
# from dkat import AT

print("test01 start")

"""

测试注释2

"""

"""

测试注释3

"""


def test_d_001():
    """

    测试注释4

    What is a Circular Import?

    """

    assert 1 == 1, "err5162"

    assert str(None) == "None", str(None)

    assert AT.VERSION >= "0.0.39", f"err5484 {AT.VERSION}"

    AT.bindport_httpserver(port=10134, daemon=True)

    AT.log_basicConfig()

    AT.mybeep()

    AT.logger.info("hello dkn logger")

    time.sleep(1.0)

    iprint(f"now:{AT.fepochSecs()}")

    print(AT.sdf_isocompact_format_datetime())

    iprint_warn("hello22")
    iprint_info("hello22")
    iprint_error("hello22")

    assert AT._AstWarnCnt_ == 1 and AT._AstErrorCnt_ == 1

    print("=" * 5)

    iprint(AT.VERSION)

    cstr = AT.sdf_logger_format_datetime()
    print(cstr)

    def f_abc(a):
        return a

    # TypeError: cannot set 'f_abc' attribute of immutable type 'str'
    # str.f_abc = f_abc
    # assert "abc".f_abc(123)==123,'err9592'

    # 可以直接修改函数
    DkPyFiles.f_remove_comments_v1 = lambda x: x

    assert DkPyFiles.f_remove_comments_v1(123) == 123, "err2556"

    # now=datetime.now()
    # datetime.faa = 1

    # DkIpyUtils.magic_fc(123)

    assert DkIpyUtils.hello(1) == 1

    run_simple_a("ls")

    if False:

        r = AT.md5_hex(b"abc")
        iprint(f"r: {r}")

        ra = AT.bindport_httpserver(port=8070)
        assert ra

        r = AT.bindport_httpserver(port=8070)
        assert not r

        ra.shutdown()

        x = 0

        def fxx():
            nonlocal x
            x += 1

        r = AT.bindport_httpserver_cb(port=8070, cb=fxx)
        r2 = AT.bindport_httpserver_cb(port=8070, cb=fxx)
        assert r and not r2 and x == 1
        r.shutdown()

        rc, out, err = run_simple_b(r"cmd.exe /c dir e:\etc ", encoding="gbk")
        iprint(out)

    if False:
        run_simple_a("rm /mnt/d/tmp/tmp/etc/* -rf")
        # 如此写法倒是可以勉强运行 但是中文都乱码了
        # robocopy的/unicode输出编码似乎有问题 搭配 'utf-16-le'还是不能正常运行的
        rc, out, err = run_simple_b(
            "robocopy.exe e:/etc d:/tmp/tmp/etc /MIR ",
            encoding="GBK",
            errors="replace",
        )
        iprint(out)

    if False:
        run_simple_a("rm /mnt/d/tmp/tmp/etc2/* -rf")
        # 如此写法似乎是最好的 中文的文件名称编码倒是正常的 只是有少部分中文乱码
        # robocopy的/unicode输出编码似乎也有问题 搭配 'utf-16-le'还是不能正常运行的
        rc, out, err = run_simple_b(
            "robocopy.exe e:/etc2 d:/tmp/tmp/etc2 /MIR ",
            encoding="GBK",
            errors="replace",
        )
        iprint(out)

    if False:
        DkNetwork.net_check_shutdown("http://192.168.0.2")

    if True:
        r = dknetwork.is_port_open("192.168.0.1", port=80)
        assert r
        r = dknetwork.is_port_open("192.168.0.1", port=2222)
        assert not r

    if True:
        dknetwork.http_scan_urls(urls=["http://192.168.0.1"])

    if True:
        dknetwork.f_test_http_get_url_simple_str()

    if False:
        HomeLanUtils.hlan_checkurl_shutdown_bj(ST=60 * 0.5)
        pass


if __name__ == "__main__":
    test_d_001()
    # hlan_checkurl_shutdown_bj()

    print(AT.VERSION)


"""

https://packaging.python.org/en/latest/tutorials/packaging-projects/


"""
