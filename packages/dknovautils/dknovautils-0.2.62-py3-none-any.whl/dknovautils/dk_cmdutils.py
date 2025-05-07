from __future__ import annotations


from dknovautils import commons, iprint_debug, iprint_warn, AT  # type:ignore
from dknovautils.commons import *  # type: ignore

from enum import Enum, auto, unique

import sys


class CmdUtils:

    @classmethod
    def add_dt_prefix(cls, prefix: str = "dateIms") -> None:
        """
    给标准输入的每一行前面附加 当前的时间戳的前缀。
    
使用方法

env | python3 -m dknovautils prefix

	py函数 给 stdin 分行 加上前缀 40分钟 更新py库
	
		add_line_prefix
	
		-p dateI
		-p dateIs
		-p dateIns
		-p date
		
		输出分行符号 根据os来决定
        
        
        """
        cls.add_datetime_prefix_per_stdin_line(prefix=prefix)

    @classmethod
    def add_datetime_prefix_per_stdin_line(cls, prefix: str) -> None:
        """
        # _prefixs = ["date", "dateI", "dateIs", "dateIns"]

        std_input = sys.stdin.readline().rstrip('\n')  # Remove trailing newline

        """

        class Pref(Enum):
            date = 10
            dateI = 20
            dateIs = 40
            dateIms = 50
            dateIns = 60

        _prefixs = [str(name) for name, _ in Pref.__members__.items()]

        assert (
            prefix in _prefixs
        ), f"err71055 'prefix' should be one of {_prefixs}. prefix:{prefix} "

        preE = Pref[prefix]

        def fprefix() -> str:  # type: ignore
            noColon = False
            if preE == Pref.date:
                # todo
                return AT.sdf_logger_format_datetime(precise="d", noColon=noColon)
            elif preE == Pref.dateI:
                # date -I
                return AT.sdf_logger_format_datetime(precise="d", noColon=noColon)
            elif preE == Pref.dateIs:
                # date -Is
                return AT.sdf_logger_format_datetime(precise="s", noColon=noColon)
            elif preE == Pref.dateIms:
                # 
                return AT.sdf_logger_format_datetime(precise="ms", noColon=noColon)            
            elif preE == Pref.dateIns:
                # todo
                return AT.sdf_logger_format_datetime(precise="a", noColon=noColon)
            else:
                AT.never("err18903")
                
                    
        import sys

        @dataclass
        class LN:
            last: str | None
            curr: str | None

        SN = 50

        def _f_parts() -> Iterator[LN]:
            last: str | None = None
            while True:
                data = sys.stdin.readline(SN)
                if False:
                    AT.never()
                elif len(data) == 0:
                    # EOF
                    yield LN(last=last, curr=None)
                    break
                else:
                    yield LN(last=last, curr=data)
                    last = data

        BRK = "\n"
        NBK = "\n"
        END = ""
        flush = True

        for ln in _f_parts():
            if False:
                print(f"\nyield: [{ln.last}] [{ln.curr}] \n")

            if ln.curr is None:
                print(NBK, end=END, flush=flush)
                break
            elif ln.last is None:
                prefix = fprefix() #"2012-12-12"
                ostr = prefix + " " + ln.curr.rstrip(BRK)
                print(ostr, end=END, flush=flush)
            elif ln.last.endswith(BRK):
                prefix = fprefix() #"2012-12-12"
                ostr = NBK + prefix + " " + ln.curr.rstrip(BRK)
                print(ostr, end=END, flush=flush)
            elif not ln.last.endswith(BRK):
                ostr = ln.curr.rstrip(BRK)
                print(ostr, end=END, flush=flush)
            else:
                AT.never()
                
                
                

        # BRN = "\n"
        # for line in sys.stdin:
        #     line = line.rstrip(BRN)
        #     line = fprefix() + " " + line
        #     # should flush the buffer
        #     print(line,flush=True)
            
            


# def f_add_prefix():

            


if __name__ == "__main__":

    print("input some str")

    CmdUtils.add_dt_prefix(prefix="dateIns")

    print("end all ok")

    pass
