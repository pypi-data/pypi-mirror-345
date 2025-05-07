from __future__ import annotations
from dknovautils import *
from dknovautils.dk_cmdutils import CmdUtils


"""

env | python3 -m dknovautils prefix



"""


def main(args) -> None:

    subcmd = args.subcmd
    if subcmd == "prefix":
        CmdUtils.add_dt_prefix()
    elif subcmd == "dtnc":
        sc_dtnc()
    elif subcmd == "hello":
        iprint(f"hello from {AT.VERSION}")
    elif False:
        pass
    else:
        iprint(f"hello from {AT.VERSION}")


def sc_dtnc():
    # dtnc
    slen = len("2025-01-27T12-07-39")
    sr = AT.sdf_logger_format_datetime(precise="a", noColon=True)[:slen]
    print(sr, flush=True)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("subcmd", help="subcmd= hello add_prefix")

    if False:

        parser.add_argument("-d", "--dir", nargs=None, type=str, help="dir")
        parser.add_argument("-p", "--passwd", nargs=None, type=str, help="passwd")
        parser.add_argument("-s", "--subj", nargs=None, type=str, help="subj")
        parser.add_argument("--server", nargs=None, type=str, help="server")
        parser.add_argument("--sslport", nargs=None, type=int, help="port")

        # 这两个变量只跟 htpasswd文件有关 如果更新密码只需要更新这个文件即可
        parser.add_argument(
            "--auth-name", nargs=None, type=str, default="dknova", help="auth-name"
        )
        parser.add_argument(
            "--auth-pwd", nargs=None, type=str, default="123456", help="auth-pwd"
        )

        # parser.add_argument('-p', '--port', nargs=1, type=int, default=8005, help='port')

    args = parser.parse_args()

    if False:
        if not args.dir:
            args.dir = "/home/dknova/test_https"

        AT.assert_(AT.is_linux, "err93757 程序需要在linux环境中运行")

    main(args)
