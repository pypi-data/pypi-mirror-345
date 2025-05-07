from __future__ import annotations


import http.server
from logging import Logger, LoggerAdapter
import socketserver
from typing import NoReturn, TypeVar
from typing_extensions import override


import dknovautils

from dknovautils.commons import *


DkAppVer = '0.2.58'

_unknown_err = "_unknown_err4035"

T = TypeVar("T")


class staticproperty(property):
    """
    https://stackoverflow.com/questions/1697501/staticmethod-with-property

    """

    def __get__(self, owner_self, owner_cls) -> Any:  # type:ignore
        return self.fget()  # type:ignore


class classproperty(property):
    def __get__(self, owner_self, owner_cls) -> Any:  # type:ignore
        return self.fget(owner_cls)  # type:ignore


"""
这是因为一个bug LoggerAdapter将在3.11版本中泛型化
https://github.com/python/typeshed/issues/7855

"""
MyLoggerAdapter = logging.LoggerAdapter
if TYPE_CHECKING:
    MyLoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    pass
    # MyLoggerAdapter = logging.LoggerAdapter 不知道如此写法是否被mypy允许


class AT(object):
    _inner_logger_fun = None

    _AstWarnCnt_: int = 0
    _AstErrorCnt_: int = 0
    _err_msgs: Deque[str] = deque(maxlen=100)

    _logger_adapter: MyLoggerAdapter | None = None  # type: ignore
    _logger_name = "dkn"

    _is_windows: bool = sys.platform.startswith("win")
    _is_linux: bool = sys.platform.startswith("linux")

    @classproperty
    def isWindows(cls) -> bool:
        return cls.iswindows

    @classproperty
    def iswindows(cls) -> bool:
        # r=sys.platform.startswith('win')
        r = cls._is_windows
        return r

    @classproperty
    def isLinux(cls) -> bool:
        return cls.islinux

    @classproperty
    def islinux(cls) -> bool:
        # r=sys.platform.startswith('win')
        r = cls._is_linux
        return r

    @classmethod
    def _create_my_logger_adapter(cls) -> MyLoggerAdapter:  # type: ignore
        """
        todo 将 info warn error级别的日志 缓存N=20条左右在内存中

        """

        t = logging.getLogger(cls._logger_name)
        r = MyLoggerAdapter_(logger=t)
        return r

    @classmethod
    def get_logger(cls, read_cache: bool = True) -> MyLoggerAdapter_:  # type: ignore
        if cls._logger_adapter is None:
            cls._logger_adapter = cls._create_my_logger_adapter()

        if read_cache:
            return cls._logger_adapter
        else:
            return cls._create_my_logger_adapter()

    @classproperty
    def logger(cls) -> MyLoggerAdapter_:  # type: ignore
        return cls.get_logger()

    @classmethod
    def logger_isEnabledFor(cls, level: int) -> bool:
        return cls.logger.isEnabledFor(level)

    @classmethod
    def log_loggerFun(
        cls,
        # loggerName: str = "dkn",
        initInnerLoggerFun: bool = True,
        beepError: bool = False,
        beepWarn: bool = False,
    ) -> Callable[[object, LLevel], None]:
        """
        创建一个logger 作为系统的缺省logger
        """

        def m_logger_fun(obj: object, llevel: LLevel) -> None:
            assert isinstance(llevel, LLevel)
            _logger = cls.get_logger()

            if False:
                pass
            elif llevel == LLevel.Trace:
                # 也用debug级别。只是在prod模式下可以关闭。
                # 其他的level也可以调用这个函数的
                _logger.log(llevel, obj)
                # _logger.debug(obj)
            elif llevel == LLevel.Debug:
                _logger.debug(obj)
            elif llevel == LLevel.Info:
                _logger.info(obj)
            elif llevel == LLevel.Warn:
                _logger.warning(obj)
                if beepWarn:
                    AT.beep_error_buffered()
            elif llevel == LLevel.Error:
                _logger.error(obj)
                if beepError:
                    AT.beep_error_buffered()
            else:
                assert False, f"bad {llevel}"

        if initInnerLoggerFun:
            cls._logger_adapter = None  # force recreate
            cls.get_logger()
            AT._inner_logger_fun = m_logger_fun

        return m_logger_fun

    # logger fmt =================================

    _LOG_FORMAT_100 = "%(asctime)s - %(levelname)s - %(message)s"

    _LOG_FORMAT_106 = (
        "%(asctime)s.%(msecs)03d %(name)s %(threadName)s [%(levelname)s] %(message)s"
    )

    # date-format ==================================

    _DATE_FORMAT_100 = "%m/%d/%Y %H:%M:%S %p"
    # _DATE_FORMAT_iso_simple = "%m/%d/%Y %H:%M:%S %p"

    STRFMT_ISO_COMPACT_SIMPLE = "%Y%m%dT%H%M%S"
    STRFMT_ISO_COMPACT_ALL_A = "%Y%m%dT%H%M%SS%fZ%Z"
    STRFMT_ISO_ALL_A = "%Y-%m-%dT%H:%M:%S.%f%Z"
    STRFMT_ISO_SEC_A = "%Y-%m-%dT%H:%M:%S"

    STRFMT_LOGGER_MS_A = "%Y-%m-%d %H:%M:%S.%f"

    _default_time_format = "%Y-%m-%d %H:%M:%S"

    """
    
    dtstr = datetime.now().strftime("%Y%m%dT%H%M%S")

        
    """

    @classmethod
    def log_basicConfig(
        cls,
        filename: str | None = None,
        loggerName: str = "dkn",
        level: int = logging.DEBUG,
        initInnerLoggerFun: bool = True,
    ) -> Callable[[object, LLevel], None]:
        """
        这个 dkn logger的设置好像不太好。
        暂时不用这个

        """

        # AT.unsupported()

        logging.basicConfig(
            filename=filename,
            level=level,
            format=cls._LOG_FORMAT_106,
            datefmt=AT.STRFMT_ISO_SEC_A,
            # datefmt=cls._DATE_FORMAT_100,
            force=True,
        )

        logger = logging.getLogger(loggerName)
        logger.setLevel(level)

        mloggerFun = AT.log_loggerFun(initInnerLoggerFun)

        return mloggerFun

    @staticmethod
    def assertAllNotNone(*args: Any) -> None:
        assert isinstance(args, tuple)
        AT.assert_(all(_ is not None for _ in args), "err7540 some value is None")

    @staticmethod
    def deg_to_rad(d: float) -> float:
        return d / 180.0 * math.pi

    __beep_last_time: float = 0

    @staticmethod
    def beep_error_buffered(tone: str = "ping") -> None:
        """
        在0.5秒内最多播放一次 类似防止按钮双击的效果

        """
        t = 0.5
        now = AT.fepochSecs()
        if now < AT.__beep_last_time + t:
            return
        else:
            AT.__beep_last_time = now
            AT.beep(tone)

    @staticmethod
    def beep(tone: str = "ping") -> None:
        if False:
            # import beepy  # type: ignore[import-untyped]
            # beepy.beep(sound=tone)
            pass

    @staticmethod
    def beep2() -> None:
        #!wget -q -T 1 http://localhost:333/hello
        print("\7")

    @classmethod
    def mybeep(
        cls,
        *,
        freq: float = 440,
        dur: float = 500,
        sleep: float | None = None,
        n: int = 1,
        lastDurRate: float = 1.0,
    ) -> None:
        if False:
            # 没用用到。只能播放特定wav文件。不适合动态生成信号。
            # import beepy
            # beepy.beep(sound=tone)
            pass

        if True and cls._is_windows:
            # from beep import beep
            import winsound

            freq = int(freq)
            dur = int(dur)

            for i in range(n):
                # beep(freq, dur)  # duration in ms, frequency in Hz
                r = 1.0 if i != n - 1 else lastDurRate
                dur2 = int(dur * r)
                winsound.Beep(freq, dur2)  # type: ignore
                if sleep is not None:
                    time.sleep(sleep)

        if True and cls._is_linux:
            freq = int(freq)

            for i in range(n):
                # beep -f 2000 -l 1500
                r = 1.0 if i != n - 1 else lastDurRate
                dur2 = int(dur * r)
                os.system(f"beep -f {freq} -l {dur2}")
                if sleep is not None:
                    time.sleep(sleep)

    @staticmethod
    def vassert_(b: bool, s: str | None = None) -> None:
        AT.assert_(b, s)

    @classmethod
    def never(cls, s: str | None = None) -> NoReturn:
        AT.assert_(False, s if s is not None else "should never come here")

    @classmethod
    def fail(cls, s: str | None = None) -> NoReturn:
        AT.assert_(False, s if s is not None else "expected failure err20384")

    @staticmethod
    def checksys() -> None:
        assert sys.version_info >= (3, 11)

    @classmethod
    def fepochMillis(cls) -> int:
        return cls.epoch_millis()

    @classproperty
    def epochmillis(cls) -> int:
        return cls.epoch_millis()

    @classmethod
    def epoch_millis(cls) -> int:
        millisec = int(cls.epoch_secs() * 1000)
        return millisec

    _last_epochsecs = 0.0

    @classproperty
    def epochsecs(cls) -> float:
        return cls.epoch_secs()

    @DeprecationWarning
    @classmethod
    def secs(cls) -> float:
        return cls.epoch_secs()

    @classmethod
    def epoch_secs(cls) -> float:
        """
        time.monotonic() 不是epoch值!! F**K

        """
        r = time.time()
        if r <= cls._last_epochsecs:
            return cls._last_epochsecs
        else:
            cls._last_epochsecs = r
            return r

    @classmethod
    def fepochSecs(cls) -> float:
        return cls.epoch_secs()

    """
        # dd/mm/YY H:M:S
    dts = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dts)

    # 20200101T120000
    dts = datetime.now().strftime("%Y%m%dT%H%M%S")
    print("date and time =", dts)
    
    
    """

    @classmethod
    def sdf_isocompact_format_datetime(
        cls, dt: datetime | None = None, *, precise: str = "s"
    ) -> str:
        """
        20201201T080100

        d: day
        s: second
        ms: millis
        a: all

        """
        assert precise in ["d", "s", "ms", "a"], "err5554 bad precise"

        AT.assert_(dt is None or isinstance(dt, datetime), "err95219")

        # if not isinstance(dt,datetime) and dt is not None:
        #     AT.unsupported()

        if dt is None:
            dt = AT._now_dt()

        dts = dt.strftime(AT.STRFMT_ISO_COMPACT_ALL_A)

        if precise == "a":
            pass
        elif precise == "ms":
            dts = dts[: (8 + 0 + 1 + 6 + 4)]
        elif precise == "s":
            dts = dts[: (8 + 0 + 1 + 6)]
        elif precise == "d":
            dts = dts[:(8)]
        else:
            AT.never()

        return dts

    @staticmethod
    def sdf_logger() -> None:
        AT.unimplemented()
        pass

    @staticmethod
    def _now_dt() -> datetime:
        """
        这个名称为何用下划线开头?

        """
        dt = datetime.now()
        return dt

    @classmethod
    def sdf_logger_format_datetime(
        cls,
        dt: int | datetime | None = None,
        *,
        precise: str = "s",
        noColon: bool = False,
    ) -> str:
        """

        https://strftime.org/
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        https://man7.org/linux/man-pages/man3/strftime.3.html

        -   增加一个参数 noColon，可以将冒号转换为-符号 这样的话 生成的结果可以直接用于文件名称中。

        2023-12-01T08:30:00.123456

        缺省返回
        "yyyy-MM-ddTHH:mm:ss"

        date -I

        d date
        s seconds
        ms millis
        a all

        assert precise in ("d", "s", "ms", "a"), "err5554 bad precise"


        """
        assert precise in ("d", "s", "ms", "a"), "err5554 bad precise"

        if dt is not None and isinstance(dt, int):
            dt = datetime.fromtimestamp(dt / 1000, tz=None)
        elif dt is None:
            dt = datetime.now()
        else:
            pass

        dts = dt.strftime(AT.STRFMT_ISO_ALL_A)

        if precise == "a":
            pass
        elif precise == "ms":
            dts = dts[: (10 + 1 + 8 + 4)]
        elif precise == "s":
            dts = dts[: (10 + 1 + 8)]
        elif precise == "d":
            dts = dts[:(10)]
        else:
            AT.never()

        if noColon:
            dts = dts.replace(":", "-")

        return dts

    @staticmethod
    def assert_(b: Any, s: str | None = None) -> None:
        # 改成完善的形式

        # assert isinstance(b, bool)

        if b:
            return

        # AT._AstErrorCnt_ += 1 后面的 iprint_error已经记录了错误 此处就不记录了
        msg = _unknown_err if s is None else s

        dknovautils.commons.iprint_error(msg)

        raise DkAstException(msg)

    @staticmethod
    def mychdir(s: str) -> None:
        assert isinstance(s, str) and len(s) > 0
        iprint_debug(f"chdir: {s}")
        os.chdir(s)

    @staticmethod
    def astTrace(b: bool, s: str) -> None:
        """在prod中完全不需要的"""
        AT.assert_(b, s)

    @staticmethod
    def unsupported(s: str = "feature") -> None:
        AT.assert_(False, f"err8255 unsupported [{s}]")

    @staticmethod
    def unimplemented(s: str = "feature") -> None:
        AT.assert_(False, f"err4173 unimplemented [{s}]")

    @staticmethod
    def log_conf_matploglib_logger(level: int = logging.INFO) -> None:
        logger = logging.getLogger("matplotlib.font_manager")
        logger.setLevel(level=level)

    @staticmethod
    def dict_group_value(d: Dict[Any, Any]) -> Dict[Any, Any]:
        d2 = {}
        for k, v in d.items():
            if not v in d2:
                d2[v] = [k]
            else:
                d2[v].append(k)
        return d2

    @classmethod
    def md5_hex(cls, bs: bytes) -> str:
        md5 = hashlib.md5()
        md5.update(bs)
        r = md5.hexdigest().lower()
        AT.assert_(len(r) == 32)
        return r

    @classmethod
    def sha256_hex(cls, bs: bytes) -> str:
        md5 = hashlib.sha256()
        md5.update(bs)
        r = md5.hexdigest().lower()
        # AT.assert_(len(r) == 32)
        return r

    @classmethod
    def get_file_md5_hex(cls, file_path: str | Path) -> str:
        """
        计算文件的md5
        :param file_name:
        :return:

        https://www.cnblogs.com/xiaodekaixin/p/11203857.html

        """
        m = hashlib.md5()  # 创建md5对象
        with open(file_path, "rb") as fobj:
            while True:
                data = fobj.read(4096)
                if not data:
                    break
                m.update(data)  # 更新md5对象

        return m.hexdigest().lower()  # 返回md5对象

    @classmethod
    def list_unique(cls, ls: List[T]) -> List[T]:
        d = {ln: None for ln in ls}
        lns = list(d.keys())
        return lns

    @classmethod
    def conf_logging_simple_a(
        cls,
        filename: str = "tmp_my.log",
        level: int = logging.DEBUG,
        log_format: str = "%(asctime)s - %(levelname)s - %(message)s",
        datefmt: str = "%m/%d/%Y %H:%M:%S %p",
    ) -> None:
        """

        有时候只是希望简单的初始化logging 然后使用标准logging函数 如此做是方便在今后去掉对本lib的依赖

        配置为
            可以保存到文件。
                也许是绝对路径 或者文件名。
            同时输出到console
                控制台编码？是否有这个问题？

        """

        cls._logger_adapter = None  # force recreate
        cls.get_logger()

        logging.basicConfig(
            filename=filename,
            level=level,
            format=log_format,
            datefmt=datefmt,
        )

    @classmethod
    def bindport_httpserver(
        cls, *, port: int, daemon: bool = True
    ) -> socketserver.TCPServer | None:
        """
        如果绑定端口成功 将启动一个线程 该线程将持续占用端口和持有TcpServer对象 函数返回 TcpServer
            一般来说 返回 server对象其实没有什么用处。某些情况 可以调用 server.shutdown() 函数关闭server和退出线程。
        否则返回 None

        """
        AT.assert_(port > 0, "err10591 port error")
        PORT = port
        Handler = http.server.SimpleHTTPRequestHandler
        server = None
        startOk = False

        try:

            def tf() -> None:
                nonlocal server
                nonlocal startOk
                try:
                    with socketserver.TCPServer(("", PORT), Handler) as _server:
                        iprint_debug(f"serving at port {port}")
                        server = _server
                        startOk = True
                        server.serve_forever()
                except:
                    startOk = False

            thread = threading.Thread(target=tf, args=(), daemon=daemon)
            thread.start()

            time.sleep(0.5)
            iprint_debug(f"bind tcp port ok. {port} {startOk}")
            return server

        except Exception as e:
            iprint_debug(f"some err occured: {e}")
            return None

    @classmethod
    def bindport_httpserver_cb(
        cls, *, port: int, cb: Callable[[], None]
    ) -> socketserver.TCPServer | None:
        """
        如果绑定端口成功 将启动一个daemon线程 持续占用该端口 然后执行cb回调函数. 返回 TCPServer
        如果绑定端口不成功 将直接 返回 None

        """
        AT.assert_(port > 0 and cb, "err27617")
        server = cls.bindport_httpserver(port=port, daemon=True)
        if server:
            try:
                cb()
            except Exception as e:
                iprint_warn(f"error78836 {e}")
            finally:
                return server
        else:
            return None

    # end
    VERSION = DkAppVer


class MyLoggerAdapter_(MyLoggerAdapter):
    # todo 这个 args kwargs 如何标注类型?
    @override
    def log(
        self, level: int, msg: object, *args, **kwargs  # type:ignore
    ) -> None:  # type:ignore

        if level == LLevel.Warn.value:
            AT._AstWarnCnt_ += 1
        elif level >= LLevel.Error.value:
            AT._AstErrorCnt_ += 1
        else:
            pass

        if self.isEnabledFor(level):
            if callable(msg):
                msg = msg()

            super().log(level, msg, *args, **kwargs)


class DkAstException(Exception):
    pass


"""

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(filename='/mnt/d/tmp/demo0726.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)





"""
